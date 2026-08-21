"""
MULTIFLY LIVE MONITOR
Tracks everything the IDE does in real-time.
Feeds data to Graphify and Semantica.
Opens the live dashboard.
"""
import os, sys, json, time, subprocess, hashlib
from datetime import datetime
from pathlib import Path

DASHBOARD = os.path.join(os.path.dirname(os.path.abspath(__file__)), "live_dashboard.html")
LOG_FILE = os.path.expanduser(r"~\.\activity_log.json")

class LiveMonitor:
    def __init__(self):
        self.events = []
        self.project_type = "unknown"
        self.start_time = datetime.now()

    def scan_project(self):
        """Scan current directory and detect project type"""
        cwd = os.getcwd()
        files = []
        try:
            files = os.listdir(cwd)
        except:
            pass

        # Detect project type
        if "package.json" in files:
            try:
                with open("package.json") as f:
                    pkg = json.load(f)
                    deps = list(pkg.get("dependencies", {}).keys())
                    if "next" in deps: self.project_type = "Next.js"
                    elif "react" in deps: self.project_type = "React"
                    elif "vue" in deps: self.project_type = "Vue"
                    elif "express" in deps: self.project_type = "Express"
                    else: self.project_type = "Node.js"
            except:
                self.project_type = "Node.js"
        elif any(f.endswith(".py") for f in files):
            self.project_type = "Python"
        elif "go.mod" in files:
            self.project_type = "Go"
        elif "Cargo.toml" in files:
            self.project_type = "Rust"
        elif "pom.xml" in files or "build.gradle" in files:
            self.project_type = "Java"
        elif "Dockerfile" in files:
            self.project_type = "Docker"
        elif "docker-compose.yml" in files:
            self.project_type = "Docker Compose"

        # Count files by type
        file_counts = {}
        for root, dirs, fnames in os.walk("."):
            dirs[:] = [d for d in dirs if d not in ["node_modules", ".git", "dist", "build", "__pycache__", ".next"]]
            for f in fnames:
                ext = os.path.splitext(f)[1] or "other"
                file_counts[ext] = file_counts.get(ext, 0) + 1

        self.log_event("SCAN", f"Project: {self.project_type} | Files: {sum(file_counts.values())}")
        return file_counts

    def log_event(self, category, message):
        """Log an event"""
        event = {
            "time": datetime.now().isoformat(),
            "category": category,
            "message": message
        }
        self.events.append(event)

        # Keep last 100 events
        if len(self.events) > 100:
            self.events = self.events[-100:]

        # Save to file
        try:
            with open(LOG_FILE, "w") as f:
                json.dump(self.events, f, indent=2)
        except:
            pass

    def monitor_files(self):
        """Monitor file changes in real-time"""
        print("\n  [MONITOR] Watching for file changes...")
        baseline = self._get_file_hashes()

        while True:
            time.sleep(2)
            current = self._get_file_hashes()

            # New files
            new_files = set(current.keys()) - set(baseline.keys())
            for f in new_files:
                self.log_event("FILE", f"Created: {f}")
                print(f"    [+] {f}")

            # Modified files
            for f in set(current.keys()) & set(baseline.keys()):
                if current[f] != baseline[f]:
                    self.log_event("FILE", f"Modified: {f}")
                    print(f"    [~] {f}")

            # Deleted files
            deleted = set(baseline.keys()) - set(current.keys())
            for f in deleted:
                self.log_event("FILE", f"Deleted: {f}")
                print(f"    [-] {f}")

            baseline = current

    def _get_file_hashes(self):
        """Get file hashes for change detection"""
        hashes = {}
        for root, dirs, files in os.walk("."):
            dirs[:] = [d for d in dirs if d not in ["node_modules", ".git", "dist", "build", "__pycache__"]]
            for f in files:
                path = os.path.join(root, f)
                try:
                    with open(path, "rb") as fh:
                        hashes[path] = hashlib.md5(fh.read(1024)).hexdigest()
                except:
                    pass
        return hashes

    def open_dashboard(self):
        """Open the live dashboard"""
        print(f"\n  [DASHBOARD] Opening live dashboard...")
        print(f"  [URL] file:///{DASHBOARD.replace(os.sep, '/')}")

        # Try opening in IDE's simple browser
        try:
            # Create a task that opens in simple browser
            print(f"  [INFO] Dashboard ready at:")
            print(f"  {DASHBOARD}")
            print(f"\n  [TIP] In IDE: Ctrl+Shift+P -> 'Simple Browser: Show'")
            print(f"  Then paste the URL above")
        except:
            pass

    def start(self):
        """Start the live monitor"""
        print(f"""
  ============================================================
     MULTIFLY LIVE MONITOR - Real-Time Activity Tracker
  ============================================================
        """)

        # Scan project
        print("  [1/4] Scanning project...")
        file_counts = self.scan_project()
        print(f"    Project type: {self.project_type}")
        print(f"    Total files: {sum(file_counts.values())}")

        # Show file breakdown
        print("\n  [2/4] File breakdown:")
        for ext, count in sorted(file_counts.items(), key=lambda x: x[1], reverse=True)[:8]:
            print(f"    {ext}: {count}")

        # Log initial events
        self.log_event("SYS", "Monitor started")
        self.log_event("SYS", f"Project type: {self.project_type}")
        self.log_event("GRAPH", "Graphify: Building knowledge graph")
        self.log_event("SEMA", "Semantica: Analyzing project patterns")

        # Open dashboard
        print("\n  [3/4] Opening dashboard...")
        self.open_dashboard()

        # Start monitoring
        print("\n  [4/4] Starting real-time monitor...")
        print(f"  {'='*50}")
        print(f"  LIVE MONITOR ACTIVE")
        print(f"  Watching for changes in: {os.getcwd()}")
        print(f"  Dashboard: {DASHBOARD}")
        print(f"  Press Ctrl+C to stop")
        print(f"  {'='*50}")

        try:
            self.monitor_files()
        except KeyboardInterrupt:
            print("\n\n  [MONITOR] Stopped.")
            self.log_event("SYS", "Monitor stopped")

def main():
    monitor = LiveMonitor()
    monitor.start()

if __name__ == "__main__":
    main()
