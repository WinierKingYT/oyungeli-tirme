#!/usr/bin/env python3
"""Gate shell commands and prevent agents from changing their own authority."""

from __future__ import annotations

import fnmatch
import os
import re
import shlex
from pathlib import PurePath

from common import emit_decision, load_lease, project_root, read_hook_input, run_fail_closed


CONTROL_OPERATORS = ("\n", "\r", "&&", "||", "|&", "|", ";", ">", "<", "`", "$(", "&")
OPAQUE_SHELLS = {"bash", "sh", "zsh", "fish", "cmd", "cmd.exe", "powershell", "powershell.exe", "pwsh", "pwsh.exe"}
DESTRUCTIVE_PROGRAMS = {"rm", "rmdir", "del", "erase", "remove-item"}
PUBLISH_PROGRAMS = {"npm", "docker", "kubectl", "terraform", "helm"}
SAFE_SIMPLE_PROGRAMS = {
    "pwd", "ls", "dir", "get-childitem", "cat", "head", "tail", "type",
    "get-content", "rg", "grep", "select-string", "wc", "stat", "file",
    "which", "where", "get-command", "du",
}
SAFE_GIT_SUBCOMMANDS = {"status", "diff", "log", "show", "rev-parse", "ls-files"}
UNSAFE_GIT_OPTIONS = {"--output", "--ext-diff", "--textconv", "--exec-path"}
SENSITIVE_REFERENCE = re.compile(
    r"(?:^|[/\\\s])(?:\.env(?:\.|$)|secrets?(?:[/\\]|$)|[^\s/\\]+\.(?:pem|key)(?:\s|$)|id_rsa(?:\s|$))",
    re.IGNORECASE,
)


def has_control_operator(command: str) -> bool:
    return any(token in command for token in CONTROL_OPERATORS)


def split_command(command: str) -> list[str]:
    try:
        return shlex.split(command, posix=os.name != "nt")
    except ValueError:
        return []


def basename(token: str) -> str:
    return PurePath(token.replace("\\", "/")).name.lower()


def strip_env_prefix(tokens: list[str]) -> list[str]:
    result = list(tokens)
    if result and basename(result[0]) in {"env", "env.exe"}:
        result.pop(0)
    while result and re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*=.*", result[0]):
        result.pop(0)
    return result


def git_subcommand(tokens: list[str]) -> tuple[str | None, list[str]]:
    tokens = strip_env_prefix(tokens)
    if not tokens or basename(tokens[0]) not in {"git", "git.exe"}:
        return None, []
    index = 1
    while index < len(tokens):
        token = tokens[index]
        if token in {"-C", "-c", "--git-dir", "--work-tree", "--namespace"}:
            index += 2
            continue
        if token.startswith(("--git-dir=", "--work-tree=", "--namespace=", "-c")):
            index += 1
            continue
        if token.startswith("-"):
            index += 1
            continue
        return token.lower(), tokens[index + 1 :]
    return None, []


def forbidden(command: str, tokens: list[str]) -> str | None:
    lowered = command.lower().replace("\\", "/")
    if SENSITIVE_REFERENCE.search(command):
        return "Shell access to a sensitive path is forbidden"
    if re.search(r"(?:^|[\s;&|])(?:\S*/)?(?:rm|rmdir|del|erase|remove-item)\s+", lowered):
        return "Destructive filesystem command is forbidden anywhere in a compound command"
    if re.search(
        r"(?:^|[\s;&|])(?:\S*/)?git(?:\.exe)?(?:\s+(?:-c|-C)\s+\S+)*\s+['\"]?(?:push|clean|rebase|merge|commit|tag)\b",
        command,
        flags=re.IGNORECASE,
    ):
        return "History-changing or publishing Git command is forbidden anywhere in a compound command"
    if re.search(r"(?:npm\s+publish|docker\s+push|kubectl\s+apply|terraform\s+apply|helm\s+upgrade)\b", lowered):
        return "Publish/deploy command is forbidden anywhere in a compound command"
    if ".ai-governance/" in lowered or ".claude/hooks/" in lowered or ".claude/settings.json" in lowered:
        return "Governance control-plane access is forbidden"
    if any(name in lowered for name in ("activate_lease.py", "deactivate_lease.py", "seal_implementation.py")):
        return "Agents cannot activate, deactivate, or seal implementation authority"

    stripped = strip_env_prefix(tokens)
    program = basename(stripped[0]) if stripped else ""
    if program in OPAQUE_SHELLS and any(
        flag.lower() in {"-c", "-command", "/c"} for flag in stripped[1:]
    ):
        return "Opaque nested shell execution is forbidden"
    if program in DESTRUCTIVE_PROGRAMS:
        return "Destructive filesystem command is forbidden"
    if program in {"python", "python3", "python.exe", "py", "node", "node.exe"}:
        joined = " ".join(stripped[1:]).lower()
        if any(name in joined for name in ("activate_lease.py", "deactivate_lease.py", "seal_implementation.py")):
            return "Agents cannot invoke lease-control scripts"

    subcommand, arguments = git_subcommand(tokens)
    lowered_arguments = [arg.lower() for arg in arguments]
    if any(
        arg in UNSAFE_GIT_OPTIONS or any(arg.startswith(option + "=") for option in UNSAFE_GIT_OPTIONS)
        for arg in lowered_arguments
    ):
        return "Git output or external-execution option is forbidden"
    if subcommand in {"push", "clean", "rebase", "merge", "commit", "tag"}:
        return f"Git {subcommand} requires explicit human operation outside the agent"
    if subcommand == "reset" and any(arg.lower() == "--hard" for arg in arguments):
        return "git reset --hard is forbidden"
    if subcommand in {"checkout", "restore"} and "--" in arguments:
        return f"git {subcommand} -- is forbidden"
    if subcommand == "branch" and any(arg.lower() in {"-d", "--delete"} for arg in arguments):
        return "Git branch deletion is forbidden"

    if program in PUBLISH_PROGRAMS:
        action = stripped[1].lower() if len(stripped) > 1 else ""
        if (program, action) in {
            ("npm", "publish"), ("docker", "push"), ("kubectl", "apply"),
            ("terraform", "apply"), ("helm", "upgrade"),
        }:
            return "Publish/deploy command requires explicit human authorization"
    return None


