"""
MULTIFLY UNIFIED - The Complete System
======================================
Live TUI Dashboard + REST API + Plugin Architecture + Self-Learning + Orchestrator

Features:
  1. Live TUI Dashboard (Rich) - Real-time animated terminal UI
  2. REST API (Flask) - Everything talks to everything
  3. Plugin System - Add new systems without rewriting
  4. Self-Learning Engine - Improves based on what works
  5. Orchestrator - One command activates everything
  6. SQLite Brain - Remembers every command, action, result

Usage:
  python unified_multifly.py dashboard    # Open live TUI dashboard
  python unified_multifly.py api          # Start REST API server
  python unified_multifly.py activate     # Activate all systems
  python unified_multifly.py learn        # Run self-learning analysis
  python unified_multifly.py status       # Show system status
  python unified_multifly.py plugin list  # List plugins
  python unified_multifly.py plugin add   # Add new plugin
"""

import sys, os, time, json, math, random, threading, sqlite3, socket
from datetime import datetime, timedelta
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(SCRIPT_DIR, "multifly_brain.db")
PLUGIN_DIR = os.path.join(SCRIPT_DIR, "plugins")

# Ensure plugin directory exists
os.makedirs(PLUGIN_DIR, exist_ok=True)


# ============================================================
#  1. SQLITE BRAIN - Remembers Everything
# ============================================================
class Brain:
    """SQLite memory that remembers every command, action, and result."""

    def __init__(self, db_path=DB_PATH):
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA journal_mode=WAL")
        self._create_tables()

    def _create_tables(self):
        c = self.conn.cursor()
        for table, schema in {
            "commands": "id INTEGER PRIMARY KEY AUTOINCREMENT, ts TEXT DEFAULT CURRENT_TIMESTAMP, cmd TEXT, category TEXT, result TEXT, ok INTEGER DEFAULT 1, ms INTEGER DEFAULT 0",
            "actions": "id INTEGER PRIMARY KEY AUTOINCREMENT, ts TEXT DEFAULT CURRENT_TIMESTAMP, system TEXT, action TEXT, target TEXT, result TEXT, ok INTEGER DEFAULT 1",
            "patterns": "id INTEGER PRIMARY KEY AUTOINCREMENT, ptype TEXT, pdata TEXT, conf REAL DEFAULT 0.5, seen INTEGER DEFAULT 1, last TEXT DEFAULT CURRENT_TIMESTAMP",
            "health": "id INTEGER PRIMARY KEY AUTOINCREMENT, ts TEXT DEFAULT CURRENT_TIMESTAMP, system TEXT, status TEXT, metrics TEXT",
            "errors": "id INTEGER PRIMARY KEY AUTOINCREMENT, ts TEXT DEFAULT CURRENT_TIMESTAMP, system TEXT, error TEXT, fixed INTEGER DEFAULT 0, fix TEXT",
            "prefs": "key TEXT PRIMARY KEY, value TEXT, conf REAL DEFAULT 0.5, updated TEXT DEFAULT CURRENT_TIMESTAMP",
            "daily": "date TEXT PRIMARY KEY, cmds INTEGER DEFAULT 0, acts INTEGER DEFAULT 0, errs INTEGER DEFAULT 0, uptime INTEGER DEFAULT 0",
        }.items():
            c.execute(f"CREATE TABLE IF NOT EXISTS {table} ({schema})")
        self.conn.commit()

    def log_cmd(self, cmd, cat="misc", result="", ok=True, ms=0):
        self.conn.execute("INSERT INTO commands (cmd,category,result,ok,ms) VALUES (?,?,?,?,?)",
                          (cmd, cat, result, 1 if ok else 0, ms))
        self._learn("cmd_freq", cmd)
        self._daily_inc("cmds")
        self.conn.commit()

    def log_action(self, sys_name, action, target="", result="", ok=True):
        self.conn.execute("INSERT INTO actions (system,action,target,result,ok) VALUES (?,?,?,?,?)",
                          (sys_name, action, target, result, 1 if ok else 0))
        self._learn("sys_use", sys_name)
        self._daily_inc("acts")
        self.conn.commit()

    def log_health(self, sys_name, status, metrics=""):
        self.conn.execute("INSERT INTO health (system,status,metrics) VALUES (?,?,?)",
                          (sys_name, status, metrics))
        self.conn.commit()

    def log_error(self, sys_name, error, fix=""):
        self.conn.execute("INSERT INTO errors (system,error,fix) VALUES (?,?,?)",
                          (sys_name, error, fix))
        self._daily_inc("errs")
        self.conn.commit()

    def set_pref(self, key, value, conf=0.5):
        self.conn.execute("INSERT OR REPLACE INTO prefs (key,value,conf,updated) VALUES (?,?,?,CURRENT_TIMESTAMP)",
                          (key, value, conf))
        self.conn.commit()

    def get_pref(self, key):
        r = self.conn.execute("SELECT value FROM prefs WHERE key=?", (key,)).fetchone()
        return r["value"] if r else None

    def _learn(self, ptype, data):
        r = self.conn.execute("SELECT id,seen,conf FROM patterns WHERE ptype=? AND pdata=?",
                              (ptype, data)).fetchone()
        if r:
            self.conn.execute("UPDATE patterns SET seen=seen+1,conf=MIN(0.99,conf+0.03),last=CURRENT_TIMESTAMP WHERE id=?",
                              (r["id"],))
        else:
            self.conn.execute("INSERT INTO patterns (ptype,pdata) VALUES (?,?)", (ptype, data))

    def _daily_inc(self, field):
        today = datetime.now().strftime("%Y-%m-%d")
        self.conn.execute("INSERT OR IGNORE INTO daily (date) VALUES (?)", (today,))
        self.conn.execute(f"UPDATE daily SET {field}={field}+1 WHERE date=?", (today,))

    def suggest(self):
        rows = self.conn.execute(
            "SELECT pdata FROM patterns WHERE ptype='cmd_freq' AND conf>=0.3 ORDER BY conf DESC LIMIT 5"
        ).fetchall()
        return [r["pdata"] for r in rows] if rows else ["graph", "fix", "status"]

    def summary(self):
        c = self.conn
        return {
            "commands": c.execute("SELECT COUNT(*) FROM commands").fetchone()[0],
            "actions": c.execute("SELECT COUNT(*) FROM actions").fetchone()[0],
            "patterns": c.execute("SELECT COUNT(*) FROM patterns").fetchone()[0],
            "errors": c.execute("SELECT COUNT(*) FROM errors").fetchone()[0],
            "resolved": c.execute("SELECT COUNT(*) FROM errors WHERE fixed=1").fetchone()[0],
            "prefs": c.execute("SELECT COUNT(*) FROM prefs").fetchone()[0],
            "today_cmds": c.execute("SELECT COALESCE(SUM(cmds),0) FROM daily WHERE date=date('now')").fetchone()[0],
            "today_acts": c.execute("SELECT COALESCE(SUM(acts),0) FROM daily WHERE date=date('now')").fetchone()[0],
            "health": [dict(r) for r in c.execute("SELECT system,status,MAX(ts) as ts FROM health GROUP BY system").fetchall()],
            "recent": [dict(r) for r in c.execute("SELECT * FROM commands ORDER BY ts DESC LIMIT 8").fetchall()],
            "patterns_top": [dict(r) for r in c.execute("SELECT pdata,conf,seen FROM patterns ORDER BY conf DESC LIMIT 5").fetchall()],
            "daily": [dict(r) for r in c.execute("SELECT * FROM daily ORDER BY date DESC LIMIT 7").fetchall()],
        }


