#!/usr/bin/env python3
"""PROPOSED Patch B1 (revision 5) for OWNER-POLICY-001 (needs Patch A applied and committed). Human-run only.

Adds the shared policy library (.claude/hooks/policy_lib.py, a new controlled file), the owner-policy
mode of activate_lease.py (no prompts, policy checks, daily counter, lease fields) and of
seal_implementation.py (lane, extension, deny, size, secret, C# allowlist, ignored-file and .meta GUID
checks), write-time enforcement of the same path, content, and secret rules in govern_write.py, an
owner-policy lease that stops working when the policy is deleted or changed, the relaxed `main` branch
rule with its acknowledgement fields, an R2 cap for policy rigor, `.git/**` as a controlled path, and
tests. Commit, push, agent_commit.py and owner_policy.py are Patch B2 and Patch C.

Dry run by default: every old snippet must occur exactly once, the new file must not exist, and the
patched Python must compile. Nothing is written without --apply, and --apply needs an interactive
terminal. Only the listed targets can be touched. Verify this file's SHA-256 against the delivery
message before running it (see PATCH-B1.md). Revert with `git restore <files>` and delete the new file.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]

ALLOWED_TARGETS = frozenset(
    {
        ".claude/hooks/common.py",
        ".claude/hooks/govern_write.py",
        "scripts/activate_lease.py",
        "scripts/seal_implementation.py",
        "scripts/validate_os.py",
    }
)

EDITS: list[tuple[str, str, str]] = []
NEW_FILES: dict[str, str] = {}


def edit(path: str, old: str, new: str) -> None:
    EDITS.append((path, old, new))


NEW_FILES[".claude/hooks/policy_lib.py"] = r'''"""Owner-policy checks shared by the hooks and the lease scripts. Standard library only."""

from __future__ import annotations

import fnmatch
import json
import re
import subprocess
import unicodedata
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from typing import Any

from common import CONTROLLED_PATHS, RIGOR_LEVELS, _lane_path_problem


BUILTIN_DENY = (
    "editor/**", "**/editor/**", "assets/plugins/**", "packages/**", "projectsettings/**",
    "*.asmdef", "*.asmref", "*.dll", "*.rsp", ".git*", "**/.git*", ".git/**",
)
TEXT_EXTENSIONS = {
    ".cs", ".json", ".txt", ".md", ".shader", ".mat", ".prefab", ".unity", ".asset", ".meta", ".yaml", ".yml", ".xml",
}
MAX_SCAN_BYTES = 2_000_000
MAX_WRITE_CHARS = 200_000
MAX_EDITS = 50
YAML_EXTENSIONS = {".asset", ".prefab", ".unity", ".mat"}
GUID_REF = re.compile(r"guid:\s*([0-9a-fA-F]{32})")
PNG_MAGIC = b"\x89PNG\r\n\x1a\n"
SUBJECT = re.compile(r"[A-Za-z0-9 .,:/()_-]{1,72}")
SUBJECT_FORBIDDEN = re.compile(r"co-authored-by|generated with|claude|anthropic|signed-off-by", re.IGNORECASE)

SECRET_SEGMENTS = (
    ".env*", "*.pem", "*.key", "*.p12", "*.pfx", "*.jks", "*.keystore", "*.ppk", "id_rsa*", "id_ed25519*",
    "*secret*", "credentials*", ".netrc", ".npmrc", ".pypirc", ".git-credentials", "*.tfstate", "*.tfvars",
    "google-services.json",
)
SECRET_CONTENT = (
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY"),
    re.compile(r"\b(?:AKIA|ASIA)[A-Z0-9]{16}\b"),
    re.compile(r"\bgh[pousr]_[A-Za-z0-9]{36,}"),
    re.compile(r"github_pat_[A-Za-z0-9_]{20,}"),
    re.compile(r"xox[abprs]-[A-Za-z0-9-]{10,}"),
    re.compile(r"AIza[0-9A-Za-z_-]{35}"),
    re.compile(r"\bsk-[A-Za-z0-9_-]{20,}"),
    re.compile(r"eyJ[A-Za-z0-9_-]{10,512}\.[A-Za-z0-9_-]{10,512}\.[A-Za-z0-9_-]{10,512}"),
    re.compile(r"://[^/\s:@]{1,256}:[^/\s@]{1,256}@"),
    re.compile(r"(?i)(?:password|secret|api[_-]?key|token)\s*[:=]\s*[\"']?[^\s\"']{8,}"),
)
LONG_RUN = re.compile(r"[A-Za-z0-9+/=]{120,}|(?:[0-9A-Fa-f]{2}){60,}")

USING = re.compile(r"\b(global\s+)?using\s+(static\s+)?(?:([A-Za-z_]\w*)\s*=\s*)?([A-Za-z_][\w.]*)\s*;")
QUALIFIED = re.compile(r"\b(System|Microsoft|Mono|Windows|Newtonsoft|Unity)\s*\.\s*([A-Za-z_]\w*)")
ALLOWED_NAMESPACES = {"System", "System.Collections", "System.Collections.Generic", "System.Linq"}
ALLOWED_SYSTEM_MEMBERS = {
    "Collections", "Linq", "Math", "Random", "Array", "Action", "Func", "Serializable", "String", "Object",
    "Enum", "Exception", "DateTime", "TimeSpan", "Guid", "Nullable", "Single", "Double", "Int32", "Int64",
    "Boolean", "Byte", "Char", "Tuple", "IComparable", "IEquatable", "EventArgs", "EventHandler",
    "ArgumentException", "InvalidOperationException", "NotImplementedException", "IDisposable", "Predicate",
    "Comparison",
}
BANNED_NAMESPACE_PREFIXES = ("UnityEngine.Networking", "UnityEngine.Windows")
CS_BANNED = (
    (re.compile(r"\\[uU]"), "unicode escape"),
    (re.compile(r"\bextern\b"), "extern"),
    (re.compile(r"\bunsafe\b"), "unsafe"),
    (re.compile(r"#\s*if"), "conditional compilation"),
    (re.compile(r"#\s*define"), "preprocessor define"),
    (re.compile(r"Type\s*\.\s*GetType"), "Type.GetType"),
    (re.compile(r"\bActivator\b"), "Activator"),
    (re.compile(r"\bMarshal\b"), "Marshal"),
    (re.compile(r"System\s*\.\s*IO"), "System.IO"),
    (re.compile(r"System\s*\.\s*Net"), "System.Net"),
    (re.compile(r"\bEnvironment\s*\."), "Environment"),
    (re.compile(r"\bProcess\s*\."), "Process"),
    (re.compile(r"Reflection"), "Reflection"),
    (re.compile(r"\bGetMethod"), "GetMethod"),
    (re.compile(r"\bGetField"), "GetField"),
    (re.compile(r"\bGetProperty"), "GetProperty"),
    (re.compile(r"\bMethodInfo\b"), "MethodInfo"),
    (re.compile(r"\bAppDomain\b"), "AppDomain"),
    (re.compile(r"\bAssembly\b"), "Assembly"),
    (re.compile(r"\bdynamic\b"), "dynamic"),
    (re.compile(r"CreateInstance"), "CreateInstance"),
    (re.compile(r"InvokeMember"), "InvokeMember"),
    (re.compile(r"GetTypes"), "GetTypes"),
    (re.compile(r"Base64"), "Base64"),
    (re.compile(r"\.Module\b"), "Module"),
    (re.compile(r"GetConstructor"), "GetConstructor"),
    (re.compile(r"\.GetMember\s*\("), "GetMember"),
    (re.compile(r"\.GetEvent\s*\("), "GetEvent"),
    (re.compile(r"\bMethodBase\b"), "MethodBase"),
    (re.compile(r"\.BaseType\b"), "BaseType"),
    (re.compile(r"\bWWW\b"), "WWW"),
    (re.compile(r"VideoPlayer"), "VideoPlayer"),
    (re.compile(r"ScreenCapture"), "ScreenCapture"),
    (re.compile(r"DestroyImmediate"), "DestroyImmediate"),
    (re.compile(r"UnityEngine\s*\.\s*Diagnostics"), "UnityEngine.Diagnostics"),
    (re.compile(r"Analytics"), "Analytics"),
    (re.compile(r"CodeDom"), "CodeDom"),
    (re.compile(r"Expressions"), "Expressions"),
    (re.compile(r"\bPlayerPrefs\b"), "PlayerPrefs"),
    (re.compile(r"Application\s*\.\s*OpenURL"), "Application.OpenURL"),
    (re.compile(r"UnityEngine\s*\.\s*Networking"), "UnityEngine.Networking"),
    (re.compile(r"UnityEngine\s*\.\s*Windows"), "UnityEngine.Windows"),
    (re.compile(r"UnityEditor"), "UnityEditor"),
    (re.compile(r"InitializeOnLoad"), "InitializeOnLoad"),
    (re.compile(r"DllImport"), "DllImport"),
)
GUID = re.compile(r"^guid:\s*([0-9a-fA-F]{32})\s*$", re.MULTILINE)


def _norm(value: str) -> str:
    return re.sub(r"^(?:\./)+", "", value.replace("\\", "/")).casefold()


def glob_match(path: str, pattern: str) -> bool:
    candidate = _norm(path)
    shape = _norm(pattern)
    return fnmatch.fnmatchcase(candidate, shape) or fnmatch.fnmatchcase(candidate + "/", shape)


def deny_patterns(policy: dict[str, Any]) -> tuple[str, ...]:
    return (*BUILTIN_DENY, *policy["deny_paths"], *CONTROLLED_PATHS)


def is_denied(policy: dict[str, Any], relative: str) -> bool:
    return any(glob_match(relative, pattern) for pattern in deny_patterns(policy))


def lane_for_path(policy: dict[str, Any], relative: str) -> dict[str, Any] | None:
    for lane in policy["lanes"]:
        if any(glob_match(relative, pattern) for pattern in lane["allowed_paths"]):
            return lane
    return None


def _lease_lane(policy: dict[str, Any], lease: dict[str, Any]) -> dict[str, Any] | None:
    return next((item for item in policy["lanes"] if item["name"] == lease.get("lane")), None)


def _literal(entry: str) -> str:
    return entry[:-3] if entry.endswith("/**") else entry


def entry_lane(policy: dict[str, Any], entry: str) -> dict[str, Any] | None:
    """The lane that fully covers one allowed_paths entry, or None."""
    literal = _norm(_literal(entry)).rstrip("/")
    for lane in policy["lanes"]:
        for pattern in lane["allowed_paths"]:
            lane_literal = _norm(_literal(pattern)).rstrip("/")
            if pattern.endswith("/**"):
                if literal == lane_literal or literal.startswith(lane_literal + "/"):
                    return lane
            elif entry == pattern:
                return lane
    return None


def secret_path_problem(relative: str) -> str | None:
    for part in relative.replace("\\", "/").split("/"):
        if any(fnmatch.fnmatchcase(part.casefold(), shape) for shape in SECRET_SEGMENTS):
            return f"secret-looking path segment: {ascii(part)}"
    return None


def secret_content_problems(text: str) -> list[str]:
    return [f"secret-looking content ({pattern.pattern[:24]}...)" for pattern in SECRET_CONTENT if pattern.search(text)]


def _strip_line_comments(text: str) -> str:
    """Drop whole-line // comments. They are the only comments cs_scan allows, so no lexer is needed."""
    return "\n".join(line for line in text.split("\n") if not line.lstrip().startswith("//"))


