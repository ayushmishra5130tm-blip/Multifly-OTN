"""
MULTIFLY OMNIROUTE WATCHDOG
Monitors OmniRoute server and auto-restarts if it crashes.
Run in background: python omniroute_watchdog.py
"""
import subprocess
import socket
import time
import os
import sys
from datetime import datetime

PORT = 20128
OMNIROUTE_DIR = os.path.expanduser(r"~\OmniRoute")
CHECK_INTERVAL = 15  # seconds between checks
RESTART_DELAY = 5    # seconds to wait before restart attempt
MAX_RESTARTS = 20    # max restarts before giving up
RESTART_WINDOW = 3600  # reset restart counter after 1 hour

restart_count = 0
last_restart_time = time.time()
process = None


def log(msg):
    """Print with timestamp."""
    ts = datetime.now().strftime("%H:%M:%S")
    print(f"[{ts}] {msg}", flush=True)


def check_port(port):
    """Check if port is listening."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(2)
        result = s.connect_ex(("127.0.0.1", port))
        s.close()
        return result == 0
    except:
        return False


def kill_omniroute():
    """Kill any existing OmniRoute processes."""
    try:
        result = subprocess.run(
            ["tasklist", "/FI", "IMAGENAME eq node.exe", "/FO", "CSV", "/NH"],
            capture_output=True, text=True, timeout=10
        )
        for line in result.stdout.strip().split("\n"):
            if not line.strip():
                continue
            parts = line.replace('"', '').split(",")
            if len(parts) >= 2:
                pid = parts[1]
                try:
                    check = subprocess.run(
                        ["wmic", "process", f"ProcessId={pid}", "get", "CommandLine"],
                        capture_output=True, text=True, timeout=5
                    )
                    if "omniroute" in check.stdout.lower() or "run-next" in check.stdout.lower():
                        subprocess.run(["taskkill", "/PID", pid, "/F"], capture_output=True, timeout=5)
                        log(f"  Killed OmniRoute process PID {pid}")
                except:
                    pass
    except Exception as e:
        log(f"  Kill error: {e}")


def start_omniroute():
    """Start OmniRoute server."""
    global process
    kill_omniroute()
    time.sleep(2)

    log("  Starting OmniRoute (npm run dev)...")
    try:
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        startupinfo.wShowWindow = 0  # SW_HIDE

        process = subprocess.Popen(
            "cmd /c npm run dev",
            cwd=OMNIROUTE_DIR,
            startupinfo=startupinfo,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            shell=True
        )
        log(f"  OmniRoute started (PID: {process.pid})")
        return True
    except Exception as e:
        log(f"  Start error: {e}")
        return False


def main():
    global restart_count, last_restart_time

    print("=" * 50)
    print("  OMNIROUTE WATCHDOG")
    print("  Auto-restarts if server crashes")
    print("=" * 50)
    print()
    log(f"Monitoring port {PORT}")
    log(f"Check interval: {CHECK_INTERVAL}s")
    log(f"Max restarts: {MAX_RESTARTS}")
    print()

    # Initial start
    if not check_port(PORT):
        log("OmniRoute not running, starting...")
        start_omniroute()
        log(f"Waiting up to 60s for startup...")
        for i in range(20):
            time.sleep(3)
            if check_port(PORT):
                log("OmniRoute is ONLINE")
                break
        else:
            log("WARNING: OmniRoute still not responding after 60s")
    else:
        log("OmniRoute already running")

    # Main watchdog loop
    while True:
        time.sleep(CHECK_INTERVAL)

        # Reset restart counter after window
        if time.time() - last_restart_time > RESTART_WINDOW:
            if restart_count > 0:
                log(f"Resetting restart counter (was {restart_count})")
                restart_count = 0

        if check_port(PORT):
            # Server is healthy
            pass
        else:
            # Server is down
            log("ALERT: OmniRoute is DOWN!")
            restart_count += 1
            last_restart_time = time.time()

            if restart_count > MAX_RESTARTS:
                log(f"FATAL: Too many restarts ({restart_count}). Giving up.")
                log("Check OmniRoute manually or fix the underlying issue.")
                sys.exit(1)

            log(f"Restart attempt {restart_count}/{MAX_RESTARTS}...")
            time.sleep(RESTART_DELAY)

            if start_omniroute():
                # Wait for it to come up
                for i in range(20):
                    time.sleep(3)
                    if check_port(PORT):
                        log(f"SUCCESS: OmniRoute restarted (attempt {restart_count})")
                        break
                else:
                    log(f"WARNING: OmniRoute not responding after restart")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        log("Watchdog stopped")
        sys.exit(0)
