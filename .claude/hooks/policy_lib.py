"""Owner-policy checks shared by the hooks and the lease scripts. Standard library only."""

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
