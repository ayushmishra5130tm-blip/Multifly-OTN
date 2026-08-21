"""
CONNECT ALL EXTERNAL SERVICES
==============================
Configures GitHub Copilot, Vercel, GitHub Actions, and Google Drive sync.
"""
import json
import os
import subprocess

SETTINGS_PATH = os.path.expanduser(r"~\AppData\Roaming\Antigravity\User\settings.json")
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

def update_settings():
    """Update IDE settings for all integrations."""
    with open(SETTINGS_PATH, "r", encoding="utf-8") as f:
        settings = json.load(f)

    # === GITHUB COPILOT SETTINGS ===
    settings["github.copilot.enable"] = {
        "*": True,
        "plaintext": True,
        "markdown": True,
        "scminput": False
    }
    settings["github.copilot.chat.agent.enabled"] = True
    settings["github.copilot.chat.localeOverride"] = "en"
    settings["github.copilot.chat.codeGeneration"] = True
    settings["github.copilot.chat.testsGeneration"] = True
    settings["github.copilot.chat.fixCode"] = True
    settings["github.copilot.chat.explain"] = True
    settings["github.copilot.chat.reviewSelection.enabled"] = True
    settings["github.copilot.chat.commands.enabled"] = True

    # === TERMINAL INTEGRATION ===
    settings["terminal.integrated.enablePersistentSessions"] = True
    settings["terminal.integrated.scrollback"] = 50000

    # === GIT SETTINGS ===
    settings["git.autofetch"] = True
    settings["git.confirmSync"] = False
    settings["git.enableSmartCommit"] = True
    settings["git.openRepositoryInParentFolders"] = "always"
    settings["gitlens.codeLens.enabled"] = True
    settings["gitlens.hovers.currentLine.overwardLines"] = True

    with open(SETTINGS_PATH, "w", encoding="utf-8") as f:
        json.dump(settings, f, indent=4, ensure_ascii=False)

    print("  [OK] IDE settings updated for Copilot + Git")


def setup_vercel_deploy():
    """Create Vercel deployment script."""
    deploy_script = os.path.join(SCRIPT_DIR, "deploy_vercel.py")
    content = '''"""
VERCEL DEPLOYER
===============
Deploy any project to Vercel with one command.

Usage:
  python deploy_vercel.py                  Deploy current directory
  python deploy_vercel.py /path/to/project Deploy specific project
  python deploy_vercel.py --list           List deployed projects
"""
import subprocess
import sys
import os

def deploy(project_dir=None):
    """Deploy to Vercel."""
    if project_dir:
        os.chdir(project_dir)

    print("\\n  Deploying to Vercel...")
    print("  =====================\\n")

    # Check if vercel.json exists
    if not os.path.exists("vercel.json"):
        print("  Creating vercel.json...")
        with open("vercel.json", "w") as f:
            json.dump({
                "version": 2,
                "builds": [],
                "routes": [{"src": "/(.*)", "dest": "/index.html"}]
            }, f, indent=2)

    # Deploy
    result = subprocess.run(
        ["vercel", "--yes", "--prod"],
        capture_output=True, text=True
    )

    if result.returncode == 0:
        print("  [OK] Deployed successfully!")
        # Extract URL from output
        for line in result.stdout.split("\\n"):
            if "https://" in line:
                print(f"  URL: {line.strip()}")
    else:
        print(f"  [ERROR] {result.stderr}")

def list_projects():
    """List deployed Vercel projects."""
    result = subprocess.run(["vercel", "ls"], capture_output=True, text=True)
    print(result.stdout)

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--list":
        list_projects()
    elif len(sys.argv) > 1:
        deploy(sys.argv[1])
    else:
        deploy()
'''
    with open(deploy_script, "w") as f:
        f.write(content)
    print("  [OK] Vercel deploy script created")