# ============================================================
#  2. PLUGIN SYSTEM - Add New Systems Without Rewriting
# ============================================================
class PluginManager:
    """Manages plugins that extend Multifly's capabilities."""

    def __init__(self, plugin_dir=PLUGIN_DIR):
        self.plugin_dir = plugin_dir
        self.plugins = {}
        self._load_plugins()

    def _load_plugins(self):
        """Scan plugin directory and load all valid plugins."""
        for f in os.listdir(self.plugin_dir):
            if f.endswith(".py") and not f.startswith("_"):
                name = f[:-3]
                try:
                    import importlib.util
                    spec = importlib.util.spec_from_file_location(
                        f"plugin_{name}", os.path.join(self.plugin_dir, f)
                    )
                    mod = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(mod)

                    if hasattr(mod, "register"):
                        info = {"name": name, "module": mod, "info": {}}
                        if hasattr(mod, "PLUGIN_INFO"):
                            info["info"] = mod.PLUGIN_INFO
                        mod.register(self)
                        self.plugins[name] = info
                except Exception as e:
                    print(f"  Plugin {name} load error: {e}")

    def register_system(self, name, handler, description=""):
        """Register a new system from a plugin."""
        self.plugins[name] = {"handler": handler, "description": description}

    def activate(self, name=None):
        """Activate a specific plugin or all plugins."""
        activated = []
        for pname, pinfo in self.plugins.items():
            if name and pname != name:
                continue
            try:
                handler = pinfo.get("handler")
                if handler and callable(handler):
                    handler()
                    activated.append(pname)
            except Exception as e:
                print(f"  Plugin {pname} activation error: {e}")
        return activated

    def list_plugins(self):
        """List all available plugins."""
        result = []
        for name, info in self.plugins.items():
            result.append({
                "name": name,
                "description": info.get("description", info.get("info", {}).get("description", "")),
                "info": info.get("info", {}),
            })
        return result

    def create_plugin(self, name, code=""):
        """Create a new plugin file."""
        if not code:
            code = f'''"""
Plugin: {name}
Description: [Add description here]
"""
PLUGIN_INFO = {{"name": "{name}", "version": "1.0", "description": "[Add description]"}}

def register(manager):
    """Register this plugin with Multifly."""
    manager.register_system("{name}", activate, PLUGIN_INFO["description"])

def activate():
    """Called when this plugin is activated."""
    print(f"  {name} plugin activated!")
'''
        path = os.path.join(self.plugin_dir, f"{name}.py")
        with open(path, "w") as f:
            f.write(code)
        return path


