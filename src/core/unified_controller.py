"""
MULTIFLY UNIFIED CONTROLLER
============================
The ONE system to control EVERYTHING.

Manages:
- OmniRoute (AI Server)
- RAGFlow (RAG Engine)
- Dify (LLM Platform)
- Graph Engine (Code Analysis)
- Obsidian Vault (Knowledge)
- Voice Commands
- LinkedIn/WhatsApp Automation
- All Multifly subsystems

Features:
- Single command to start/stop everything
- Docker container management
- Service health monitoring
- Auto-recovery on crashes
- Real-time status dashboard
- REST API for external control
"""

import os
import sys
import json
import time
import socket
import sqlite3
import subprocess
import threading
from datetime import datetime
from pathlib import Path
from collections import defaultdict

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(os.path.dirname(SCRIPT_DIR))


class ServiceManager:
    """Manage all services (Docker + native)."""

    SERVICES = {
        "omniroute": {
            "name": "OmniRoute AI Server",
            "type": "native",
            "port": 20128,
            "start_cmd": f'cd /d "C:\\Users\\Ayush Mishra\\OmniRoute" && npm run dev',
            "health_url": "http://localhost:20128/",
            "priority": 1,
        },
        "ragflow": {
            "name": "RAGFlow RAG Engine",
            "type": "docker",
            "port": 9380,
            "container": "ragflow-server",
            "health_url": "http://localhost:9380/",
            "priority": 2,
        },
        "dify": {
            "name": "Dify LLM Platform",
            "type": "docker",
            "port": 3000,
            "container": "dify-web",
            "health_url": "http://localhost:3000/",
            "priority": 3,
        },
        "graph_engine": {
            "name": "Graph Engineering Engine",
            "type": "native",
            "port": None,
            "priority": 4,
        },
        "obsidian": {
            "name": "Obsidian Knowledge Vault",
            "type": "native",
            "port": None,
            "priority": 5,
        },
        "voice": {
            "name": "Voice Command System",
            "type": "native",
            "port": None,
            "priority": 6,
        },
        "api": {
            "name": "REST API Server",
            "type": "native",
            "port": 2035,
            "start_cmd": f'python "{SCRIPT_DIR}/unified_multifly.py" api',
            "priority": 7,
        },
        "websocket": {
            "name": "WebSocket Server",
            "type": "native",
            "port": 2036,
            "priority": 8,
        },
    }

    def __init__(self):
        self.status = {}
        self._check_all()

    def _check_port(self, port):
        """Check if a port is listening."""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(2)
            result = s.connect_ex(("127.0.0.1", port))
            s.close()
            return result == 0
        except Exception:
            return False

    def _check_container(self, name):
        """Check if a Docker container is running."""
        try:
            result = subprocess.run(
                f"docker inspect --format='{{{{.State.Status}}}}' {name}",
                shell=True, capture_output=True, text=True, timeout=10
            )
            return result.stdout.strip() == "running"
        except Exception:
            return False

    def _check_all(self):
        """Check status of all services."""
        for sid, svc in self.SERVICES.items():
            if svc["type"] == "docker" and "container" in svc:
                self.status[sid] = {
                    "name": svc["name"],
                    "running": self._check_container(svc["container"]),
                    "type": "docker",
                }
            elif svc.get("port"):
                self.status[sid] = {
                    "name": svc["name"],
                    "running": self._check_port(svc["port"]),
                    "type": "native",
                    "port": svc["port"],
                }
            else:
                self.status[sid] = {
                    "name": svc["name"],
                    "running": False,
                    "type": "native",
                }

    def start(self, service_id):
        """Start a specific service."""
        svc = self.SERVICES.get(service_id)
        if not svc:
            return {"error": f"Unknown service: {service_id}"}

        if self.status.get(service_id, {}).get("running"):
            return {"status": "already_running", "service": svc["name"]}

        if svc["type"] == "docker" and "container" in svc:
            return self._start_docker(service_id, svc)
        elif svc.get("start_cmd"):
            return self._start_native(service_id, svc)
        else:
            return {"status": "no_start_command", "service": svc["name"]}

    def _start_docker(self, service_id, svc):
        """Start a Docker container."""
        try:
            subprocess.run(
                f"docker start {svc['container']}",
                shell=True, capture_output=True, timeout=30
            )
            self.status[service_id]["running"] = True
            return {"status": "started", "service": svc["name"]}
        except Exception as e:
            return {"status": "error", "error": str(e)}

    def _start_native(self, service_id, svc):
        """Start a native service."""
        try:
            subprocess.Popen(
                svc["start_cmd"],
                shell=True,
                creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == "nt" else 0
            )
            self.status[service_id]["running"] = True
            return {"status": "started", "service": svc["name"]}
        except Exception as e:
            return {"status": "error", "error": str(e)}

    def stop(self, service_id):
        """Stop a specific service."""
        svc = self.SERVICES.get(service_id)
        if not svc:
            return {"error": f"Unknown service: {service_id}"}

        if svc["type"] == "docker" and "container" in svc:
            try:
                subprocess.run(
                    f"docker stop {svc['container']}",
                    shell=True, capture_output=True, timeout=30
                )
                self.status[service_id]["running"] = False
                return {"status": "stopped", "service": svc["name"]}
            except Exception as e:
                return {"status": "error", "error": str(e)}
        return {"status": "cannot_stop_native", "service": svc["name"]}

    def start_all(self):
        """Start all services in priority order."""
        results = []
        sorted_services = sorted(
            self.SERVICES.items(),
            key=lambda x: x[1].get("priority", 99)
        )
        for sid, svc in sorted_services:
            result = self.start(sid)
            results.append({"service": sid, **result})
            time.sleep(2)  # Stagger starts
        return results

    def status_all(self):
        """Get status of all services."""
        self._check_all()
        return self.status