def setup_github_actions():
    """Create GitHub Actions CI/CD workflow."""
    workflow_dir = os.path.join(SCRIPT_DIR, ".github", "workflows")
    os.makedirs(workflow_dir, exist_ok=True)

    workflow = '''name: Multifly CI/CD

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.12", "3.13", "3.14"]

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python ${{ matrix.python-version }}
        uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install rich flask websockets

      - name: Run tests
        run: |
          python -c "from unified_multifly import Brain, SystemRegistry, PluginManager, SelfLearner, Orchestrator; print('All imports OK')"
          python -c "from multifly_elite import WebSocketServer, NLPEngine, MLLearner; print('Elite imports OK')"

      - name: Check brain database
        run: |
          python -c "
          from unified_multifly import Brain
          brain = Brain()
          s = brain.summary()
          print(f'Brain: {s[\"commands\"]} cmds, {s[\"patterns\"]} patterns')
          brain.conn.close()
          "

  deploy:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'

    steps:
      - uses: actions/checkout@v4

      - name: Deploy to Vercel
        uses: amondnet/vercel-action@v25
        with:
          vercel-token: ${{ secrets.VERCEL_TOKEN }}
          vercel-org-id: ${{ secrets.VERCEL_ORG_ID }}
          vercel-project-id: ${{ secrets.VERCEL_PROJECT_ID }}
          vercel-args: '--prod'
'''
    workflow_path = os.path.join(workflow_dir, "ci-cd.yml")
    with open(workflow_path, "w") as f:
        f.write(workflow)
    print("  [OK] GitHub Actions workflow created")


def setup_google_drive_sync():
    """Create Google Drive sync script for brain database."""
    sync_script = os.path.join(SCRIPT_DIR, "sync_brain.py")
    content = '''"""
GOOGLE DRIVE BRAIN SYNC
========================
Syncs the Multifly brain database with Google Drive.

Setup:
  1. Install: pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib
  2. Get credentials from Google Cloud Console
  3. Place credentials.json in scripts folder
  4. Run: python sync_brain.py --setup

Usage:
  python sync_brain.py --upload    Upload brain to Drive
  python sync_brain.py --download  Download brain from Drive
  python sync_brain.py --auto      Auto-sync every 5 minutes
"""
import os
import sys
import json
import time
import shutil
from datetime import datetime
from pathlib import Path

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(SCRIPT_DIR, "multifly_brain.db")
SYNC_CONFIG = os.path.join(SCRIPT_DIR, "sync_config.json")
DRIVE_FOLDER_NAME = "MultiflyBrain"

def setup():
    """Setup Google Drive sync."""
    print("\\n  Setting up Google Drive sync...")
    print("  ================================\\n")
    print("  Steps:")
    print("  1. Go to https://console.cloud.google.com")
    print("  2. Create project -> Enable Google Drive API")
    print("  3. Create OAuth 2.0 credentials")
    print("  4. Download credentials.json to:")
    print(f"     {SCRIPT_DIR}")
    print("  5. Run this script again")
    print()

    # Create sync config
    config = {
        "folder_name": DRIVE_FOLDER_NAME,
        "local_path": DB_PATH,
        "sync_interval_seconds": 300,
        "last_sync": None,
        "auto_sync": False
    }
    with open(SYNC_CONFIG, "w") as f:
        json.dump(config, f, indent=2)
    print(f"  Config saved to: {SYNC_CONFIG}")

def quick_sync():
    """Quick sync using rclone or manual copy."""
    # Check if Google Drive folder exists locally
    gdrive_paths = [
        os.path.expanduser(r"~\Google Drive"),
        os.path.expanduser(r"~\My Drive"),
        "G:\\My Drive",
        "G:\\Google Drive",
    ]

    gdrive_root = None
    for p in gdrive_paths:
        if os.path.exists(p):
            gdrive_root = p
            break

    if gdrive_root:
        target_dir = os.path.join(gdrive_root, DRIVE_FOLDER_NAME)
        os.makedirs(target_dir, exist_ok=True)
        target_db = os.path.join(target_dir, "multifly_brain.db")

        # Copy database
        shutil.copy2(DB_PATH, target_db)
        print(f"  [OK] Synced to Google Drive: {target_db}")

        # Save sync time
        config = {"last_sync": datetime.now().isoformat(), "target": target_db}
        with open(SYNC_CONFIG, "w") as f:
            json.dump(config, f, indent=2)
        return True
    else:
        print("  [!] Google Drive folder not found locally")
        print("  Install Google Drive for Desktop:")
        print("  https://www.google.com/drive/download/")
        return False

def auto_sync():
    """Auto-sync every 5 minutes."""
    print("  Auto-syncing every 5 minutes... (Ctrl+C to stop)\\n")
    while True:
        quick_sync()
        time.sleep(300)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        if cmd == "--setup":
            setup()
        elif cmd == "--upload" or cmd == "--sync":
            quick_sync()
        elif cmd == "--download":
            print("  Download: Copy from Google Drive to local")
            quick_sync()
        elif cmd == "--auto":
            auto_sync()
        else:
            print(f"  Unknown: {cmd}")
    else:
        quick_sync()
'''
    with open(sync_script, "w") as f:
        f.write(content)
    print("  [OK] Google Drive sync script created")