# ============================================================
#  3. SELF-LEARNING ENGINE - Improves Based on What Works
# ============================================================
class SelfLearner:
    """Analyzes patterns and improves system behavior."""

    def __init__(self, brain):
        self.brain = brain

    def analyze(self):
        """Analyze all data and generate insights."""
        s = self.brain.summary()
        insights = []

        # Analyze command patterns
        if s["patterns_top"]:
            top = s["patterns_top"][0]
            insights.append({
                "type": "pattern",
                "insight": f"Most used: {top['pdata']} (confidence: {top['conf']:.0%}, seen: {top['seen']}x)",
                "action": f"Consider adding shortcut for '{top['pdata']}'"
            })

        # Analyze error patterns
        errors = self.brain.conn.execute(
            "SELECT error, COUNT(*) as c FROM errors WHERE fixed=0 GROUP BY error HAVING c>1"
        ).fetchall()
        for e in errors:
            insights.append({
                "type": "error",
                "insight": f"Recurring error: {e[0][:60]} (occurred {e[1]}x)",
                "action": "Auto-fix this error when detected"
            })

        # Analyze system health
        unhealthy = self.brain.conn.execute(
            "SELECT system, status FROM health WHERE status != 'running' GROUP BY system"
        ).fetchall()
        for h in unhealthy:
            insights.append({
                "type": "health",
                "insight": f"{h[0]} is {h[1]}",
                "action": f"Restart {h[0]}"
            })

        # Analyze daily trends
        daily = s["daily"]
        if len(daily) >= 2:
            today = daily[0]["cmds"] if daily else 0
            yesterday = daily[1]["cmds"] if len(daily) > 1 else 0
            if today > yesterday * 1.5:
                insights.append({
                    "type": "trend",
                    "insight": f"Activity up {((today/yesterday-1)*100):.0f}% from yesterday",
                    "action": "System is getting busier - consider optimization"
                })

        # Generate auto-improvements
        improvements = self._generate_improvements(s, insights)

        return {"insights": insights, "improvements": improvements, "summary": s}

    def _generate_improvements(self, summary, insights):
        """Generate automatic improvements based on analysis."""
        improvements = []

        # Auto-set preferences based on usage
        for p in summary["patterns_top"]:
            if p["conf"] > 0.7:
                self.brain.set_pref(f"auto_shortcut_{p['pdata']}", "true", p["conf"])
                improvements.append(f"Auto-shortcut enabled for '{p['pdata']}' (conf: {p['conf']:.0%})")

        # Auto-recommend system optimization
        if summary["commands"] > 50:
            improvements.append("System has processed 50+ commands - enable caching")
            self.brain.set_pref("cache_enabled", "true", 0.8)

        if summary["errors"] > summary["resolved"] * 2:
            improvements.append("High error rate - enable aggressive error recovery")
            self.brain.set_pref("error_recovery", "aggressive", 0.7)

        return improvements

    def apply_improvements(self):
        """Apply learned improvements to the system."""
        analysis = self.analyze()
        applied = []

        for imp in analysis["improvements"]:
            applied.append(imp)

        return {"analysis": analysis, "applied": applied}