def cs_scan(text: str) -> list[str]:
    """A speed bump, not a sandbox: allowlisted namespaces and banned tokens for C# lane files.

    Ambiguity is refused rather than lexed: block comments and trailing // comments are not allowed, so
    the only comments are whole-line ones. The raw text and a copy without those lines are both scanned,
    so a comment line cannot split a token."""
    problems: list[str] = []
    text = text.lstrip("\ufeff")
    if len(text) > MAX_SCAN_BYTES:
        return ["text is too large to scan"]
    if any(unicodedata.category(char) in {"Cf", "Cc", "Cs"} and char not in "\t\n\r" for char in text):
        return ["control or invisible formatting character in C# (the compiler ignores them inside names)"]
    if re.search("\r(?!\n)|[  ]", text):
        return ["unusual line terminator in C# (a bare CR, U+2028 or U+2029 ends a line for the compiler but not for this scan)"]
    if "/*" in text:
        return ["block comments are not allowed in owner-policy C# files (they can split tokens)"]
    lines = text.split("\n")
    if any("//" in line and not line.lstrip().startswith("//") for line in lines):
        return ["// is only allowed on a line of its own in owner-policy C# files (no trailing comments)"]
    if any(line.lstrip().startswith("#") for line in lines):
        return ["preprocessor directives are not allowed in owner-policy C# files (the compiler treats them as whitespace between tokens)"]
    for candidate in (text, _strip_line_comments(text)):
        for match in USING.finditer(candidate):
            global_use, static_use, alias, namespace = match.groups()
            if global_use or static_use or alias:
                problems.append(f"using form not allowed: {ascii(match.group(0).strip())}")
            elif namespace in ALLOWED_NAMESPACES:
                continue
            elif (namespace == "UnityEngine" or namespace.startswith("UnityEngine.")) and not namespace.startswith(
                BANNED_NAMESPACE_PREFIXES
            ):
                continue
            else:
                problems.append(f"namespace not allowed: {ascii(namespace)}")
        for root_name, member in QUALIFIED.findall(candidate):
            if root_name != "System" or member not in ALLOWED_SYSTEM_MEMBERS:
                problems.append(f"qualified name not allowed: {ascii(root_name + '.' + member)}")
        for pattern, label in CS_BANNED:
            if pattern.search(candidate):
                problems.append(f"banned token: {label}")
    return list(dict.fromkeys(problems))


def path_problems(policy: dict[str, Any], lane: dict[str, Any], relative: str) -> list[str]:
    problems: list[str] = []
    parts = relative.replace("\\", "/").split("/")
    if ":" in relative or any(part in {"", ".", ".."} or part.endswith((".", " ")) for part in parts):
        problems.append(f"unsafe path: {ascii(relative)}")
    if is_denied(policy, relative):
        problems.append(f"denied path: {ascii(relative)}")
    suffix = PurePosixPath(relative.replace("\\", "/")).suffix.casefold()
    if suffix not in {item.casefold() for item in lane["extensions"]}:
        problems.append(f"extension not allowed in lane {ascii(lane['name'])}: {ascii(relative)}")
    secret = secret_path_problem(relative)
    if secret:
        problems.append(f"{secret} in {ascii(relative)}")
    owner = lane_for_path(policy, relative)
    if owner is None or owner["name"] != lane["name"]:
        problems.append(f"path is outside lane {ascii(lane['name'])}: {ascii(relative)}")
    return problems


def _written_texts(root: Path | None, relative: str, tool_input: dict[str, Any]) -> tuple[list[str], list[str]]:
    """Every text a write would put on disk (new content, edit fragments, the file after the edits) and any refusal."""
    texts: list[str] = []
    for key in ("content", "new_source"):
        value = tool_input.get(key)
        if isinstance(value, str):
            texts.append(value)
    edits = tool_input.get("edits")
    if isinstance(edits, list):
        items = [item for item in edits if isinstance(item, dict)]
    elif "new_string" in tool_input:
        items = [tool_input]
    else:
        items = []
    if len(items) > MAX_EDITS:
        return texts, ["too many edits in one write"]
    current: str | None = None
    if items and root is not None:
        target = root / relative
        if target.exists():
            try:
                if target.stat().st_size > 4 * MAX_WRITE_CHARS:
                    return texts, ["the file is too large to check an edit against"]
                current = target.read_text(encoding="utf-8", errors="replace")
            except OSError:
                return texts, ["the file could not be read to check an edit against"]
            if len(current) > MAX_WRITE_CHARS:
                return texts, ["the file is too large to check an edit against"]
    for item in items:
        old, new = item.get("old_string"), item.get("new_string")
        if isinstance(new, str):
            texts.append(new)
        if current is not None and isinstance(old, str) and old and isinstance(new, str):
            current = current.replace(old, new, -1 if item.get("replace_all") is True else 1)
            if len(current) > 4 * MAX_WRITE_CHARS:
                return texts, ["the edited file would be too large to scan"]
    if current is not None and items:
        texts.append(current)
    return texts, []