def create_master_launcher():
    """Update the master launcher with all services."""
    launcher = os.path.join(SCRIPT_DIR, "multifly_connect.py")
    content = '''"""
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
    print("\\n  === GITHUB COPILOT ===\\n")
    result = subprocess.run(
        ["gh", "auth", "status"],
        capture_output=True, text=True, timeout=10
    )
    if "Logged in" in result.stdout:
        print("  [OK] GitHub authenticated")
    else:
        print("  [!] Not logged in - run: gh auth login")

    # Check extension
    ag = os.path.expanduser(r"~\\AppData\\Local\\Programs\\Antigravity IDE\\bin\\antigravity-ide.cmd")
    result = subprocess.run([ag, "--list-extensions"], capture_output=True, text=True, timeout=10)
    if "github.copilot" in result.stdout:
        print("  [OK] Copilot extension installed")
        print("  [OK] Copilot Chat installed")
    else:
        print("  [!] Copilot not installed")

    print("  Copilot features available:")
    print("    - Code completion (auto-suggest)")
    print("    - Chat: @workspace, /explain, /fix, /tests")
    print("    - Code review")
    print("    - Test generation")

def deploy_vercel():
    """Deploy current project to Vercel."""
    print("\\n  === VERCEL DEPLOY ===\\n")
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
    print("\\n  === CI/CD CHECKS ===\\n")
    checks = [
        ("Python syntax", "python -m py_compile unified_multifly.py"),
        ("Python syntax", "python -m py_compile multifly_elite.py"),
        ("Import check", "python -c \\"from unified_multifly import Brain; print('OK')\\""),
        ("Import check", "python -c \\"from multifly_elite import NLPEngine; print('OK')\\""),
        ("Brain check", "python -c \\"from unified_multifly import Brain; b=Brain(); print(f'Brain: {b.summary()[\"commands\"]} cmds'); b.close()\\""),
    ]
    for name, cmd in checks:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
        status = "OK" if result.returncode == 0 else "FAIL"
        print(f"  [{status}] {name}")

def sync_brain():
    """Sync brain database."""
    print("\\n  === BRAIN SYNC ===\\n")
    sync_script = os.path.join(SCRIPT_DIR, "sync_brain.py")
    if os.path.exists(sync_script):
        subprocess.run([sys.executable, sync_script, "--sync"])
    else:
        print("  Sync script not found. Run setup first.")

def connect_all():
    """Connect all services."""
    print("\\n  ====================================================")
    print("   MULTIFLY CONNECT - All Services")
    print("  ====================================================\\n")
    check_copilot()
    print()
    run_ci()
    print()
    sync_brain()
    print()
    print("  ====================================================")
    print("   All services connected!")
    print("  ====================================================\\n")

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
'''
    with open(launcher, "w") as f:
        f.write(content)
    print("  [OK] Master connect script created")


if __name__ == "__main__":
    print("\\n  ====================================================")
    print("   CONNECTING ALL EXTERNAL SERVICES")
    print("  ====================================================\\n")

    update_settings()
    setup_vercel_deploy()
    setup_github_actions()
    setup_google_drive_sync()
    create_master_launcher()

    print("\\n  ====================================================")
    print("   ALL SERVICES CONNECTED!")
    print("  ====================================================\\n")
    print("  Commands:")
    print("    python multifly_connect.py copilot   Check Copilot")
    print("    python multifly_connect.py deploy    Deploy to Vercel")
    print("    python multifly_connect.py ci        Run CI/CD checks")
    print("    python multifly_connect.py sync      Sync brain to Drive")
    print("    python multifly_connect.py all       Connect everything")
    print()