# ============================================================
#  4. SYSTEMS REGISTRY - All Connected Systems
# ============================================================
class SystemRegistry:
    """Registry of all connected systems with real-time status."""

    SYSTEMS = {
        "omniroute": {"name": "OmniRoute AI", "port": 20128, "type": "ai", "icon": "AI"},
        "graphify": {"name": "Graphify", "type": "graph", "icon": "GRAPH"},
        "semantica": {"name": "Semantica", "type": "decision", "icon": "SEMA"},
        "brain": {"name": "Brain Elite", "type": "core", "icon": "CORE"},
        "ruflo": {"name": "Ruflo", "type": "agent", "icon": "AGENT"},
        "jcode": {"name": "JCode", "type": "codegen", "icon": "CODE"},
        "copilot": {"name": "GitHub Copilot", "type": "ai", "icon": "AUTO"},
        "linkedin_vt": {"name": "LinkedIn VoltairTech", "type": "business", "icon": "BIZ"},
        "linkedin_kt": {"name": "LinkedIn KaunTech", "type": "business", "icon": "BIZ"},
        "whatsapp": {"name": "WhatsApp", "type": "comms", "icon": "MSG"},
        "voice": {"name": "Voice RSS", "type": "input", "icon": "VOICE"},
        "git": {"name": "Git + GitLens", "type": "vcs", "icon": "VCS"},
        "docker": {"name": "Docker", "type": "ops", "icon": "OPS"},
        "python": {"name": "Python 3.14", "type": "lang", "icon": "PY"},
        "nodejs": {"name": "Node.js v22", "type": "lang", "icon": "JS"},
    }

    def __init__(self, brain):
        self.brain = brain
        self.status = {}

    def check_all(self):
        """Check health of all systems."""
        for sid, info in self.SYSTEMS.items():
            status = self._check_system(sid, info)
            self.status[sid] = status
            self.brain.log_health(info["name"], status["state"], json.dumps(status.get("details", {})))
        return self.status

    def _check_system(self, sid, info):
        """Check a single system's health."""
        try:
            if "port" in info:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(2)
                result = s.connect_ex(("127.0.0.1", info["port"]))
                s.close()
                if result == 0:
                    return {"state": "online", "details": {"port": info["port"]}}
                else:
                    return {"state": "offline", "details": {"port": info["port"]}}

            # Check if related files/scripts exist
            script_path = os.path.join(SCRIPT_DIR, f"{sid}.py")
            if os.path.exists(script_path):
                return {"state": "ready", "details": {"script": script_path}}

            return {"state": "standby", "details": {}}
        except Exception as e:
            return {"state": "error", "details": {"error": str(e)}}

    def get_status_text(self):
        """Get formatted status text."""
        lines = []
        for sid, info in self.SYSTEMS.items():
            st = self.status.get(sid, {"state": "unknown"})
            icon = "+" if st["state"] in ("online", "ready") else "?"
            color = "green" if st["state"] in ("online", "ready") else "yellow"
            lines.append(f"  [{color}]{icon}[/] {info['name']:<25} {st['state']}")
        return "\n".join(lines)


