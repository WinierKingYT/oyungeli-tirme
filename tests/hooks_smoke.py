import json, subprocess, sys
C = "C:/proj"
PUSH = "git " + "push"
def run(hook, payload):
    r = subprocess.run([sys.executable, f".claude/hooks/{hook}"], input=payload, capture_output=True, text=True, timeout=20)
    return r.returncode, r.stdout.strip(), r.stderr.strip()
def dec(out):
    try: return json.loads(out)["hookSpecificOutput"]["permissionDecision"]
    except Exception: return "allow"
cases = [
 ("Write .meta", {"tool_name":"Write","cwd":C,"tool_input":{"file_path":C+"/Assets/Player.cs.meta","content":"x"}}, "deny"),
 ("Edit .prefab (backslash, relative)", {"tool_name":"Edit","cwd":C,"tool_input":{"file_path":"Assets\\P.prefab"}}, "deny"),
 ("Bash push", {"tool_name":"Bash","cwd":C,"tool_input":{"command":PUSH+" origin main"}}, "deny"),
 ("PowerShell chained push", {"tool_name":"PowerShell","cwd":C,"tool_input":{"command":"git add . && "+PUSH}}, "deny"),
 ("Write .cs", {"tool_name":"Write","cwd":C,"tool_input":{"file_path":C+"/Assets/_Project/Scripts/Player.cs","content":"class P{}"}}, "allow"),
 ("git status", {"tool_name":"Bash","cwd":C,"tool_input":{"command":"git status"}}, "allow"),
 ("ProjectSettings .asset", {"tool_name":"Write","cwd":C,"tool_input":{"file_path":C+"/ProjectSettings/ProjectSettings.asset"}}, "deny"),
 ("echo mentioning push (text only)", {"tool_name":"Bash","cwd":C,"tool_input":{"command":"echo \"do not "+PUSH+"\""}}, "allow"),
 ("commit message mentioning push", {"tool_name":"Bash","cwd":C,"tool_input":{"command":"git commit -m \"docs: explain "+PUSH+" policy\""}}, "allow"),
 ("git -C path push", {"tool_name":"Bash","cwd":C,"tool_input":{"command":"git -C \"C:/proj\" "+PUSH.split()[1]}}, "deny"),
 ("push after semicolon", {"tool_name":"Bash","cwd":C,"tool_input":{"command":"git status; "+PUSH}}, "deny"),
 ("Remove-Item Assets", {"tool_name":"PowerShell","cwd":C,"tool_input":{"command":"Remove-Item Assets/Old.cs"}}, "ask"),
 ("Remove-Item -Recurse", {"tool_name":"PowerShell","cwd":C,"tool_input":{"command":"Remove-Item build -Recurse -Force"}}, "deny"),
 ("manifest.json", {"tool_name":"Edit","cwd":C,"tool_input":{"file_path":C+"/Packages/manifest.json"}}, "ask"),
]
fail = 0
for name, ev, exp in cases:
    rc, out, err = run("guard.py", json.dumps(ev))
    got = dec(out); ok = got == exp and rc == 0; fail += not ok
    print("PASS" if ok else "FAIL", "| guard |", name, "->", got)
rc, out, err = run("guard.py", "{not json")
ok = rc == 0 and dec(out) == "allow"; fail += not ok
print("PASS" if ok else "FAIL", "| guard | malformed input -> allow (fail-open), stderr:", err[:80])
for hook, ev in [("after_edit.py", {"hook_event_name":"PostToolUse","tool_name":"Write","cwd":".","tool_input":{"file_path":"Assets/_Project/Scripts/Player.cs"}}),
                 ("after_edit.py", {"hook_event_name":"PostToolUse","tool_name":"Write","cwd":".","tool_input":{"file_path":"README.md"}}),
                 ("session_context.py", {"hook_event_name":"SessionStart","cwd":".","source":"startup"}),
                 ("session_context.py", {"hook_event_name":"PreCompact","cwd":".","trigger":"manual"})]:
    rc, out, err = run(hook, json.dumps(ev)); ok = rc == 0; fail += not ok
    print("PASS" if ok else "FAIL", "|", hook, ev["hook_event_name"], ev["tool_input"]["file_path"] if "tool_input" in ev else "", "rc", rc, "| out:", out[:250].replace("\n", " / "), "| err:", err[:150])
print("FAILURES", fail)
sys.exit(1 if fail else 0)
