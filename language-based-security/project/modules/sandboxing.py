#!/usr/bin/env python3
#credit goes to Emi

import subprocess
import tempfile
import shutil
import signal
import json
import re
import os
import sys

#config
MODEL       = os.getenv("OLLAMA_PREFER_MODEL", "gemma4")
OLLAMA_HOST = os.getenv("OLLAMA_HOST_URL", "http://localhost:11434")
USERNAME    = os.environ.get("USER", "Emi")
HOME        = os.path.expanduser("~")

#colors
def banner():
    print(f"""
    Hal1000
    Local AI Task Agent: {MODEL}
    Commands: 
    'sandbox' 'sb': toggle sandbox
    'quit' 'q' 'exit': exit
""")

#system prompt
SYSTEM_PROMPT = f"""You are HAL, a local AI task agent on an Ubuntu Linux machine.
Help with system tasks: creating directories, installing packages, setting up projects, config files, etc.
The current user is: {USERNAME}  Home directory: /home/{USERNAME}

When given a goal respond with:
1. A brief one-line summary.
2. A JSON block of steps:

```json
[
  {{"description": "What this step does", "command": "shell command"}},
  {{"description": "Verify step", "command": "check command", "verify": true}}
]
```

Rules:
- One command per step. Set "command" to null for conceptual steps.
- CRITICAL: Each command runs in its own isolated subprocess. so things like cd and source never persist.
  - Never use cd standalone. use full absolute paths: mkdir -p /home/{USERNAME}/myproject/src
  - Chain with &&: cd /home/{USERNAME}/myproject && cargo build
  - Never "source venv/bin/activate". always call binaries directly:
      /home/{USERNAME}/myproject/env/bin/pip install pandas
  - Create venv and install in one step:
      python3 -m venv /home/{USERNAME}/myproject/env && /home/{USERNAME}/myproject/env/bin/pip install pandas
- VERIFICATION IS MANDATORY. Every plan MUST include verify steps marked with "verify": true.
  After EVERY mkdir, file write, package install, git clone always add a verify step.
  A failed verify step stops the entire plan immediately.
  Example:
  [{{"description": "Create dir", "command": "mkdir -p /home/{USERNAME}/proj"}},
   {{"description": "Verify dir", "command": "ls -la /home/{USERNAME}/proj", "verify": true}},
   {{"description": "Install serde", "command": "cd /home/{USERNAME}/proj && cargo add serde"}},
   {{"description": "Verify Cargo.toml", "command": "grep serde /home/{USERNAME}/proj/Cargo.toml", "verify": true}}]
- WRITING FILES: Use brace grouping for reports:
    {{ echo "# Report"; lscpu; free -h; df -h; }} > /home/{USERNAME}/report.md
  Use tee+heredoc for static files:
    tee /home/{USERNAME}/README.md << 'EOF'
    # Title
    Content
    EOF
  Never chain echo with a single redirect. Never use python3 -c with multi-line strings.
- Prefer apt and standard Unix tools. Avoid sudo unless essential.
- After results: brief summary + next steps. Be concise."""

# predefine of system commands
SYSTEM_CMDS = [
    'apt', 'apt-get', 'dpkg', 'snap', 'flatpak',
    'pacman', 'yay', 'paru', 'dnf', 'yum', 'zypper',
    'apk'
]