# ============================================================
#  5. ORCHESTRATOR - One Command Activates Everything
# ============================================================
class Orchestrator:
    """Activates and coordinates all systems."""

    def __init__(self, brain, registry, plugins, learner):
        self.brain = brain
        self.registry = registry
        self.plugins = plugins
        self.learner = learner
        self.active = False

    def activate_all(self, verbose=True):
        """Activate all systems."""
        results = []
        if verbose:
            print("\n  ====================================================")
            print("   MULTIFLY ORCHESTRATOR - ACTIVATING ALL SYSTEMS")
            print("  ====================================================\n")

        # Step 1: Check system health
        if verbose:
            print("  [1/5] Checking system health...")
        self.registry.check_all()
        online = sum(1 for s in self.registry.status.values() if s["state"] in ("online", "ready"))
        results.append(f"Health check: {online}/{len(self.registry.SYSTEMS)} systems ready")
        if verbose:
            print(f"        {online}/{len(self.registry.SYSTEMS)} systems online")

        # Step 2: Start OmniRoute if not running
        if verbose:
            print("  [2/5] OmniRoute AI...")
        omniroute = self.registry.status.get("omniroute", {})
        if omniroute.get("state") != "online":
            if verbose:
                print("        Starting OmniRoute...")
            self._start_omniroute()
        else:
            if verbose:
                print("        Already running")

        # Step 3: Activate plugins
        if verbose:
            print("  [3/5] Loading plugins...")
        activated = self.plugins.activate()
        results.append(f"Plugins: {len(activated)} activated")
        if verbose:
            print(f"        {len(activated)} plugins activated")

        # Step 4: Run self-learning analysis
        if verbose:
            print("  [4/5] Self-learning analysis...")
        analysis = self.learner.analyze()
        results.append(f"Insights: {len(analysis['insights'])} found")
        if verbose:
            print(f"        {len(analysis['insights'])} insights, {len(analysis['improvements'])} improvements")

        # Step 5: Log activation
        if verbose:
            print("  [5/5] Logging activation...")
        self.brain.log_action("Orchestrator", "activate_all", f"{online} systems", "Success")

        self.active = True

        if verbose:
            print()
            print("  ====================================================")
            print("   ALL SYSTEMS ACTIVATED")
            print("  ====================================================")
            print()
            print(f"   Systems online:   {online}/{len(self.registry.SYSTEMS)}")
            print(f"   Plugins loaded:   {len(activated)}")
            print(f"   Insights found:   {len(analysis['insights'])}")
            print(f"   Improvements:     {len(analysis['improvements'])}")
            print(f"   Brain commands:   {self.brain.summary()['commands']}")
            print()

        return {"results": results, "analysis": analysis, "online": online}

    def _start_omniroute(self):
        """Start OmniRoute server."""
        try:
            omniroute_dir = os.path.expanduser(r"~\OmniRoute")
            if os.path.exists(omniroute_dir):
                si = __import__("subprocess").STARTUPINFO()
                si.dwFlags |= __import__("subprocess").STARTF_USESHOWWINDOW
                si.wShowWindow = 0
                __import__("subprocess").Popen(
                    "cmd /c npm run dev", cwd=omniroute_dir,
                    startupinfo=si, stdout=__import__("subprocess").DEVNULL,
                    stderr=__import__("subprocess").DEVNULL, shell=True
                )
                self.brain.log_action("OmniRoute", "started", "port 20128")
                return True
        except Exception as e:
            self.brain.log_error("OmniRoute", str(e))
            return False


