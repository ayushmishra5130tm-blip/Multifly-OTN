"""
MULTIFLY LAUNCHER - One Command Starts Everything
===================================================
The single entry point for the entire Multifly system.

Usage:
  python multifly_launcher.py           Start everything
  python multifly_launcher.py --status  Show what's running
  python multifly_launcher.py --stop    Stop everything
  python multifly_launcher.py --help    Show help
"""

import sys, os, time, json, socket, signal, subprocess, threading
from datetime import datetime
from pathlib import Path

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PID_FILE = os.path.join(SCRIPT_DIR, "multifly_pids.json")

# All services with their启动 commands
SERVICES = {
    "omniroute": {
        "name": "OmniRoute AI Server",
        "port": 20128,
        "cmd": "npm run dev",
        "cwd": os.path.expanduser(r"~\OmniRoute"),
        "type": "node",
        "priority": 1,
    },
    "api": {
        "name": "REST API Server",
        "port": 2035,
        "cmd": f'python "{SCRIPT_DIR}/unified_multifly.py" api',
        "type": "python",
        "priority": 2,
    },
    "websocket": {
        "name": "WebSocket Server",
        "port": 2036,
        "cmd": f'python "{SCRIPT_DIR}/multifly_elite.py" websocket',
        "type": "python",
        "priority": 3,
    },
    "watchdog": {
        "name": "OmniRoute Watchdog",
        "cmd": f'python "{SCRIPT_DIR}/omniroute_watchdog.py"',
        "type": "python",
        "priority": 4,
    },
}