#sandbox
class Sandbox:
    def __init__(self):
        self.active      = False
        self.session_dir = None
        self.upper_dir   = None
        self.work_dir    = None
        self.pcap_path   = None
        self._tcpdump    = None

    def start(self):
        self.session_dir = tempfile.mkdtemp(prefix="hal-sandbox-")
        self.upper_dir   = os.path.join(self.session_dir, "upper")
        self.work_dir    = os.path.join(self.session_dir, "work")
        self.pcap_path   = os.path.join(self.session_dir, "network.pcap")
        os.makedirs(self.upper_dir)
        os.makedirs(self.work_dir)
        try:
            # Test if tcpdump works without sudo first
            test = subprocess.run(
                ["tcpdump", "-i", "any", "-c", "1", "-w", "/dev/null"],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=2
            )
            if test.returncode == 0:
                self._tcpdump = subprocess.Popen(
                    ["tcpdump", "-i", "any", "-w", self.pcap_path, "-q"],
                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
                )
            else:
                self._tcpdump = None
                print("\ntcpdump error can't start. likely permisions (debug msg)")
        except Exception:
            self._tcpdump = None
        self.active = True
        print(f"\nSandbox ON: bwrap container active, network being logged.")
        print(f"Session dir: {self.session_dir}\n")

    def stop(self):
        if self._tcpdump:
            try:
                self._tcpdump.send_signal(signal.SIGTERM)
                self._tcpdump.wait(timeout=3)
            except Exception:
                pass
            self._tcpdump = None
        self.active = False

    def cleanup(self):
        self.stop()
        if self.session_dir and os.path.exists(self.session_dir):
            shutil.rmtree(self.session_dir, ignore_errors=True)
        self.session_dir = None

    def wrap_command(self, command):
        home_upper = os.path.join(self.upper_dir, "home", USERNAME)
        home_work  = os.path.join(self.work_dir,  "home", USERNAME)
        os.makedirs(home_upper, exist_ok=True)
        os.makedirs(home_work,  exist_ok=True)
        return [
            "bwrap",
            "--ro-bind", "/", "/",
            "--bind", home_upper, HOME,
            "--proc", "/proc",
            "--dev", "/dev",
            "--tmpfs", "/tmp",
            "--unshare-pid",
            "--die-with-parent",
            "--cap-add", "cap_net_raw",     #remove these to stop raw sockets in the container
            "--cap-add", "cap_net_admin",   #
            "--",
            "bash", "-c", command
        ]

    def changed_files(self):
        changed = []
        for root, dirs, files in os.walk(self.upper_dir):
            for f in files:
                full = os.path.join(root, f)
                rel  = os.path.relpath(full, self.upper_dir)
                changed.append(("/" + rel, full))
        return changed

    def review(self, last_steps):
        """Show what changed, ask whether to commit or discard."""
        changed = self.changed_files()
        pcap_ok = (self.pcap_path and os.path.exists(self.pcap_path)
                   and os.path.getsize(self.pcap_path) > 0)

        print(f"\nSandbox session ended.")
        print(f"{len(changed)} file(s) modified in sandbox:")
        for real, _ in changed:
            print(f"  {real}")

        if pcap_ok:
            print(f"\nNetwork log: {self.pcap_path}")
            print(f"Open with:   wireshark {self.pcap_path}")

        if changed:
            print(f"\nSandbox dir: {self.upper_dir}")
            print(f"Browse with: nautilus {self.upper_dir}")

        if not changed or not last_steps:
            print(f"\nNothing to commit.")
            self.cleanup()
            return None

        print(f"\nWhat do you want to do?")
        print(f"[C] Commit: replay steps on your real system")
        print(f"[D] Discard: throw away sandbox, keep real system untouched")
        if pcap_ok:
            print(f"[W] Open network log in Wireshark then decide")

        while True:
            choice = input(f"\n> ").strip().lower()
            if choice in ('c', 'commit'):
                self.cleanup()
                return last_steps  # caller will re-execute on real system
            elif choice in ('d', 'discard'):
                self.cleanup()
                print(f"Discarded. Your real system is unchanged.")
                return None
            elif choice in ('w',) and pcap_ok:
                subprocess.Popen(
                    ["wireshark", self.pcap_path],
                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                    start_new_session=True
                )
                print(f"Wireshark opened. Enter C to commit or D to discard when ready.")
            else:
                print(f"Enter C, D{', or W' if pcap_ok else ''}")