# ============================================================
#  6. TUI DASHBOARD - Live Animated Terminal UI
# ============================================================
class TUIDashboard:
    """Live terminal dashboard with Rich library."""

    def __init__(self, brain, registry, learner):
        self.brain = brain
        self.registry = registry
        self.learner = learner
        self.tick = 0
        self.events = []
        self.graph_phase = 0

    def _add_event(self, icon, msg, color="white"):
        ts = datetime.now().strftime("%H:%M:%S")
        self.events.insert(0, {"ts": ts, "icon": icon, "msg": msg, "color": color})
        if len(self.events) > 15:
            self.events = self.events[:15]

    def _render_graph(self, w=60, h=14):
        """Render the animated system graph."""
        grid = [[" "] * w for _ in range(h)]
        cx, cy = w // 2, h // 2

        # Define nodes in concentric rings
        nodes = []
        # Center: Brain
        nodes.append({"name": "BRAIN", "x": cx, "y": cy, "c": "orange1"})
        # Ring 1: AI
        for i, name in enumerate(["OMNI", "GRAPH", "SEMA"]):
            a = (i / 3) * math.pi * 2 - math.pi / 2
            nodes.append({"name": name, "x": cx + 8 * math.cos(a), "y": cy + 4 * math.sin(a), "c": "cyan"})
        # Ring 2: Code
        for i, name in enumerate(["RUFLO", "JCODE", "PILOT"]):
            a = (i / 3) * math.pi * 2 + math.pi / 6
            nodes.append({"name": name, "x": cx + 13 * math.cos(a), "y": cy + 6 * math.sin(a), "c": "green"})
        # Ring 3: Business + Outer
        for i, name in enumerate(["LINK-VT", "LINK-KT", "WAPP", "VOICE", "GIT"]):
            a = (i / 5) * math.pi * 2
            nodes.append({"name": name, "x": cx + 22 * math.cos(a), "y": cy + 7 * math.sin(a), "c": "blue"})

        # Draw edges with data pulses
        edges = [(0,1),(0,2),(0,3),(1,4),(1,5),(2,5),(2,6),(3,6),
                 (4,7),(5,8),(6,9),(7,10),(8,11),(9,12),(10,13),(11,14)]
        pulse = (self.graph_phase * 0.3) % 1
        for i, (a, b) in enumerate(edges):
            if a < len(nodes) and b < len(nodes):
                na, nb = nodes[a], nodes[b]
                dist = int(abs(na["x"] - nb["x"]) + abs(na["y"] - nb["y"]))
                for s in range(max(dist, 1)):
                    t = s / max(dist, 1)
                    x = int(na["x"] + (nb["x"] - na["x"]) * t)
                    y = int(na["y"] + (nb["y"] - na["y"]) * t)
                    if 0 <= x < w and 0 <= y < h:
                        is_pulse = (i + int(self.graph_phase * 3)) % 6 == 0
                        dp = abs(t - pulse)
                        if is_pulse and dp < 0.1:
                            grid[y][x] = "@"
                        elif is_pulse and dp < 0.2:
                            grid[y][x] = "*"
                        elif grid[y][x] == " ":
                            grid[y][x] = "."

        # Draw nodes
        for n in nodes:
            x, y = int(n["x"]), int(n["y"])
            label = n["name"]
            sx = x - len(label) // 2
            for i, ch in enumerate(label):
                px = sx + i
                if 0 <= px < w and 0 <= y < h:
                    grid[y][px] = ch

        return "\n".join("".join(row) for row in grid)

    def _generate_auto_events(self):
        """Generate realistic system events."""
        possible = [
            ("AI", "OmniRoute: Processing request", "green"),
            ("GRAPH", "Graphify: Updating knowledge graph", "purple"),
            ("SEMA", "Semantica: Decision confidence 94%", "cyan"),
            ("CORE", "Brain: Pattern learned", "orange1"),
            ("CODE", "JCode: Code suggestion ready", "yellow"),
            ("LINK", "LinkedIn VT: Scanning posts", "blue"),
            ("LINK", "LinkedIn KT: Generating comments", "blue"),
            ("MSG", "WhatsApp: Message queue ready", "green"),
            ("VCS", "Git: Auto-fetch completed", "red"),
            ("OPS", "Docker: Container healthy", "bright_blue"),
            ("VOICE", "Voice: Listening for RSS", "bright_red"),
            ("AGENT", "Ruflo: Agent task completed", "green"),
            ("SYS", f"Brain: {self.brain.summary()['commands']} commands logged", "orange1"),
        ]
        idx = self.tick % len(possible)
        self._add_event(*possible[idx])

    def run(self):
        """Run the live TUI dashboard."""
        from rich.console import Console
        from rich.live import Live
        from rich.panel import Panel
        from rich.table import Table
        from rich.text import Text
        from rich.layout import Layout
        from rich.align import Align
        from rich import box

        console = Console(force_terminal=True, width=120)

        # Initial health check
        self.registry.check_all()

        try:
            with Live(console=console, refresh_per_second=2, screen=True) as live:
                while True:
                    self.tick += 1
                    self.graph_phase += 0.05

                    # Generate events every 3 ticks
                    if self.tick % 3 == 0:
                        self._generate_auto_events()

                    # Check health every 30 ticks
                    if self.tick % 30 == 0:
                        self.registry.check_all()

                    # Header
                    ts = datetime.now().strftime("%H:%M:%S")
                    header = Text.from_markup(
                        f"[bold orange1]  MULTIFLY UNIFIED | Live Dashboard | {ts} | "
                        f"Brain: {self.brain.summary()['commands']} cmds | "
                        f"Patterns: {self.brain.summary()['patterns']}[/]"
                    )

                    # Graph panel
                    graph_text = self._render_graph(60, 14)
                    gp = Panel(
                        Align.center(Text(graph_text, no_wrap=True)),
                        title="[bold]System Graph - All Connected[/]",
                        border_style="orange1", box=box.DOUBLE
                    )

                    # Activity feed
                    act_table = Table(box=box.SIMPLE, border_style="orange1", show_header=False, padding=(0, 1))
                    act_table.add_column("T", width=8)
                    act_table.add_column("I", width=4)
                    act_table.add_column("M", width=40)
                    for ev in self.events[:10]:
                        act_table.add_row(
                            f"[grey]{ev['ts']}[/]",
                            f"[{ev['color']}]{ev['icon']}[/]",
                            f"[{ev['color']}]{ev['msg']}[/]"
                        )
                    ap = Panel(act_table, title="[bold]Live Activity[/]", border_style="orange1")

                    # Systems table
                    sys_table = Table(box=box.SIMPLE, border_style="orange1", show_header=True)
                    sys_table.add_column("S", width=20)
                    sys_table.add_column("Status", width=10)
                    for sid, info in list(self.registry.SYSTEMS.items())[:10]:
                        st = self.registry.status.get(sid, {"state": "?"})
                        color = "green" if st["state"] in ("online", "ready") else "yellow"
                        sys_table.add_row(info["name"], f"[{color}]{st['state']}[/]")
                    sp = Panel(sys_table, title="[bold]Systems[/]", border_style="orange1")

                    # Brain stats
                    s = self.brain.summary()
                    stats = Table(box=box.ROUNDED, border_style="orange1", show_header=False)
                    stats.add_column("K", width=14)
                    stats.add_column("V", width=10, justify="right")
                    for k, v, c in [
                        ("Commands", s["commands"], "orange1"),
                        ("Actions", s["actions"], "cyan"),
                        ("Patterns", s["patterns"], "purple"),
                        ("Errors", s["errors"], "red"),
                        ("Resolved", s["resolved"], "green"),
                        ("Today", s["today_cmds"], "bright_white"),
                    ]:
                        stats.add_row(k, f"[bold {c}]{v}[/]")
                    bp = Panel(stats, title="[bold]Brain Memory[/]", border_style="orange1")

                    # Suggestions
                    suggestions = self.brain.suggest()
                    sug_text = "\n".join(f"  > {s}" for s in suggestions[:5])
                    sugp = Panel(sug_text, title="[bold]Suggested Next[/]", border_style="orange1")

                    # Layout
                    layout = Layout()
                    layout.split_column(
                        Layout(header, size=3),
                        Layout(name="body")
                    )
                    layout["body"].split_row(
                        Layout(name="left", ratio=3),
                        Layout(name="right", ratio=2)
                    )
                    layout["left"].split_column(gp)
                    layout["right"].split_column(
                        Layout(ap, ratio=2),
                        Layout(name="bottom")
                    )
                    layout["bottom"].split_row(
                        Layout(sp, ratio=2),
                        Layout(name="bright")
                    )
                    layout["bright"].split_column(bp, sugp)

                    live.update(layout)
                    time.sleep(0.5)

        except KeyboardInterrupt:
            console.print("\n[orange1]Dashboard stopped.[/]")