def read_only(tokens: list[str], command: str) -> bool:
    if not tokens or has_control_operator(command):
        return False
    if basename(tokens[0]) in {"env", "env.exe"} or any(
        re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*=.*", token) for token in tokens[:-1]
    ):
        return False
    stripped = strip_env_prefix(tokens)
    if not stripped:
        return False
    program = basename(stripped[0])
    for token in stripped[1:]:
        normalized = token.replace("\\", "/")
        if normalized.startswith(("/", "~/", "../")) or "/../" in normalized or re.match(r"^[A-Za-z]:", normalized):
            return False
    if program in {"python", "python3", "python.exe", "py"}:
        args = [item.replace("\\", "/") for item in stripped[1:]]
        if args and args[0] == "scripts/validate_os.py":
            return len(args) == 1
        if args and args[0] == "scripts/doctor.py":
            return len(args) == 1 or args[1:] == ["--require-claude"]
        if args and args[0] in {"scripts/task_digest.py", "scripts/artifact_digest.py"}:
            return len(args) == 2 and not args[1].startswith("-")
    if program in SAFE_SIMPLE_PROGRAMS:
        return True
    subcommand, arguments = git_subcommand(tokens)
    if subcommand not in SAFE_GIT_SUBCOMMANDS:
        return False
    if any(token in {"-C", "-c", "--git-dir", "--work-tree"} or token.startswith(("--git-dir=", "--work-tree=", "-c")) for token in tokens[1:]):
        return False
    lowered_args = [arg.lower() for arg in arguments]
    if any(
        arg in UNSAFE_GIT_OPTIONS or any(arg.startswith(option + "=") for option in UNSAFE_GIT_OPTIONS)
        for arg in lowered_args
    ):
        return False
    return True


def main() -> None:
    data = read_hook_input()
    command = data.get("tool_input", {}).get("command")
    if not isinstance(command, str) or not command.strip():
        emit_decision(data, "deny", "Shell command is missing; fail closed")
        return
    normalized = command.strip()
    tokens = split_command(normalized)
    if not tokens:
        emit_decision(data, "deny", "Shell command could not be parsed safely")
        return

    denial = forbidden(normalized, tokens)
    if denial:
        emit_decision(data, "deny", denial)
        return

    if read_only(tokens, normalized):
        emit_decision(data, "allow", "Recognized simple read-only inspection command")
        return

    lease, reason = load_lease(project_root())
    if not lease:
        emit_decision(
            data,
            "deny",
            f"LEASE_REQUIRED: non-read-only shell command blocked. {reason}",
            "Use simple read-only inspection or ask the human to activate an approved task lease.",
        )
        return

    if has_control_operator(normalized):
        emit_decision(
            data,
            "ask",
            f"Compound, redirected, piped, or substituted commands are never auto-approved by task {lease['task_id']}",
            "Review every subcommand, redirection target, and expansion before one-time approval.",
        )
        return

    if any(fnmatch.fnmatchcase(normalized, pattern) for pattern in lease["allowed_commands"]):
        emit_decision(data, "allow", f"Simple command is authorized by active task {lease['task_id']}")
        return

    emit_decision(
        data,
        "ask",
        f"Command is not pre-authorized by task {lease['task_id']}",
        "Review the full command and its blast radius before approving one-time execution.",
    )


if __name__ == "__main__":
    run_fail_closed(main)
