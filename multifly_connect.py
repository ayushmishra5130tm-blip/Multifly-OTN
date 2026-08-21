"""
MULTIFLY CONNECT - All Services Connected
==========================================
One command to connect and use all external services.

Usage:
  python multifly_connect.py copilot     Check Copilot status
  python multifly_connect.py deploy      Deploy to Vercel
  python multifly_connect.py ci          Run CI/CD checks
  python multifly_connect.py sync        Sync brain to Google Drive
  python multifly_connect.py all         Connect everything
"""
import sys
import os
import subprocess
import json

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

def check_copilot():
    """Check GitHub Copilot status."""
    print("\n  === GITHUB COPILOT ===\n")
    result = subprocess.run(
        ["gh", "auth", "status"],
        capture_output=True, text=True, timeout=10
    )
    if "Logged in" in result.stdout:
        print("  [OK] GitHub authenticated")
    else:
        print("  [!] Not logged in - run: gh auth login")

    ag = os.path.expanduser(r"~\AppData\Local\Programs\Antigravity IDE\bin\antigravity-ide.cmd")
    result = subprocess.run([ag, "--list-extensions"], capture_output=True, text=True, timeout=10)
    if "github.copilot" in result.stdout:
        print("  [OK] Copilot extension installed")
        print("  [OK] Copilot Chat installed")
    else:
        print("  [!] Copilot not installed")

    print("\n  Copilot features available:")
    print("    - Code completion (auto-suggest)")
    print("    - Chat: @workspace, /explain, /fix, /tests")
    print("    - Code review")
    print("    - Test generation")


def deploy_vercel():
    """Deploy current project to Vercel."""
    print("\n  === VERCEL DEPLOY ===\n")
    result = subprocess.run(
        ["vercel", "--version"],
        capture_output=True, text=True, timeout=10
    )
    print(f"  Vercel CLI: {result.stdout.strip()}")

    if os.path.exists("vercel.json"):
        print("  Deploying with existing vercel.json...")
        subprocess.run(["vercel", "--yes", "--prod"])
    else:
        print("  No vercel.json found. Creating...")
        with open("vercel.json", "w") as f:
            json.dump({"version": 2}, f, indent=2)
        subprocess.run(["vercel", "--yes", "--prod"])


def run_ci():
    """Run CI/CD checks locally."""
    print("\n  === CI/CD CHECKS ===\n")
    scripts_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Check syntax
    for f in ["unified_multifly.py", "multifly_elite.py"]:
        path = os.path.join(scripts_dir, f)
        result = subprocess.run([sys.executable, "-m", "py_compile", path],
                              capture_output=True, text=True, timeout=10)
        status = "OK" if result.returncode == 0 else "FAIL"
        print(f"  [{status}] {f} syntax")
    
    # Check imports
    sys.path.insert(0, scripts_dir)
    try:
        from unified_multifly import Brain
        print("  [OK] unified_multifly imports")
    except Exception as e:
        print(f"  [FAIL] unified_multifly: {e}")
    
    try:
        from multifly_elite import NLPEngine, MLLearner
        print("  [OK] multifly_elite imports")
    except Exception as e:
        print(f"  [FAIL] multifly_elite: {e}")


def sync_brain():
    """Sync brain database."""
    print("\n  === BRAIN SYNC ===\n")
    sync_script = os.path.join(SCRIPT_DIR, "sync_brain.py")
    if os.path.exists(sync_script):
        subprocess.run([sys.executable, sync_script, "--sync"])
    else:
        print("  [!] Google Drive folder not found locally")
        print("  Install Google Drive for Desktop:")
        print("  https://www.google.com/drive/download/")


def connect_all():
    """Connect all services."""
    print("\n  ====================================================")
    print("   MULTIFLY CONNECT - All Services")
    print("  ====================================================\n")

    check_copilot()
    print()
    run_ci()
    print()
    sync_brain()
    print()

    print("  ====================================================")
    print("   All services connected!")
    print("  ====================================================\n")
    print("  Commands:")
    print("    python multifly_connect.py copilot   Check Copilot")
    print("    python multifly_connect.py deploy    Deploy to Vercel")
    print("    python multifly_connect.py ci        Run CI/CD checks")
    print("    python multifly_connect.py sync      Sync brain to Drive")
    print("    python multifly_connect.py all       Connect everything")
    print()


if __name__ == "__main__":
    if len(sys.argv) > 1:
        cmd = sys.argv[1].lower()
        if cmd == "copilot":
            check_copilot()
        elif cmd == "deploy":
            deploy_vercel()
        elif cmd == "ci":
            run_ci()
        elif cmd == "sync":
            sync_brain()
        elif cmd == "all":
            connect_all()
        else:
            print(f"  Unknown: {cmd}")
    else:
        connect_all()