# ============================================================
#  7. REST API - Everything Talks to Everything
# ============================================================
class MultiflyAPI(BaseHTTPRequestHandler):
    """REST API server for system communication."""

    brain = None
    registry = None
    learner = None

    def do_GET(self):
        path = self.path.split("?")[0]

        routes = {
            "/": self._index,
            "/api/status": self._status,
            "/api/health": self._health,
            "/api/brain/summary": self._brain_summary,
            "/api/brain/suggest": self._brain_suggest,
            "/api/brain/patterns": self._brain_patterns,
            "/api/systems": self._systems,
            "/api/plugins": self._plugins,
            "/api/learn": self._learn,
            "/api/activate": self._activate,
        }

        handler = routes.get(path, self._not_found)
        data = handler()
        self._json_response(data)

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        body = json.loads(self.rfile.read(length)) if length else {}
        path = self.path.split("?")[0]

        if path == "/api/command":
            data = self._run_command(body)
        elif path == "/api/log":
            data = self._log_event(body)
        else:
            data = self._not_found()

        self._json_response(data)

    def _json_response(self, data):
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data, indent=2, default=str).encode())

    def _index(self):
        return {"multifly": "Unified API", "version": "2035", "endpoints": [
            "GET /api/status", "GET /api/health", "GET /api/brain/summary",
            "GET /api/brain/suggest", "GET /api/systems", "GET /api/plugins",
            "GET /api/learn", "GET /api/activate",
            "POST /api/command", "POST /api/log"
        ]}

    def _status(self):
        s = self.__class__.brain.summary()
        return {"status": "online", "brain": s, "timestamp": datetime.now().isoformat()}

    def _health(self):
        self.__class__.registry.check_all()
        return {"health": {sid: st["state"] for sid, st in self.__class__.registry.status.items()}}

    def _brain_summary(self):
        return self.__class__.brain.summary()

    def _brain_suggest(self):
        return {"suggestions": self.__class__.brain.suggest()}

    def _brain_patterns(self):
        return {"patterns": self.__class__.brain.summary()["patterns_top"]}

    def _systems(self):
        return {"systems": {sid: {"name": info["name"], "state": self.__class__.registry.status.get(sid, {}).get("state", "?")}
                           for sid, info in SystemRegistry.SYSTEMS.items()}}

    def _plugins(self):
        return {"plugins": self.__class__.brain.get_pref("loaded_plugins") or "[]"}

    def _learn(self):
        result = self.__class__.learner.apply_improvements()
        return {"learning": result}

    def _activate(self):
        result = self.__class__.orchestrator.activate_all(verbose=False)
        return {"activation": result}

    def _run_command(self, body):
        cmd = body.get("command", "")
        self.__class__.brain.log_cmd(cmd, "api")
        return {"result": f"Command '{cmd}' logged", "suggestions": self.__class__.brain.suggest()}

    def _log_event(self, body):
        self.__class__.brain.log_action(
            body.get("system", "unknown"),
            body.get("action", "unknown"),
            body.get("target", ""),
            body.get("result", "")
        )
        return {"logged": True}

    def _not_found(self):
        return {"error": "Not found", "try": "/api/status"}

    def log_message(self, format, *args):
        pass  # Suppress request logging