def check_port(port):
    """Check if a port is listening."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(2)
        result = s.connect_ex(("127.0.0.1", port))
        s.close()
        return result == 0
    except:
        return False


def save_pids(pids):
    """Save running process IDs."""
    with open(PID_FILE, "w") as f:
        json.dump(pids, f, indent=2)


def load_pids():
    """Load saved process IDs."""
    if os.path.exists(PID_FILE):
        with open(PID_FILE, "r") as f:
            return json.load(f)
    return {}


def kill_pids():
    """Kill all saved Multifly processes."""
    pids = load_pids()
    for service, pid in pids.items():
        try:
            subprocess.run(["taskkill", "/PID", str(pid), "/F"], 
                         capture_output=True, timeout=5)
        except:
            pass
    # Clear PID file
    if os.path.exists(PID_FILE):
        os.remove(PID_FILE)


def start_service(name, config):
    """Start a single service."""
    if config.get("port") and check_port(config["port"]):
        print(f"  [OK] {config['name']} (already running on port {config['port']})")
        return None

    try:
        si = subprocess.STARTUPINFO()
        si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        si.wShowWindow = 0  # SW_HIDE

        if config["type"] == "node":
            proc = subprocess.Popen(
                config["cmd"],
                cwd=config.get("cwd", os.getcwd()),
                startupinfo=si,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                shell=True
            )
        else:
            proc = subprocess.Popen(
                config["cmd"],
                startupinfo=si,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                shell=True
            )

        print(f"  [>>] {config['name']} (PID: {proc.pid})")
        return proc.pid

    except Exception as e:
        print(f"  [!!] {config['name']} failed: {e}")
        return None


def show_status():
    """Show status of all services."""
    print("\n  ====================================================")
    print("   MULTIFLY STATUS - All Services")
    print("  ====================================================\n")

    all_ok = True
    for name, config in sorted(SERVICES.items(), key=lambda x: x[1].get("priority", 99)):
        if config.get("port"):
            running = check_port(config["port"])
            icon = "+" if running else "X"
            color = "green" if running else "red"
            status = f"ONLINE (port {config['port']})" if running else "OFFLINE"
            if not running:
                all_ok = False
        else:
            # For services without ports, check PID file
            pids = load_pids()
            running = name in pids
            icon = "+" if running else "?"
            color = "green" if running else "yellow"
            status = "RUNNING" if running else "NOT STARTED"
            if not running:
                all_ok = False

        print(f"  [{color}]{icon}[/] {config['name']:<30} {status}")

    print()

    # Brain status
    try:
        sys.path.insert(0, SCRIPT_DIR)
        from unified_multifly import Brain
        brain = Brain()
        s = brain.summary()
        print(f"  Brain: {s['commands']} commands | {s['patterns']} patterns | {s['actions']} actions")
        brain.conn.close()
    except:
        print("  Brain: not initialized")

    # System tools
    print()
    tools = []
    for tool, cmd in [("Python", "python --version"), ("Node", "node --version"), ("Git", "git --version")]:
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=5)
            ver = result.stdout.strip()
            tools.append(f"{tool}: {ver}")
        except:
            tools.append(f"{tool}: not found")
    print(f"  Tools: {' | '.join(tools)}")

    return all_ok


def launch_all():
    """Launch all services."""
    print("\n  ====================================================")
    print("   MULTIFLY LAUNCHER - Starting All Systems")
    print(f"   {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("  ====================================================\n")

    # Kill any existing instances first
    kill_pids()

    # Start services in priority order
    pids = {}
    for name, config in sorted(SERVICES.items(), key=lambda x: x[1].get("priority", 99)):
        pid = start_service(name, config)
        if pid:
            pids[name] = pid
            time.sleep(2)  # Give each service time to start

    # Save PIDs
    save_pids(pids)

    # Final status
    print()
    print("  ====================================================")
    online = 0
    for name, config in SERVICES.items():
        if config.get("port") and check_port(config["port"]):
            online += 1
        elif name in pids:
            online += 1

    print(f"   {online}/{len(SERVICES)} services started")
    print()
    print("   REST API:  http://127.0.0.1:2035")
    print("   WebSocket: ws://127.0.0.1:2036")
    print("   OmniRoute: http://localhost:20128")
    print("   Dashboard: python unified_multifly.py dashboard")
    print("   NLP Mode:  python multifly_elite.py nlp")
    print("   ML Report: python multifly_elite.py ml")
    print("  ====================================================\n")


def stop_all():
    """Stop all services."""
    print("\n  Stopping all Multifly services...")
    kill_pids()

    # Also kill by port
    for name, config in SERVICES.items():
        if config.get("port"):
            try:
                result = subprocess.run(
                    f'netstat -ano | grep ":{config["port"]}" | grep LISTENING',
                    shell=True, capture_output=True, text=True, timeout=5
                )
                for line in result.stdout.strip().split("\n"):
                    if line.strip():
                        pid = line.strip().split()[-1]
                        subprocess.run(["taskkill", "/PID", pid, "/F"], 
                                     capture_output=True, timeout=5)
            except:
                pass

    print("  All services stopped.\n")


def show_help():
    """Show help information."""
    print("""
  ====================================================
   MULTIFLY - The Complete Developer System
  ====================================================

  COMMANDS:
    python multifly_launcher.py           Start all services
    python multifly_launcher.py --status  Check what's running
    python multifly_launcher.py --stop    Stop everything
    python multifly_launcher.py --help    This help

  SERVICES:
    OmniRoute AI    (port 20128)   AI code generation
    REST API        (port 2035)    System communication
    WebSocket       (port 2036)    Real-time updates
    Watchdog        (background)   Auto-restart OmniRoute

  TOOLS:
    python unified_multifly.py dashboard    Live TUI dashboard
    python unified_multifly.py api          REST API only
    python unified_multifly.py activate     Activate all systems
    python unified_multifly.py learn        Self-learning
    python unified_multifly.py status       Quick status
    python multifly_elite.py nlp            Natural language
    python multifly_elite.py ml             ML analysis
    python multifly_elite.py websocket      WebSocket only

  KEYBOARD SHORTCUTS (in IDE):
    Ctrl+Shift+Space    2035 Command Center
    Ctrl+Shift+B        Neural prompt
    Ctrl+Shift+G        Live animated dashboard
    Ctrl+Shift+F        Auto-fix everything
    Ctrl+Shift+D        Deploy
    Ctrl+Shift+T        Run tests
    Ctrl+Shift+O        Generate docs

  ====================================================
    """)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        cmd = sys.argv[1].lower()
        if cmd == "--status" or cmd == "-s":
            show_status()
        elif cmd == "--stop" or cmd == "-k":
            stop_all()
        elif cmd == "--help" or cmd == "-h":
            show_help()
        else:
            print(f"  Unknown option: {cmd}")
            show_help()
    else:
        launch_all()