class DockerManager:
    """Manage Docker containers for RAGFlow and Dify."""

    def __init__(self):
        self.compose_dir_ragflow = os.path.expanduser(r"~\ragflow\docker")
        self.compose_dir_dify = os.path.expanduser(r"~\dify\docker")

    def _run_compose(self, dir_path, action):
        """Run docker-compose action."""
        try:
            result = subprocess.run(
                f"docker compose {action}",
                cwd=dir_path,
                shell=True,
                capture_output=True,
                text=True,
                timeout=120
            )
            return {"success": result.returncode == 0, "output": result.stdout[:500], "error": result.stderr[:500]}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def start_ragflow(self):
        """Start RAGFlow with Docker Compose."""
        if not os.path.exists(self.compose_dir_ragflow):
            return {"success": False, "error": "RAGFlow docker dir not found"}
        return self._run_compose(self.compose_dir_ragflow, "up -d")

    def stop_ragflow(self):
        """Stop RAGFlow."""
        if not os.path.exists(self.compose_dir_ragflow):
            return {"success": False, "error": "RAGFlow docker dir not found"}
        return self._run_compose(self.compose_dir_ragflow, "down")

    def start_dify(self):
        """Start Dify with Docker Compose."""
        if not os.path.exists(self.compose_dir_dify):
            return {"success": False, "error": "Dify docker dir not found"}
        return self._run_compose(self.compose_dir_dify, "up -d")

    def stop_dify(self):
        """Stop Dify."""
        if not os.path.exists(self.compose_dir_dify):
            return {"success": False, "error": "Dify docker dir not found"}
        return self._run_compose(self.compose_dir_dify, "down")

    def list_containers(self):
        """List all running containers."""
        try:
            result = subprocess.run(
                "docker ps --format '{{.Names}}\t{{.Status}}\t{{.Ports}}'",
                shell=True, capture_output=True, text=True, timeout=10
            )
            return result.stdout.strip()
        except Exception:
            return "Cannot list containers"