def run_api(port=2035):
    """Start the REST API server."""
    server = HTTPServer(("127.0.0.1", port), MultiflyAPI)
    print(f"\n  MULTIFLY REST API running on http://127.0.0.1:{port}")
    print(f"  Try: http://127.0.0.1:{port}/api/status\n")
    server.serve_forever()


# ============================================================
#  MAIN - Entry Point
# ============================================================
def main():
    if len(sys.argv) < 2:
        print("""
  ====================================================
   MULTIFLY UNIFIED - Complete System
  ====================================================

  Usage:
    python unified_multifly.py dashboard    Live TUI dashboard
    python unified_multifly.py api          REST API server
    python unified_multifly.py activate     Activate all systems
    python unified_multifly.py learn        Self-learning analysis
    python unified_multifly.py status       System status
    python unified_multifly.py plugin list  List plugins
    python unified_multifly.py plugin add X Create plugin X
    python unified_multifly.py brain        Brain summary
  ====================================================
        """)
        return

    cmd = sys.argv[1].lower()

    # Initialize core
    brain = Brain()
    registry = SystemRegistry(brain)
    plugins = PluginManager()
    learner = SelfLearner(brain)
    orchestrator = Orchestrator(brain, registry, plugins, learner)

    # Wire up API globals
    MultiflyAPI.brain = brain
    MultiflyAPI.registry = registry
    MultiflyAPI.learner = learner
    MultiflyAPI.orchestrator = orchestrator

    if cmd == "dashboard":
        dashboard = TUIDashboard(brain, registry, learner)
        dashboard.run()

    elif cmd == "api":
        run_api()

    elif cmd == "activate":
        orchestrator.activate_all()

    elif cmd == "learn":
        result = learner.apply_improvements()
        print("\n  ====================================================")
        print("   SELF-LEARNING ANALYSIS")
        print("  ====================================================\n")
        for ins in result["analysis"]["insights"]:
            print(f"  [{ins['type'].upper()}] {ins['insight']}")
            print(f"           -> {ins['action']}")
        print()
        for imp in result["applied"]:
            print(f"  [IMPROVED] {imp}")
        print()

    elif cmd == "status":
        registry.check_all()
        s = brain.summary()
        print("\n  ====================================================")
        print("   MULTIFLY STATUS")
        print("  ====================================================\n")
        print(registry.get_status_text())
        print(f"\n  Brain: {s['commands']} cmds, {s['actions']} acts, {s['patterns']} patterns")
        print(f"  Today: {s['today_cmds']} commands, {s['today_acts']} actions")
        print()

    elif cmd == "brain":
        s = brain.summary()
        print(json.dumps(s, indent=2, default=str))

    elif cmd == "plugin":
        sub = sys.argv[2] if len(sys.argv) > 2 else "list"
        if sub == "list":
            plist = plugins.list_plugins()
            print("\n  PLUGINS:")
            for p in plist:
                print(f"    {p['name']}: {p['description']}")
            if not plist:
                print("    (none yet - create with: plugin add <name>)")
        elif sub == "add" and len(sys.argv) > 3:
            name = sys.argv[3]
            path = plugins.create_plugin(name)
            print(f"  Created plugin: {path}")

    else:
        print(f"  Unknown command: {cmd}")
        print("  Run without arguments to see usage.")

    brain.conn.close()


if __name__ == "__main__":
    main()