def write_problems(
    policy: dict[str, Any],
    lease: dict[str, Any],
    relative: str,
    tool_input: dict[str, Any],
    root: Path | None = None,
) -> list[str]:
    """Write-time rules for an owner-policy lease: the same path and content rules as at seal time."""
    lane = _lease_lane(policy, lease)
    if lane is None:
        return ["the lease lane is not in the current policy"]
    problems = path_problems(policy, lane, relative)
    suffix = PurePosixPath(relative.replace("\\", "/")).suffix.casefold()
    texts, refusals = _written_texts(root, relative, tool_input)
    if refusals:
        return list(dict.fromkeys([*problems, *refusals]))
    if any(len(text) > MAX_WRITE_CHARS for text in texts):
        problems.append("written content is too large to scan")
        return list(dict.fromkeys(problems))
    for text in texts:
        if suffix == ".cs":
            problems.extend(cs_scan(text))
        problems.extend(secret_content_problems(text))
        if suffix in {".cs", ".json", ".txt"} and LONG_RUN.search(text):
            problems.append("long encoded run in written content")
    return list(dict.fromkeys(problems))


def lease_count_today(root: Path) -> int:
    try:
        data = json.loads((root / ".ai-governance" / "lease-counter.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return 0
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    if not isinstance(data, dict) or data.get("date") != today or not isinstance(data.get("count"), int):
        return 0
    return data["count"]


def bump_lease_counter(root: Path) -> None:
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    counter = root / ".ai-governance" / "lease-counter.json"
    counter.write_text(json.dumps({"date": today, "count": lease_count_today(root) + 1}) + "\n", encoding="utf-8")


def policy_activation_check(
    root: Path,
    policy: dict[str, Any],
    meta: dict[str, Any],
    review_meta: dict[str, Any],
    repository: dict[str, str],
) -> tuple[list[str], dict[str, Any]]:
    """Owner-policy activation rules. Returns (problems, extra lease fields)."""
    problems: list[str] = []
    if repository["git_branch"] != policy["required_branch"]:
        problems.append(f"current branch must be {ascii(policy['required_branch'])}")
    if meta.get("approval_mode") != "hash":
        problems.append("approval_mode must be hash")
    reviewers = policy["reviewer_ids"]
    if meta.get("approved_by") not in reviewers:
        problems.append("approved_by is not one of the policy reviewer_ids")
    if meta.get("authored_by") in reviewers:
        problems.append("authored_by must not be a policy reviewer id")
    rigor = meta.get("rigor")
    if rigor not in RIGOR_LEVELS:
        problems.append("rigor must be one of R0..R4")
    commands = meta.get("allowed_commands")
    if not isinstance(commands, list) or any(item not in policy["allowed_commands"] for item in commands):
        problems.append("allowed_commands must be empty or listed in the policy")
    subject = meta.get("commit_subject")
    if (
        not isinstance(subject, str)
        or not subject.strip()
        or not SUBJECT.fullmatch(subject)
        or SUBJECT_FORBIDDEN.search(subject)
    ):
        problems.append("commit_subject is missing, blank, too long, has unsafe characters, or names an AI tool")
    lanes: list[dict[str, Any]] = []
    for raw in meta.get("allowed_paths", []):
        entry = str(raw)
        problem = _lane_path_problem(entry)
        if problem:
            problems.append(problem)
            continue
        lane = entry_lane(policy, entry)
        if lane is None:
            problems.append(f"allowed path is outside every lane: {ascii(entry)}")
            continue
        literal = _literal(entry)
        patterns = (*BUILTIN_DENY, *policy["deny_paths"])
        if any(glob_match(literal, item) or glob_match(literal + "/x", item) for item in patterns):
            problems.append(f"allowed path is denied by the policy: {ascii(entry)}")
        lanes.append(lane)
    if len({lane["name"] for lane in lanes}) > 1:
        problems.append("allowed_paths must stay inside one lane")
    if lanes and rigor in RIGOR_LEVELS:
        cap = min(RIGOR_LEVELS.index(lanes[0]["max_rigor"]), RIGOR_LEVELS.index(policy["effective_rigor_cap"]))
        if RIGOR_LEVELS.index(rigor) > cap:
            problems.append(f"rigor {rigor} is above the policy cap {RIGOR_LEVELS[cap]}")
    if lease_count_today(root) >= policy["max_leases_per_day"]:
        problems.append("the daily lease limit is reached")
    if problems or not lanes:
        return problems, {}
    return problems, {
        "policy_id": policy["policy_id"],
        "policy_sha256": policy["policy_sha256"],
        "lane": lanes[0]["name"],
        "commit_subject": subject,
    }


def _ignored_in_lane(root: Path, policy: dict[str, Any], lane: dict[str, Any]) -> list[str]:
    try:
        result = subprocess.run(
            [policy["git_executable"], "status", "--porcelain=v1", "-z", "--ignored=matching", "--untracked-files=all"],
            cwd=root, text=True, encoding="utf-8", errors="replace", capture_output=True, check=False, timeout=30,
        )
    except (OSError, subprocess.SubprocessError):
        return ["git status could not be read to look for ignored files"]
    if result.returncode != 0:
        return ["git status could not be read to look for ignored files"]
    found: list[str] = []
    for entry in result.stdout.split("\0"):
        if entry.startswith("!! "):
            path = entry[3:]
            owner = lane_for_path(policy, path)
            if owner is not None and owner["name"] == lane["name"]:
                found.append(f"ignored file inside lane {ascii(lane['name'])}: {ascii(path)}")
    return found


def _meta_guid_problems(root: Path, paths: list[str]) -> list[str]:
    changed = {path for path in paths if path.casefold().endswith(".meta")}
    assets = root / "Assets"
    if not changed or not assets.is_dir():
        return []
    seen: dict[str, str] = {}
    problems: list[str] = []
    for meta_file in sorted(assets.rglob("*.meta")):
        try:
            found = GUID.search(meta_file.read_text(encoding="utf-8", errors="replace"))
        except OSError:
            continue
        if not found:
            continue
        guid = found.group(1).lower()
        relative = meta_file.relative_to(root).as_posix()
        if guid in seen and (relative in changed or seen[guid] in changed):
            problems.append(f"duplicate .meta GUID {guid} in {ascii(relative)} and {ascii(seen[guid])}")
        seen.setdefault(guid, relative)
    return problems


def _guid_index(root: Path) -> dict[str, str]:
    index: dict[str, str] = {}
    for folder in ("Assets", "Packages"):
        base = root / folder
        if not base.is_dir():
            continue
        for meta_file in base.rglob("*.meta"):
            try:
                found = GUID.search(meta_file.read_text(encoding="utf-8", errors="replace"))
            except OSError:
                continue
            if found:
                index.setdefault(found.group(1).lower(), meta_file.relative_to(root).as_posix()[:-5])
    return index


def _denied_outside_packages(policy: dict[str, Any], target: str) -> bool:
    """Denied by any pattern except the broad Packages one, so Packages/**/Editor and .dll still count."""
    patterns = [item for item in deny_patterns(policy) if _norm(item) != "packages/**"]
    return any(glob_match(target, pattern) for pattern in patterns)


def _yaml_reference_problems(root: Path, policy: dict[str, Any], paths: list[str]) -> list[str]:
    """A lane YAML asset may not reference (by GUID) an asset in a denied place such as Editor or Plugins."""
    yaml_files = [
        path for path in paths
        if PurePosixPath(path.replace("\\", "/")).suffix.casefold() in YAML_EXTENSIONS and (root / path).is_file()
    ]
    if not yaml_files:
        return []
    index = _guid_index(root)
    problems: list[str] = []
    for relative in yaml_files:
        text = (root / relative).read_text(encoding="utf-8", errors="replace")
        for match in GUID_REF.finditer(text):
            target = index.get(match.group(1).lower())
            if target and _denied_outside_packages(policy, target):
                problems.append(f"{ascii(relative)} references a denied asset: {ascii(target)}")
    return list(dict.fromkeys(problems))


def seal_policy_problems(root: Path, policy: dict[str, Any], lease: dict[str, Any], paths: list[str]) -> list[str]:
    """Extra checks applied when an owner-policy lease is sealed."""
    lane = _lease_lane(policy, lease)
    if lane is None:
        return ["the lease lane is not in the current policy"]
    problems: list[str] = []
    if len(paths) > policy["max_changed_paths"]:
        problems.append(f"too many changed paths ({len(paths)} > {policy['max_changed_paths']})")
    total = 0
    for relative in paths:
        problems.extend(path_problems(policy, lane, relative))
        target = root / relative
        if not target.is_file():
            continue
        label = ascii(relative)
        size = target.stat().st_size
        total += size
        if size > MAX_SCAN_BYTES:
            problems.append(f"file is too large to scan: {label}")
            continue
        data = target.read_bytes()
        suffix = PurePosixPath(relative.replace("\\", "/")).suffix.casefold()
        problems.extend(f"{label}: {item}" for item in secret_content_problems(data.decode("latin-1")))
        if suffix == ".png" and not data.startswith(PNG_MAGIC):
            problems.append(f"file is not a PNG image: {label}")
        if suffix not in TEXT_EXTENSIONS:
            continue
        if b"\0" in data:
            problems.append(f"text file contains NUL bytes (UTF-16 or binary): {label}")
            continue
        if suffix == ".cs":
            try:
                text = data.decode("utf-8-sig")
            except UnicodeDecodeError:
                problems.append(f"C# file is not valid UTF-8: {label}")
                continue
            problems.extend(f"{label}: {item}" for item in cs_scan(text))
            if LONG_RUN.search(text):
                problems.append(f"{label}: long encoded run")
        elif suffix in {".json", ".txt"} and LONG_RUN.search(data.decode("utf-8", errors="replace")):
            problems.append(f"{label}: long encoded run")
    if total > policy["max_total_bytes"]:
        problems.append(f"changed files are too large ({total} > {policy['max_total_bytes']} bytes)")
    problems.extend(_ignored_in_lane(root, policy, lane))
    problems.extend(_meta_guid_problems(root, paths))
    problems.extend(_yaml_reference_problems(root, policy, paths))
    return problems
'''

# --- .claude/hooks/common.py ---------------------------------------------------------------------
edit(
    ".claude/hooks/common.py",
    r'''    "scripts/agent_commit.py",
''',
    r'''    "scripts/agent_commit.py",
    ".git/**",
''',
)
edit(
    ".claude/hooks/common.py",
    r'''    if not policy["required_branch"].startswith("agent/"):
        return "Owner policy required_branch must start with agent/"''',
    r'''    if policy["required_branch"] == "main":
        remote_url = policy.get("remote_url")
        if (
            policy.get("commit_to_default_branch") is not True
            or policy["base_branch"] != "main"
            or policy.get("remote_name") != "origin"
            or not isinstance(remote_url, str)
            or not re.fullmatch(r"https://[A-Za-z0-9.-]+/[\w./-]+", remote_url, re.ASCII)
            or ".." in remote_url
            or not _is_int(policy.get("max_unpushed_commits"))
        ):
            return "Owner policy branch main needs commit_to_default_branch, origin, an https remote_url, and max_unpushed_commits"
    elif not policy["required_branch"].startswith("agent/"):
        return "Owner policy required_branch must be main (with acknowledgement fields) or start with agent/"''',
)
edit(
    ".claude/hooks/common.py",
    r'''    if policy.get("effective_rigor_cap") not in RIGOR_LEVELS:''',
    r'''    if policy.get("effective_rigor_cap") not in RIGOR_LEVELS[:3]:''',
)
edit(
    ".claude/hooks/common.py",
    r'''            or lane.get("max_rigor") not in RIGOR_LEVELS''',
    r'''            or lane.get("max_rigor") not in RIGOR_LEVELS[:3]''',
)
edit(
    ".claude/hooks/common.py",
    r'''    if not isinstance(lease["allowed_commands"], list):
        return None, "Lease allowed_commands is invalid"
    return lease, "Active implementation lease is valid"''',
    r'''    if not isinstance(lease["allowed_commands"], list):
        return None, "Lease allowed_commands is invalid"
    if lease.get("authority") == "owner-policy":
        policy, _ = load_owner_policy(root)
        if policy is None or policy["policy_sha256"] != lease.get("policy_sha256"):
            return None, "Owner policy is missing, invalid, or changed since activation"
    return lease, "Active implementation lease is valid"''',
)

# --- .claude/hooks/govern_write.py ---------------------------------------------------------------
edit(
    ".claude/hooks/govern_write.py",
    r'''    if lease and matches_any(root_relative, lease["allowed_paths"]):
        emit_decision(data, "allow", f"Path is inside active task {lease['task_id']}: {root_relative}")
        return''',
    r'''    if lease and matches_any(root_relative, lease["allowed_paths"]):
        if lease.get("authority") == "owner-policy":
            from policy_lib import write_problems

            lease_policy = load_owner_policy(project_root())[0]
            problems = (
                write_problems(lease_policy, lease, root_relative, tool_input, project_root())
                if lease_policy is not None
                else ["the owner policy is unavailable"]
            )
            if problems:
                emit_decision(data, "deny", "Owner-policy write refused: " + "; ".join(problems))
                return
        emit_decision(data, "allow", f"Path is inside active task {lease['task_id']}: {root_relative}")
        return''',
)

# --- scripts/activate_lease.py -------------------------------------------------------------------
edit(
    "scripts/activate_lease.py",
    r'''from common import CONTROLLED_PATHS, git_dirty_paths, git_state, matches_any, parse_frontmatter  # noqa: E402''',
    r'''from common import CONTROLLED_PATHS, git_dirty_paths, git_state, load_owner_policy, matches_any, parse_frontmatter  # noqa: E402
from policy_lib import bump_lease_counter, policy_activation_check  # noqa: E402''',
)
edit(
    "scripts/activate_lease.py",
    r'''    parser = argparse.ArgumentParser(description="Activate a scoped implementation lease")''',
    r'''    parser = argparse.ArgumentParser(description="Activate a scoped implementation lease", allow_abbrev=False)''',
)
edit(
    "scripts/activate_lease.py",
    r'''        help="Accept uncommitted changes that already sit inside the task's allowed_paths",
    )
    args = parser.parse_args()
''',
    r'''        help="Accept uncommitted changes that already sit inside the task's allowed_paths",
    )
    parser.add_argument(
        "--owner-policy",
        action="store_true",
        help="Activate under the owner's standing policy (no prompts; the policy checks apply)",
    )
    args = parser.parse_args()
''',
)
edit(
    "scripts/activate_lease.py",
    r'''    if not 0 < args.hours <= 24:
        fail("--hours must be greater than 0 and at most 24")
''',
    r'''    policy = None
    if args.owner_policy:
        if args.inherit_dirty:
            fail("--inherit-dirty cannot be combined with --owner-policy")
        policy, policy_reason = load_owner_policy(ROOT)
        if policy is None:
            fail(policy_reason)
        if not any(item == "--hours" or item.startswith("--hours=") for item in sys.argv):
            args.hours = float(policy["max_lease_hours"])
        if args.hours > policy["max_lease_hours"]:
            fail(f"--hours exceeds the policy limit of {policy['max_lease_hours']}")
    if not 0 < args.hours <= 24:
        fail("--hours must be greater than 0 and at most 24")
''',
)
edit(
    "scripts/activate_lease.py",
    r'''    dirty, dirty_reason = git_dirty_paths(ROOT)
    if dirty is None:''',
    r'''    policy_extras: dict = {}
    if policy is not None:
        policy_problems, policy_extras = policy_activation_check(ROOT, policy, meta, review_meta, repository)
        if policy_problems:
            fail("owner-policy activation refused: " + "; ".join(policy_problems))
    dirty, dirty_reason = git_dirty_paths(ROOT)
    if dirty is None:''',
)
edit(
    "scripts/activate_lease.py",
    r'''    if input("\nType the exact task ID: ").strip() != meta["task_id"]:
        fail("task ID confirmation failed")
    if input("Type ACTIVATE: ").strip() != "ACTIVATE":
        fail("activation phrase not confirmed")
''',
    r'''    if policy is None:
        if input("\nType the exact task ID: ").strip() != meta["task_id"]:
            fail("task ID confirmation failed")
        if input("Type ACTIVATE: ").strip() != "ACTIVATE":
            fail("activation phrase not confirmed")
''',
)
edit(
    "scripts/activate_lease.py",
    r'''        "inherited_paths": inherited_hashes,
        **repository,
    }
''',
    r'''        "inherited_paths": inherited_hashes,
        "authority": "owner-policy" if policy is not None else "human",
        **policy_extras,
        **repository,
    }
''',
)
edit(
    "scripts/activate_lease.py",
    r'''    print(f"\nACTIVE: {meta['task_id']} until {lease['expires_at']}")''',
    r'''    if policy is not None:
        bump_lease_counter(ROOT)
    print(f"\nACTIVE: {meta['task_id']} until {lease['expires_at']}")''',
)

# --- scripts/seal_implementation.py ---------------------------------------------------------------
edit(
    "scripts/seal_implementation.py",
    r'''from common import file_sha256, load_lease, matches_any  # noqa: E402''',
    r'''from common import file_sha256, load_lease, load_owner_policy, matches_any  # noqa: E402
from policy_lib import seal_policy_problems  # noqa: E402''',
)
edit(
    "scripts/seal_implementation.py",
    r'''    if outside:
        raise SystemExit("ERROR: changed paths outside lease: " + ", ".join(outside))
''',
    r'''    if outside:
        raise SystemExit("ERROR: changed paths outside lease: " + ", ".join(outside))
    if lease.get("authority") == "owner-policy":
        policy, policy_reason = load_owner_policy(ROOT)
        if policy is None:
            raise SystemExit(f"ERROR: {policy_reason}")
        if policy["policy_sha256"] != lease.get("policy_sha256"):
            raise SystemExit("ERROR: the owner policy changed since activation")
        seal_problems = seal_policy_problems(ROOT, policy, lease, paths)
        if seal_problems:
            raise SystemExit("ERROR: owner-policy seal refused: " + "; ".join(seal_problems))
''',
)

# --- scripts/validate_os.py: copy exclusions and tests ---------------------------------------------
edit(
    "scripts/validate_os.py",
    r'''        project = Path(temp) / "project"
        shutil.copytree(
            ROOT, project,
            ignore=shutil.ignore_patterns(
                "__pycache__", "*.pyc", "implementation-lease.json", "implementation-seals", "scheduled_tasks.lock",
            ),
        )''',
    r'''        project = Path(temp) / "project"
        shutil.copytree(
            ROOT, project,
            ignore=shutil.ignore_patterns(
                "__pycache__", "*.pyc", "implementation-lease.json", "implementation-seals", "scheduled_tasks.lock",
                "owner-policy.json", "lease-counter.json", "empty-hooks",
            ),
        )''',
)
edit(
    "scripts/validate_os.py",
    r'''        project = root / "r4-project"
        shutil.copytree(
            ROOT, project,
            ignore=shutil.ignore_patterns(
                "__pycache__", "*.pyc", "implementation-lease.json", "implementation-seals", "scheduled_tasks.lock",
            ),
        )''',
    r'''        project = root / "r4-project"
        shutil.copytree(
            ROOT, project,
            ignore=shutil.ignore_patterns(
                "__pycache__", "*.pyc", "implementation-lease.json", "implementation-seals", "scheduled_tasks.lock",
                "owner-policy.json", "lease-counter.json", "empty-hooks",
            ),
        )''',
)
edit(
    "scripts/validate_os.py",
    r'''def validate_repository_attestation(v: Validation) -> None:''',
    r'''def validate_policy_lib(v: Validation) -> None:
    import common
    import policy_lib

    git_path = shutil.which("git")
    if not git_path:
        v.check(False, "git must be available for the policy library tests")
        return
    policy = valid_owner_policy(str(Path(git_path).resolve()))
    policy["lanes"] = [
        {"name": "prototype", "allowed_paths": ["Assets/_Prototype/**", "Assets/_Prototype.meta"], "max_rigor": "R1", "extensions": [".cs", ".meta", ".txt"]},
        {"name": "game", "allowed_paths": ["Assets/Game/**"], "max_rigor": "R2", "extensions": [".cs", ".meta"]},
    ]
    policy["policy_sha256"] = "0" * 64
    good_cs = "using System;\nusing System.Collections.Generic;\nusing UnityEngine;\nusing UnityEngine.UI;\n\npublic class A : MonoBehaviour { }\n"
    v.check(policy_lib.cs_scan(good_cs) == [], "an ordinary C# file must pass the scan")
    v.check(policy_lib.cs_scan("// note\n/// <summary>Doc.</summary>\nclass A { }\n") == [], "whole-line comments must pass the scan")
    bad_cs = {
        "using System.IO;": "namespace",
        "using System.Diagnostics;": "namespace",
        "using UnityEngine.Networking;": "namespace",
        "using static System.Math;": "using form",
        "using Alias = System.Text.StringBuilder;": "using form",
        "global using System;": "using form",
        "\ufeffusing Microsoft.Win32;\nclass A {}": "bom and namespace root",
        "namespace N { using System.Diagnostics; class A {} }": "using inside a namespace",
        "using System; using System.Net;": "second using on a line",
        "using /* c */ System.IO;": "comment inside a using",
        "class A { void F() { System /* c */ . IO . File . Delete(\"x\"); } }": "comment splits a token",
        "class A { void F() { System // c\n .IO.File.Delete(\"x\"); } }": "line comment splits a token",
        "class A { string s = \"http://x\"; void F() { System.IO.File.Delete(s); } }": "slashes in a string hide nothing",
        "class A { string s = \"\\U00000053\"; }": "long unicode escape",
        "class A { void F() { Microsoft.Win32.Registry.CurrentUser.Close(); } }": "qualified registry access",
        "class A { void F() { System.AppDomain.CurrentDomain.Load(null); } }": "runtime loading",
        "class A { dynamic d; }": "dynamic",
        "class A { void F() { global::System.IO.File.Delete(\"x\"); } }": "global qualified name",
        "using UnityEditor;": "editor",
        "class A { [InitializeOnLoad] static A() {} }": "initialize on load",
        "class A { [DllImport(\"x\")] static extern void F(); }": "dll import",
        "class A { void F() { System.Diagnostics.Process.Start(\"x\"); } }": "process",
        "class A { void F() { var t = obj.GetType().GetMethod(\"M\"); } }": "reflection",
        "class A { string s = \"\\u0053\"; }": "unicode escape",
        "#if UNITY_EDITOR\nclass A {}\n#endif": "conditional compilation",
        "#define X\nclass A {}": "preprocessor define",
        "class A { string s = \"/*\"; void F() { System /* c */ . IO . File . Delete(\"x\"); } }": "string with a comment opener",
        "class A { string s = \"//\"; void F() { System // c\n .IO.File.Delete(\"x\"); } }": "string with slashes and a line-comment split",
        "class A { string s = @\"/*\"; void F() { System /* c */ . IO . File . Delete(\"x\"); } }": "verbatim string with a comment opener",
        "class A { void F() { Sys​tem.IO.File.Delete(\"x\"); } }": "invisible formatting character",
        "class A { void F() {\nSystem\n// c\n.IO.File.Delete(\"x\");\n} }": "whole-line comment splits a token",
        "class A { int x; // trailing\n}": "trailing comments are refused",
        "class A { string s = $\"{\"//\"}\"; void F() { System/*c*/.IO.File.Delete(s); } }": "interpolation hole with slashes",
        "#region x'\nclass A { void F() { System /* c */ . IO . File . Delete(\"x\"); } }": "apostrophe in a directive",
        ("class A { void F() { Sys" + chr(0x200B) + "tem.IO.File.Delete(\"x\"); } }"): "invisible character built with chr",
        "class A { void F() {\nSystem\n#pragma warning disable\n.IO.File.Delete(\"x\");\n} }": "preprocessor directive splits a token",
        "#nullable enable\nclass A {}\n": "any preprocessor directive is refused",
        "//a\rSystem\r//b\r.IO.File.Delete(x);": "bare carriage returns hide a token behind comments",
        ("//a" + chr(0x2028) + "System" + chr(0x2028) + "//b" + chr(0x2028) + ".IO.File.Delete(x);"): "line separator hides a token behind comments",
        "class A { void F() { Unity.Foo.Bar(); } }": "unity qualified name",
        "class A { void F() { var m = typeof(A).Module; } }": "module",
        "class A { void F() { new WWW(\"x\"); } }": "www",
        "class A { void F() { PlayerPrefs.SetString(\"a\", \"b\"); } }": "player prefs",
        "class A { void F() { Application.OpenURL(\"x\"); } }": "open url",
    }
    for source, label in bad_cs.items():
        v.check(bool(policy_lib.cs_scan(source)), f"the C# scan must reject ({label}): {source[:40]!r}")
    v.check(policy_lib.cs_scan("class A { void F() { int x = Application.targetFrameRate; var y = obj.GetType(); var z = System.Math.Abs(1); } }") == [], "ordinary Application, GetType and System.Math use must pass")
    for text in (
        "-----BEGIN RSA PRIVATE KEY-----",
        "key = AKIAABCDEFGHIJKLMNOP",
        "ghp_" + "a" * 36,
        "https://user:pass@example.com/x",
        "password = hunter2hunter2",
    ):
        v.check(bool(policy_lib.secret_content_problems(text)), f"the secret scan must flag: {text[:30]!r}")
    v.check(policy_lib.secret_content_problems("public int Score = 10; // token count") == [], "harmless text must pass the secret scan")
    v.check(bool(policy_lib.LONG_RUN.search("A" * 130)), "a long base64-looking run must be flagged")
    v.check(policy_lib.LONG_RUN.search("public int Score = 10;") is None, "ordinary text must not look like an encoded run")
    for relative in (".env", "Assets/Game/id_rsa", "Assets/Game/server.pem", "Assets/Game/my_secret.json", "Assets/credentials.txt"):
        v.check(policy_lib.secret_path_problem(relative) is not None, f"secret-looking path must be flagged: {relative}")
    v.check(policy_lib.secret_path_problem("Assets/Game/Player.cs") is None, "an ordinary path must not be flagged")
    lane = policy["lanes"][0]
    v.check(policy_lib.path_problems(policy, lane, "Assets/_Prototype/A.cs") == [], "an in-lane path must pass")
    for relative, reason in (
        ("Assets/_Prototype/Editor/A.cs", "editor"),
        ("Assets/_Prototype/A.dll", "dll"),
        ("Assets/_Prototype/A.asmdef", "asmdef"),
        ("Assets/_Prototype/.gitignore", "gitignore"),
        ("Assets/_Prototype/A.png", "extension"),
        ("Assets/Game/A.cs", "other lane"),
        ("Assets/_Prototype/A.cs:stream", "stream"),
        ("Assets/_Prototype/A.cs.", "trailing dot"),
        (".claude/hooks/x.py", "controlled"),
        ("scripts/x.py", "policy deny"),
    ):
        v.check(bool(policy_lib.path_problems(policy, lane, relative)), f"a path must be refused ({reason}): {relative}")
    lease = {"lane": "prototype"}
    v.check(policy_lib.write_problems(policy, lease, "Assets/_Prototype/A.cs", {"content": good_cs}) == [], "a compliant write must pass the write-time rules")
    v.check(bool(policy_lib.write_problems(policy, lease, "Assets/_Prototype/Editor/A.cs", {"content": "class A {}"})), "a write into an Editor folder must be refused at write time")
    v.check(bool(policy_lib.write_problems(policy, lease, "Assets/_Prototype/A.cs", {"content": "using UnityEditor;"})), "a write with editor code must be refused at write time")
    v.check(bool(policy_lib.write_problems(policy, lease, "Assets/_Prototype/n.txt", {"content": "AKIAABCDEFGHIJKLMNOP"})), "a write with a secret must be refused at write time")
    v.check(bool(policy_lib.write_problems(policy, lease, "Assets/_Prototype/A.cs", {"new_string": "System.IO.File.Delete(x);"})), "an edit fragment must be scanned at write time")
    v.check(bool(policy_lib.write_problems(policy, {"lane": "unknown"}, "Assets/_Prototype/A.cs", {})), "an unknown lease lane must refuse writes")
    v.check(bool(policy_lib.write_problems(policy, lease, "Assets/_Prototype/A.cs", {"content": "/*" * 150000})), "an oversized write must be refused before any scan")
    v.check(bool(policy_lib.write_problems(policy, lease, "Assets/_Prototype/A.cs", {"edits": [{"old_string": "a", "new_string": "System.IO.File.Delete(x);"}]})), "MultiEdit fragments must be scanned")
    with tempfile.TemporaryDirectory(prefix="aigdo-edit-") as scratch:
        scratch_root = Path(scratch)
        (scratch_root / "Assets" / "_Prototype").mkdir(parents=True)
        (scratch_root / "Assets" / "_Prototype" / "S.cs").write_text("class A { void F() { System } }", encoding="utf-8")
        split_edit = {"old_string": " } }", "new_string": ".IO.File.Delete(x); } }"}
        v.check(policy_lib.write_problems(policy, lease, "Assets/_Prototype/A.cs", split_edit) == [], "a fragment alone can look harmless")
        v.check(bool(policy_lib.write_problems(policy, lease, "Assets/_Prototype/S.cs", split_edit, scratch_root)), "an edit must be judged on the resulting file")
        (scratch_root / "Assets" / "_Prototype" / "Huge.cs").write_text("x" * 900000, encoding="utf-8")
        v.check(
            bool(policy_lib.write_problems(policy, lease, "Assets/_Prototype/Huge.cs", {"old_string": "x", "new_string": "y"}, scratch_root)),
            "an edit to a file too large to check must be refused",
        )
    import time as _time

    started = _time.monotonic()
    v.check(bool(policy_lib.write_problems(policy, lease, "Assets/_Prototype/n.txt", {"content": "eyJ" * 60000})), "a long repeated token run must be refused without hanging")
    v.check(isinstance(policy_lib.write_problems(policy, lease, "Assets/_Prototype/n.txt", {"content": "://a:" * 39999}), list), "a long repeated credential-like run must finish")
    v.check(_time.monotonic() - started < 20, "the two long adversarial runs must finish within 20 seconds")
    v.check(len(policy_lib.write_problems(policy, lease, "Assets/_Prototype/A.cs", {"edits": [{"old_string": "a", "new_string": "b"}] * 51})) > 0, "too many edits in one write must be refused")
    for entry, expected in (
        ("Assets/_Prototype/**", "prototype"),
        ("Assets/_Prototype/Sub/**", "prototype"),
        ("Assets/_Prototype/A.cs", "prototype"),
        ("Assets/_Prototype.meta", "prototype"),
        ("Assets/Game/**", "game"),
        ("Assets/Other/**", None),
        ("Assets/**", None),
        ("Assets/_PrototypeX/**", None),
    ):
        found = policy_lib.entry_lane(policy, entry)
        v.check((found["name"] if found else None) == expected, f"entry lane for {entry} must be {expected}")
    base = {"approval_mode": "hash", "approved_by": "independent-reviewer", "authored_by": "implementation-author",
            "rigor": "R1", "allowed_commands": [], "commit_subject": "Add prototype file", "allowed_paths": ["Assets/_Prototype/**"]}
    repo = {"git_branch": "agent/work"}
    no_root = Path(tempfile.gettempdir()) / "aigdo-no-such-root"

    def check(**changes: object) -> list[str]:
        problems, _ = policy_lib.policy_activation_check(no_root, policy, {**base, **changes}, {}, repo)
        return problems

    v.check(check() == [], "a compliant task must pass the activation checks")
    for label, changes in {
        "rigor above lane": {"rigor": "R2"},
        "rigor missing": {"rigor": "R9"},
        "commands": {"allowed_commands": ["dotnet build"]},
        "subject attribution": {"commit_subject": "Co-Authored-By: someone"},
        "subject charset": {"commit_subject": "bad $(x)"},
        "subject blank": {"commit_subject": "   "},
        "subject missing": {"commit_subject": None},
        "reviewer": {"approved_by": "somebody"},
        "self review": {"authored_by": "independent-reviewer"},
        "approval mode": {"approval_mode": "ssh-signature"},
        "outside lane": {"allowed_paths": ["Assets/Other/**"]},
        "two lanes": {"allowed_paths": ["Assets/_Prototype/**", "Assets/Game/**"]},
        "denied path": {"allowed_paths": ["Assets/_Prototype/Editor/**"]},
        "wildcard": {"allowed_paths": ["Assets/_Prototype/*.cs"]},
    }.items():
        v.check(bool(check(**changes)), f"the activation checks must refuse ({label})")
    v.check(policy_lib.policy_activation_check(no_root, policy, {**base, "rigor": "R2", "allowed_paths": ["Assets/Game/**"]}, {}, repo)[0] != [], "R2 must exceed the R1 policy cap")
    branch_repo = {"git_branch": "main"}
    v.check(bool(policy_lib.policy_activation_check(no_root, policy, base, {}, branch_repo)[0]), "the wrong branch must be refused")
    with tempfile.TemporaryDirectory(prefix="aigdo-branch-") as temp:
        root = Path(temp)
        (root / ".ai-governance").mkdir()
        target = root / ".ai-governance" / "owner-policy.json"
        main_policy = {
            **valid_owner_policy(str(Path(git_path).resolve())), "required_branch": "main",
            "commit_to_default_branch": True, "remote_name": "origin", "remote_url": "https://github.com/o/r",
            "max_unpushed_commits": 5,
        }
        target.write_text(json.dumps(main_policy), encoding="utf-8")
        v.check(common.load_owner_policy(root)[0] is not None, "a main-branch policy with every acknowledgement field must load")
        for label, changes in {
            "no acknowledgement": {"commit_to_default_branch": False},
            "no remote": {"remote_url": None},
            "credential url": {"remote_url": "https://user:pw@github.com/o/r"},
            "http url": {"remote_url": "http://github.com/o/r"},
            "traversal url": {"remote_url": "https://github.com/o/../r"},
            "other remote": {"remote_name": "upstream"},
            "no cap": {"max_unpushed_commits": 0},
            "other base": {"base_branch": "develop"},
            "rigor cap R3": {"required_branch": "agent/work", "effective_rigor_cap": "R3"},
            "lane rigor R4": {"required_branch": "agent/work", "lanes": [{"name": "x", "allowed_paths": ["Assets/X/**"], "max_rigor": "R4", "extensions": [".cs"]}]},
        }.items():
            target.write_text(json.dumps({**main_policy, **changes}), encoding="utf-8")
            v.check(common.load_owner_policy(root)[0] is None, f"a policy must be refused ({label})")
    v.check(common.matches_any(".git/config", common.CONTROLLED_PATHS), ".git internals must be controlled paths")
    v.check(not common.matches_any(".gitignore", common.CONTROLLED_PATHS), ".gitignore must not be a controlled path")


def validate_owner_policy_activation(v: Validation) -> None:
    git_path = shutil.which("git")
    if not git_path:
        v.check(False, "git must be available for the owner-policy activation tests")
        return
    git_path = str(Path(git_path).resolve())
    write_hook = HOOKS / "govern_write.py"
    with tempfile.TemporaryDirectory(prefix="aigdo-b1-") as temp:
        project = Path(temp) / "project"
        shutil.copytree(
            ROOT, project,
            ignore=shutil.ignore_patterns(
                ".git", "__pycache__", "*.pyc", "implementation-lease.json", "implementation-seals",
                "scheduled_tasks.lock", "owner-policy.json", "lease-counter.json", "empty-hooks",
            ),
        )

        def git(*args: str) -> None:
            subprocess.run([git_path, *args], cwd=project, check=True, capture_output=True)

        git("init", "-q")
        git("symbolic-ref", "HEAD", "refs/heads/agent/work")
        git("config", "user.email", "validator@example.invalid")
        git("config", "user.name", "AIGDO Validator")
        task = project / "docs" / "05-production" / "tasks" / "TASK-POLICY-ATTEST.md"
        review = project / "docs" / "07-evidence" / "READY-TASK-POLICY-ATTEST.md"
        task.write_text(
            "---\n"
            "task_id: TASK-POLICY-ATTEST\n"
            "status: READY_FOR_IMPLEMENTATION\n"
            "authored_by: implementation-author\n"
            "approved_by: independent-reviewer\n"
            "ready_review_receipt: docs/07-evidence/READY-TASK-POLICY-ATTEST.md\n"
            "rigor: R1\n"
            "approval_mode: hash\n"
            "system_id: SYS-POLICY-ATTEST\n"
            "commit_subject: Add prototype test file\n"
            "allowed_paths:\n"
            "  - Assets/_Prototype/**\n"
            "allowed_commands:\n"
            "---\n"
            "# Owner-policy attestation task\n",
            encoding="utf-8",
        )
        review.write_text(
            "---\n"
            "review_id: REVIEW-TASK-POLICY-ATTEST-R1\n"
            "task_id: TASK-POLICY-ATTEST\n"
            "disposition: READY_FOR_IMPLEMENTATION\n"
            "reviewer: independent-reviewer\n"
            f"task_sha256: {sha256(task)}\n"
            "reviewed_at: 2026-09-16T00:00:00Z\n"
            "approval_mode: hash\n"
            "signature_file: UNSET\n"
            "allowed_signers_file: UNSET\n"
            "---\n# Ready review\n",
            encoding="utf-8",
        )
        plugins = project / "Assets" / "Plugins"
        plugins.mkdir(parents=True, exist_ok=True)
        (plugins / "P.cs").write_text("class P {}\n", encoding="utf-8")
        (plugins / "P.cs.meta").write_text("fileFormatVersion: 2\nguid: fedcba9876543210fedcba9876543210\n", encoding="utf-8")
        git("add", ".")
        git("commit", "-qm", "policy base")
        policy_file = project / ".ai-governance" / "owner-policy.json"
        lease_path = project / ".ai-governance" / "implementation-lease.json"
        lane_dir = project / "Assets" / "_Prototype"

        def policy(**changes: object) -> dict:
            base = valid_owner_policy(git_path)
            base["lanes"] = [
                {"name": "prototype", "allowed_paths": ["Assets/_Prototype/**"], "max_rigor": "R1", "extensions": [".cs", ".meta", ".txt", ".png", ".asset"]}
            ]
            return {**base, **changes}

        def write_policy(**changes: object) -> None:
            policy_file.write_text(json.dumps(policy(**changes)), encoding="utf-8")

        def activate(*extra: str) -> subprocess.CompletedProcess[str]:
            return subprocess.run(
                [sys.executable, "scripts/activate_lease.py", "docs/05-production/tasks/TASK-POLICY-ATTEST.md", "--owner-policy", *extra],
                cwd=project, input="", text=True, encoding="utf-8", errors="replace", capture_output=True, check=False,
            )

        def seal() -> subprocess.CompletedProcess[str]:
            return subprocess.run(
                [sys.executable, "scripts/seal_implementation.py"],
                cwd=project, input="", text=True, encoding="utf-8", errors="replace", capture_output=True, check=False,
            )

        def hook_write(relative: str, content: str | None = None) -> str:
            tool_input: dict = {"file_path": str(project / relative)}
            if content is not None:
                tool_input["content"] = content
            payload = {"hook_event_name": "PreToolUse", "cwd": str(project), "tool_name": "Write", "tool_input": tool_input}
            return decision(hook_call(write_hook, project, payload))

        v.check(activate().returncode == 2, "owner-policy activation must be refused without a policy file")
        write_policy()
        v.check(activate("--inherit-dirty").returncode == 2, "owner-policy activation must refuse --inherit-dirty")
        v.check(activate("--hours", "9").returncode == 2, "owner-policy activation must refuse hours above the policy limit")
        v.check(activate("--hours=9").returncode == 2, "owner-policy activation must refuse hours above the limit in the = form")
        v.check(activate("--hou", "2").returncode == 2, "an abbreviated --hours must be refused")
        for label, changes in {
            "reviewer": {"reviewer_ids": ["somebody-else"]},
            "lane": {"lanes": [{"name": "other", "allowed_paths": ["Assets/Other/**"], "max_rigor": "R1", "extensions": [".cs"]}]},
            "deny": {"deny_paths": ["Assets/_Prototype/**"]},
            "rigor cap": {"effective_rigor_cap": "R0", "lanes": [{"name": "prototype", "allowed_paths": ["Assets/_Prototype/**"], "max_rigor": "R0", "extensions": [".cs"]}]},
            "branch": {"required_branch": "agent/other"},
        }.items():
            write_policy(**changes)
            refused = activate()
            v.check(
                refused.returncode == 2 and not lease_path.exists(),
                f"owner-policy activation must be refused ({label}): {refused.stderr.strip()}",
            )
        write_policy(max_leases_per_day=2)
        first = activate()
        try:
            lease = json.loads(lease_path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            lease = {}
        v.check(first.returncode == 0, f"a compliant task must activate under the policy without prompts: {first.stderr.strip()}")
        v.check(
            lease.get("authority") == "owner-policy" and lease.get("lane") == "prototype"
            and lease.get("commit_subject") == "Add prototype test file" and bool(lease.get("policy_sha256")),
            "an owner-policy lease must record its authority, lane, commit subject, and policy hash",
        )
        again = activate()
        v.check(again.returncode == 2 and "unexpired ACTIVE lease" in again.stderr, "a second activation while a lease is active must be refused")
        lease_path.unlink(missing_ok=True)
        v.check(activate().returncode == 0, "a second lease within the daily limit must activate")
        lease_path.unlink(missing_ok=True)
        limited = activate()
        v.check(limited.returncode == 2 and "daily lease limit" in limited.stderr, "the daily lease limit must be enforced")
        write_policy()
        v.check(activate().returncode == 0, "activation must succeed again once the limit allows it")

        lane_dir.mkdir(parents=True, exist_ok=True)
        (project / "Assets" / "Other").mkdir(parents=True, exist_ok=True)
        v.check(hook_write("Assets/_Prototype/Good.cs", "using UnityEngine;\nclass G {}\n") == "allow", "the write hook must allow a compliant lane write")
        v.check(hook_write("Assets/_Prototype/Editor/E.cs", "class E {}\n") == "deny", "the write hook must refuse an Editor-folder write")
        v.check(hook_write("Assets/_Prototype/Bad.cs", "using UnityEditor;\n") == "deny", "the write hook must refuse editor code")
        v.check(hook_write("Assets/_Prototype/note.txt", "AKIAABCDEFGHIJKLMNOP\n") == "deny", "the write hook must refuse a secret")
        v.check(hook_write("Assets/_Prototype/Cf.cs", "class C { void F() { Sys​tem.IO.File.Delete(\"x\"); } }\n") == "deny", "the write hook must refuse an invisible formatting character")
        v.check(hook_write("Assets/_Prototype/Big.cs", "/*" * 150000) == "deny", "the write hook must refuse an oversized write")
        v.check(hook_write("Assets/_Prototype/Cf2.cs", "class C { void F() { Sys" + chr(0x200B) + "tem.IO.File.Delete(\"x\"); } }\n") == "deny", "the write hook must refuse an invisible character built with chr")
        v.check(hook_write("Assets/_Prototype/Tr.cs", "class C { int x; // trailing\n}\n") == "deny", "the write hook must refuse a trailing comment")
        v.check(hook_write("Assets/_Prototype/evil.dll", "MZ") == "deny", "the write hook must refuse a forbidden extension")
        v.check(hook_write("Assets/Other/X.cs", "class X {}\n") == "deny", "the write hook must refuse a path outside the lease")
        policy_file.unlink()
        v.check(hook_write("Assets/_Prototype/Good.cs", "using UnityEngine;\nclass G {}\n") == "deny", "deleting the policy must stop an active owner-policy lease")
        gone = seal()
        v.check(gone.returncode != 0 and "Owner policy" in gone.stderr, "the seal must refuse when the policy is gone")
        write_policy()
        v.check(hook_write("Assets/_Prototype/Good.cs", "using UnityEngine;\nclass G {}\n") == "allow", "restoring the identical policy must restore the lease")

        (lane_dir / "keep.txt").write_text("ok\n", encoding="utf-8")
        (project / ".git" / "info" / "exclude").write_text("ignored.txt\n", encoding="utf-8")
        bad_files: dict[str, str | bytes] = {
            "Bad.cs": "using UnityEditor;\nclass A {}\n",
            "evil.dll": "MZ",
            ".gitignore": "x\n",
            "note.txt": "AKIAABCDEFGHIJKLMNOP\n",
            "ignored.txt": "hidden\n",
            "utf16.cs": "using System;\nclass A {}\n".encode("utf-16"),
            "bom.cs": "\ufeffusing Microsoft.Win32;\nclass B {}\n".encode("utf-8"),
            "pic.png": b"AKIAABCDEFGHIJKLMNOP",
            "split.cs": "class C { void F() { System /* c */ . IO . File . Delete(\"x\"); } }\n",
            "ref.asset": "m_Script: {fileID: 11500000, guid: fedcba9876543210fedcba9876543210, type: 3}\n",
            "quote.cs": "class Q { string s = \"/*\"; void F() { System /* c */ . IO . File . Delete(\"x\"); } }\n",
        }
        for name, content in bad_files.items():
            data = content if isinstance(content, bytes) else content.encode("utf-8")
            (lane_dir / name).write_bytes(data)
            refused = seal()
            v.check(refused.returncode != 0 and "owner-policy seal refused" in refused.stderr, f"the seal must refuse a lane file ({name}): {refused.stderr.strip()}")
            (lane_dir / name).unlink()
        (lane_dir / "A.cs.meta").write_text("fileFormatVersion: 2\nguid: 0123456789abcdef0123456789abcdef\n", encoding="utf-8")
        (lane_dir / "B.cs.meta").write_text("fileFormatVersion: 2\nguid: 0123456789abcdef0123456789abcdef\n", encoding="utf-8")
        duplicate = seal()
        v.check(duplicate.returncode != 0 and "duplicate .meta GUID" in duplicate.stderr, "the seal must refuse duplicate .meta GUIDs")
        (lane_dir / "B.cs.meta").unlink()
        (project / "Assets" / "Other" / "X.cs").write_text("class X {}\n", encoding="utf-8")
        outside = seal()
        v.check(outside.returncode != 0 and "outside lease" in outside.stderr, "the seal must refuse a path outside the lease")
        (project / "Assets" / "Other" / "X.cs").unlink()
        write_policy(max_total_bytes=1999999)
        changed = seal()
        v.check(changed.returncode != 0 and "changed since activation" in changed.stderr, "the seal must refuse a policy changed after activation")
        write_policy()
        (lane_dir / "A.cs").write_text("using UnityEngine;\npublic class A : MonoBehaviour { }\n", encoding="utf-8")
        sealed = seal()
        v.check(sealed.returncode == 0, f"a compliant lane change must seal: {sealed.stderr.strip()}")
        try:
            sealed_lease = json.loads(lease_path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            sealed_lease = {}
        v.check(sealed_lease.get("state") == "SEALED" and sealed_lease.get("authority") == "owner-policy", "the sealed lease must keep its owner-policy authority")


def validate_repository_attestation(v: Validation) -> None:''',
)
edit(
    "scripts/validate_os.py",
    r'''    validate_owner_policy_mode(v)
    validate_repository_attestation(v)
''',
    r'''    validate_owner_policy_mode(v)
    validate_policy_lib(v)
    validate_owner_policy_activation(v)
    validate_repository_attestation(v)
''',
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="Write the changes (default is a dry run)")
    args = parser.parse_args()

    if args.apply and not sys.stdin.isatty():
        print("Refusing --apply without an interactive terminal.")
        return 1

    contents: dict[str, str] = {}
    newlines: dict[str, str] = {}
    problems: list[str] = []
    for relative, old, new in EDITS:
        if relative not in ALLOWED_TARGETS:
            problems.append(f"{relative}: not an allowed target")
            continue
        path = ROOT / relative
        if relative not in contents:
            try:
                text = path.read_bytes().decode("utf-8")
            except OSError as exc:
                problems.append(f"{relative}: cannot read ({exc})")
                continue
            newlines[relative] = "\r\n" if "\r\n" in text else "\n"
            contents[relative] = text
        style = newlines[relative]
        old_n = old.replace("\n", style)
        new_n = new.replace("\n", style)
        count = contents[relative].count(old_n)
        if count != 1:
            problems.append(f"{relative}: expected exactly 1 match, found {count} for: {old.strip().splitlines()[0]}")
            continue
        contents[relative] = contents[relative].replace(old_n, new_n)

    for relative in NEW_FILES:
        if (ROOT / relative).exists():
            problems.append(f"{relative}: already exists")

    if not problems:
        for relative, text in {**contents, **NEW_FILES}.items():
            if relative.endswith(".py"):
                try:
                    compile(text, relative, "exec")
                except SyntaxError as exc:
                    problems.append(f"{relative}: patched file would not compile ({exc})")

    if problems:
        print("NOT APPLIED. Fix these first (the repository may have changed since the proposal):")
        for problem in problems:
            print(f"  - {problem}")
        return 1

    for relative in (*NEW_FILES, *contents):
        print(f"{'WRITE' if args.apply else 'WOULD WRITE'}: {relative}")
    if not args.apply:
        print("Dry run only. Re-run with --apply to write these files.")
        return 0
    for relative, text in NEW_FILES.items():
        (ROOT / relative).write_bytes(text.encode("utf-8"))
    for relative, text in contents.items():
        (ROOT / relative).write_bytes(text.encode("utf-8"))
    print("Applied. Now read `git diff` for these files and run the verification steps in PATCH-B1.md.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