class UnifiedBrain:
    """The unified brain that connects everything."""

    def __init__(self, db_path=None):
        self.db_path = db_path or os.path.join(BASE_DIR, "unified_brain.db")
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()

        c.execute("""CREATE TABLE IF NOT EXISTS commands (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            input TEXT, intent TEXT, system TEXT,
            result TEXT, success INTEGER, ms INTEGER
        )""")

        c.execute("""CREATE TABLE IF NOT EXISTS knowledge (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT, key TEXT UNIQUE,
            value TEXT, confidence REAL DEFAULT 0.5
        )""")

        c.execute("""CREATE TABLE IF NOT EXISTS service_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            service TEXT, action TEXT, status TEXT, details TEXT
        )""")

        conn.commit()
        conn.close()

    def log_command(self, input_text, intent, system, result, success=True, ms=0):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute(
            "INSERT INTO commands (input, intent, system, result, success, ms) VALUES (?,?,?,?,?,?)",
            (input_text, intent, system, result, 1 if success else 0, ms)
        )
        conn.commit()
        conn.close()

    def log_service(self, service, action, status, details=""):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute(
            "INSERT INTO service_log (service, action, status, details) VALUES (?,?,?,?)",
            (service, action, status, details)
        )
        conn.commit()
        conn.close()

    def save_knowledge(self, key, value, category="general"):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute(
            "INSERT OR REPLACE INTO knowledge (category, key, value) VALUES (?,?,?)",
            (category, key, value)
        )
        conn.commit()
        conn.close()

    def get_stats(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        stats = {
            "commands": c.execute("SELECT COUNT(*) FROM commands").fetchone()[0],
            "knowledge": c.execute("SELECT COUNT(*) FROM knowledge").fetchone()[0],
            "service_logs": c.execute("SELECT COUNT(*) FROM service_log").fetchone()[0],
        }
        conn.close()
        return stats


class UnifiedController:
    """
    THE MASTER CONTROLLER
    Controls everything from one place.
    """

    def __init__(self):
        self.services = ServiceManager()
        self.docker = DockerManager()
        self.brain = UnifiedBrain()

    def status(self):
        """Get complete system status."""
        svc_status = self.services.status_all()
        brain_stats = self.brain.get_stats()

        return {
            "timestamp": datetime.now().isoformat(),
            "services": svc_status,
            "brain": brain_stats,
            "total_services": len(svc_status),
            "running": sum(1 for s in svc_status.values() if s.get("running")),
            "stopped": sum(1 for s in svc_status.values() if not s.get("running")),
        }

    def start_system(self, target=None):
        """Start system(s). target=None means all."""
        if target:
            return self.services.start(target)
        return self.services.start_all()

    def stop_system(self, target):
        """Stop a specific system."""
        return self.services.stop(target)

    def docker_action(self, action, target):
        """Docker operations: start/stop/status for ragflow/dify."""
        if target == "ragflow":
            if action == "start":
                return self.docker.start_ragflow()
            elif action == "stop":
                return self.docker.stop_ragflow()
        elif target == "dify":
            if action == "start":
                return self.docker.start_dify()
            elif action == "stop":
                return self.docker.stop_dify()
        elif action == "list":
            return {"containers": self.docker.list_containers()}
        return {"error": f"Unknown docker action: {action} {target}"}

    def analyze_code(self, path=None):
        """Run graph engine analysis."""
        sys.path.insert(0, SCRIPT_DIR)
        try:
            from graph_engine import MultiflyGraphEngine
            engine = MultiflyGraphEngine()
            result = engine.analyze(path or os.getcwd())
            self.brain.log_command("analyze code", "graph_analysis", "graph_engine", "success")
            return result
        except Exception as e:
            return {"error": str(e)}

    def query_knowledge(self, query):
        """Search across all knowledge sources."""
        results = {"query": query, "sources": {}}

        # Search graph engine
        try:
            sys.path.insert(0, SCRIPT_DIR)
            from graph_engine import MultiflyGraphEngine
            engine = MultiflyGraphEngine()
            graph_results = engine.query(query)
            results["sources"]["graph"] = graph_results[:5]
        except Exception:
            pass

        # Search brain
        try:
            conn = sqlite3.connect(self.brain.db_path)
            c = conn.cursor()
            c.execute(
                "SELECT key, value FROM knowledge WHERE key LIKE ? OR value LIKE ? LIMIT 5",
                (f"%{query}%", f"%{query}%")
            )
            results["sources"]["brain"] = [{"key": r[0], "value": r[1]} for r in c.fetchall()]
            conn.close()
        except Exception:
            pass

        return results

    def dashboard_data(self):
        """Get all data for the dashboard."""
        return {
            "status": self.status(),
            "docker": self.docker.list_containers(),
            "brain": self.brain.get_stats(),
            "timestamp": datetime.now().isoformat(),
        }


def main():
    """CLI for the unified controller."""
    if len(sys.argv) < 2:
        print("""
  ====================================================
   MULTIFLY UNIFIED CONTROLLER
   One System to Rule Them All
  ====================================================

  Usage:
    python unified_controller.py status              Full system status
    python unified_controller.py start [service]     Start service(s)
    python unified_controller.py stop <service>      Stop a service
    python unified_controller.py docker <act> <tgt>  Docker: start/stop/list ragflow/dify
    python unified_controller.py analyze [path]      Analyze codebase
    python unified_controller.py query <text>        Search knowledge
    python unified_controller.py dashboard           Dashboard data

  Services:
    omniroute      AI Server (port 20128)
    ragflow        RAG Engine (Docker)
    dify           LLM Platform (Docker)
    graph_engine   Code Analysis
    obsidian       Knowledge Vault
    voice          Voice Commands
    api            REST API (port 2035)
    websocket      WebSocket (port 2036)
  ====================================================
        """)
        return

    ctrl = UnifiedController()
    cmd = sys.argv[1]

    if cmd == "status":
        result = ctrl.status()
        print(json.dumps(result, indent=2, default=str))

    elif cmd == "start":
        target = sys.argv[2] if len(sys.argv) > 2 else None
        result = ctrl.start_system(target)
        print(json.dumps(result, indent=2, default=str))

    elif cmd == "stop":
        target = sys.argv[2] if len(sys.argv) > 2 else "omniroute"
        result = ctrl.stop_system(target)
        print(json.dumps(result, indent=2, default=str))

    elif cmd == "docker":
        action = sys.argv[2] if len(sys.argv) > 2 else "list"
        target = sys.argv[3] if len(sys.argv) > 3 else ""
        result = ctrl.docker_action(action, target)
        print(json.dumps(result, indent=2, default=str))

    elif cmd == "analyze":
        path = sys.argv[2] if len(sys.argv) > 2 else None
        result = ctrl.analyze_code(path)
        print(json.dumps(result, indent=2, default=str))

    elif cmd == "query":
        query = " ".join(sys.argv[2:])
        result = ctrl.query_knowledge(query)
        print(json.dumps(result, indent=2, default=str))

    elif cmd == "dashboard":
        result = ctrl.dashboard_data()
        print(json.dumps(result, indent=2, default=str))


if __name__ == "__main__":
    main()