#ollama
def ask_ollama(messages):
    import urllib.request
    payload = json.dumps({
        "model": MODEL,
        "messages": messages,
        "stream": False
    }).encode()
    req = urllib.request.Request(
        f"{OLLAMA_HOST}/api/chat",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    with urllib.request.urlopen(req, timeout=120) as resp:
        return json.loads(resp.read())["message"]["content"].strip()

#step parsing
def parse_steps(response):
    patterns = [
        r'```json\s*(\[.*?\])\s*```',
        r'```\s*(\[.*?\])\s*```',
        r'(\[\s*\{[^\]]*description[^\]]*\}\s*\])',
        r'(\[\s*\{.*?\}\s*\])',
    ]
    for pattern in patterns:
        m = re.search(pattern, response, re.DOTALL)
        if m:
            try:
                data = json.loads(m.group(1))
                if isinstance(data, list) and data and isinstance(data[0], dict):
                    return data
            except Exception:
                pass
    return []

#command execution
GUI_APPS = [
    'steam', 'firefox', 'chrome', 'chromium', 'code', 'kate', 'gedit',
    'nautilus', 'dolphin', 'thunar', 'vlc', 'mpv', 'gimp', 'inkscape',
    'blender', 'discord', 'slack', 'spotify', 'obs', 'thunderbird',
    'libreoffice', 'xterm', 'konsole', 'gnome-terminal', 'alacritty', 'kitty',
]

SYSTEM_CMDS = ['apt', 'apt-get', 'dpkg', 'snap', 'flatpak']

def is_system_cmd(cmd):
    cmd_str = cmd.strip().lower()

    if 'sudo ' in cmd_str or 'su ' in cmd_str:
        return True

    sub_cmds = re.split(r'&&|\|\||;', cmd_str)
    for sub in sub_cmds:
        parts = sub.strip().split()
        if parts and parts[0] in SYSTEM_CMDS:
            return True

    return False

def is_gui_app(cmd):
    return any(app in cmd.lower() for app in GUI_APPS)

def run_command(command, sandbox=None):
    env = os.environ.copy()
    if is_gui_app(command):
        subprocess.Popen(
            command, shell=True, env=env,
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            start_new_session=True, cwd=HOME
        )
        return 0, "Launched in background.", ""
    if sandbox and sandbox.active:
        result = subprocess.run(
            sandbox.wrap_command(command),
            text=True, capture_output=True, env=env, cwd=HOME,
            stdin=subprocess.DEVNULL
        )
    else:
        result = subprocess.run(
            command, shell=True, text=True,
            capture_output=True, env=env, cwd=HOME
        )
    return result.returncode, result.stdout, result.stderr

#plan UI
def show_plan(steps, sandbox_active):
    tag = " [SANDBOX]" if sandbox_active else ""
    print(f"\n--- Proposed Plan{tag} ---------")
    for i, s in enumerate(steps, 1):
        verify_tag = f" [verify]" if s.get("verify") else ""
        print(f"\n  {i}. {s.get('description','')}{verify_tag}")
        if s.get("command"):
            print(f"     $ {s['command']}")
    print(f"\n--------------------------------")
    print(f"\nRun all? [Y]es  [S]tep-by-step  [N]o\n")
    while True:
        c = input(f"> ").strip().lower()
        if c in ('y', 'yes', ''): return 'all'
        if c in ('s', 'step'):    return 'step'
        if c in ('n', 'no'):      return 'no'

def execute_steps(steps, mode = 'all', sandbox=None):
    results = []
    skipped_sys_cmd = False

    for i, step in enumerate(steps, 1):
        cmd       = step.get("command")
        desc      = step.get("description", "")
        is_verify = step.get("verify", False)

        if not cmd:
            print(f"\n  {i}. {desc} no command, skipped.")
            results.append(f"Step {i}: skipped.")
            continue

        if mode == 'step':
            print(f"\n{i}. {desc}")
            print(f"$ {cmd}")
            print(f"\n[Y] Run  [N] Skip  [Q] Quit\n")
            c = input(f"> ").strip().lower()
            if c in ('q', 'quit'):
                print(f"\nStopped.")
                results.append("Plan stopped by user.")
                break
            if c in ('n', 'no'):
                results.append(f"Step {i}: skipped.")
                continue
            pass

        # Warn about system commands in sandbox mode
        if sandbox and sandbox.active and is_system_cmd(cmd):
            # print(f"\nSANDBOX WARNING: This command touches"
            #       f"the real system even in sandbox mode:")
            # print(f"$ {cmd}")
            # print(f"Run on real system anyway?"
            #       f"[Y] Yes [N] Skip\n")
            # c = input(f"> ").strip().lower()
            # if c not in ('y', 'yes'):
            #     results.append(f"Step {i} ({desc}): skipped (system cmd in sandbox).")
            #     continue
            results.append(f"Step {i} ({desc}): [SKIPPED] System command.")
            skipped_sys_cmd = True
            continue

        prefix = ""
        print(f"\n  {prefix}$ {cmd}")
        code, out, err = run_command(cmd, sandbox)

        if code == 0:
            print(f"Done")
            if out.strip():
                print(f"{out.strip()[:300]}")
            results.append(f"Step {i} ({desc}): OK\n{out[:400]}")
        else:
            print(f"Failed (exit {code})")
            if sandbox and sandbox.active and skipped_sys_cmd:
                print(f"  -> Auto-skipped failure (expected missing dependency in sandbox).")
                results.append(f"Step {i} ({desc}): [AUTO-SKIPPED] Failed (Expected due to skipped system command).")
                continue

            if err.strip():
                print(f"{err.strip()[:300]}")
            results.append(f"Step {i} ({desc}): FAILED\n{err[:400]}")

            if is_verify:
                if skipped_sys_cmd:
                    results.append("Plan stopped: Verification failed (Expected: System commands were safely skipped in sandbox).")
                else:
                    print(f"\nVerification failed. stopping plan.")
                    results.append("Plan stopped: verification failed.")
                break
            else:
                # print(f"\nContinue anyway? [Y]/[N]\n")
                # c = input(f"> ").strip().lower()
                # if c not in ('y', 'yes'):
                #     results.append("Plan stopped by user after failure.")
                #     break
                results.append("Plan stopped on failure.")
                break

    return results

#main loop
def main():
    banner()

    import urllib.request
    print(f"Connecting to Ollama ({MODEL})...", end="", flush=True)
    try:
        urllib.request.urlopen(f"{OLLAMA_HOST}/api/tags", timeout=5)
        print(f"\nConnected to Ollama")
    except Exception:
        print(f"Cannot reach Ollama")
        sys.exit(1)

    conversation = [{"role": "system", "content": SYSTEM_PROMPT}]
    sandbox      = Sandbox()
    last_steps   = []

    while True:
        mode_tag = f" [SANDBOX]" if sandbox.active else ""
        try:
            goal = input(f"HAL{mode_tag}> ").strip()
        except (KeyboardInterrupt, EOFError):
            print(f"\nGoodbye.")
            sandbox.cleanup()
            break

        if not goal:
            continue

        if goal.lower() in ('quit', 'exit', 'q'):
            print(f"Goodbye.")
            sandbox.cleanup()
            break

        # Sandbox toggle
        if goal.lower() in ('sandbox', 'sb'):
            if not sandbox.active:
                sandbox.start()
            else:
                to_commit = sandbox.review(last_steps)
                if to_commit:
                    print(f"\nCommitting to real system")
                    results = execute_steps(to_commit, 'all', sandbox=None)
                    conversation.append({
                        "role": "user",
                        "content": f"Committed to real system. Results:\n{results}\n\nBrief summary?"
                    })
                    try:
                        followup = ask_ollama(conversation)
                        conversation.append({"role": "assistant", "content": followup})
                        clean = re.sub(r'```json.*?```', '', followup, flags=re.DOTALL).strip()
                        print(f"\nHAL: {clean}\n")
                    except Exception:
                        pass
                last_steps = []
            continue

        conversation.append({"role": "user", "content": goal})
        print(f"\nThinking...", flush=True)

        try:
            response = ask_ollama(conversation)
        except Exception as e:
            print(f"Error: {e}")
            continue

        conversation.append({"role": "assistant", "content": response})
        steps = parse_steps(response)

        summary = re.sub(r'```json.*?```', '', response, flags=re.DOTALL).strip()
        if summary:
            print(f"\nHAL: {summary}")

        if not steps:
            #print(f"\nNo plan found. Raw output:")
            #print(f"{response[:600]}\n")
            continue

        decision = show_plan(steps, sandbox.active)

        if decision == 'no':
            print(f"\nCancelled.\n")
            conversation.append({"role": "user", "content": "User cancelled."})
            continue

        last_steps = steps
        sb = sandbox if sandbox.active else None
        results = execute_steps(steps, decision, sandbox=sb)

        # If sandbox was active, offer review
        if sandbox.active:
            to_commit = sandbox.review(last_steps)
            if to_commit:
                print(f"\nCommitting to real system")
                results = execute_steps(to_commit, 'all', sandbox=None)
                last_steps = []

        conversation.append({
            "role": "user",
            "content": f"Results:\n{results}\n\nBrief summary + next steps?"
        })
        print(f"\nAnalysing...", flush=True)
        try:
            followup = ask_ollama(conversation)
            conversation.append({"role": "assistant", "content": followup})
            clean = re.sub(r'```json.*?```', '', followup, flags=re.DOTALL).strip()
            print(f"\nHAL: {clean}\n")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    main()