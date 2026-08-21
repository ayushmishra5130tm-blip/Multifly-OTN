"""
MULTIFLY LIVE DASHBOARD - Pure Python Terminal UI
Real-time graph engineering, system monitor, Semantica + Graphify
No HTML. No browser. Pure developer power. ASCII only.
"""
import sys, os, time, json, math, hashlib, codecs
from datetime import datetime

# Force UTF-8 output on Windows
if sys.platform == "win32":
    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.buffer, "strict")
    sys.stderr = codecs.getwriter("utf-8")(sys.stderr.buffer, "strict")
    os.environ.setdefault("PYTHONIOENCODING", "utf-8")

from rich.console import Console
from rich.live import Live
from rich.table import Table
from rich.panel import Panel
from rich.layout import Layout
from rich.text import Text
from rich.columns import Columns
from rich.align import Align
from rich import box

console = Console(force_terminal=True)

# ============================================
# GRAPH ENGINE - ASCII knowledge graph
# ============================================
class GraphEngine:
    def __init__(self, width=60, height=16):
        self.width = width
        self.height = height
        self.nodes = []
        self.edges = []
        self.phase = 0
        self._init_nodes()

    def _init_nodes(self):
        systems = [
            ("O-R", "AI", "orange1"),
            ("GPH", "Graph", "purple"),
            ("SEM", "Decide", "cyan"),
            ("BRN", "Core", "orange3"),
            ("RFL", "Agent", "green"),
            ("JCD", "Code", "yellow"),
            ("CPT", "Auto", "bright_cyan"),
            ("LIN", "Biz", "blue"),
            ("GIT", "VCS", "red"),
            ("DKR", "Ops", "bright_blue"),
            ("PY", "3.14", "bright_blue"),
            ("NJS", "v22", "green"),
            ("RCT", "UI", "bright_cyan"),
        ]
        cx, cy = self.width // 2, self.height // 2
        for i, (name, desc, color) in enumerate(systems):
            angle = (i / len(systems)) * math.pi * 2 - math.pi / 2
            r = 5 + (i % 3) * 2
            x = int(cx + r * math.cos(angle))
            y = int(cy + r * math.sin(angle) * 0.55)
            self.nodes.append({"name": name, "desc": desc, "color": color, "x": x, "y": y, "angle": angle})

        self.edges = [
            (0,3),(1,3),(2,3),(4,3),(5,3),(6,3),
            (0,1),(1,2),(0,2),
            (5,10),(5,11),(5,12),
            (6,10),(6,11),(6,12),
            (8,9),(4,0),(7,0),
        ]

    def render(self):
        self.phase += 0.12
        grid = [[' ' for _ in range(self.width)] for _ in range(self.height)]
        colors = {}

        pulse_idx = int(self.phase) % len(self.edges)
        for i, (a, b) in enumerate(self.edges):
            na, nb = self.nodes[a], self.nodes[b]
            is_active = i == pulse_idx
            steps = max(abs(na['x'] - nb['x']), abs(na['y'] - nb['y']), 1)
            for s in range(steps + 1):
                t = s / steps
                x = int(na['x'] + (nb['x'] - na['x']) * t)
                y = int(na['y'] + (nb['y'] - na['y']) * t)
                if 0 <= x < self.width and 0 <= y < self.height:
                    if is_active and s == int(steps * (self.phase % 1)):
                        grid[y][x] = '*'
                        colors[(x, y)] = 'bright_orange'
                    elif grid[y][x] == ' ':
                        grid[y][x] = '.'
                        colors[(x, y)] = 'dark_orange'

        for n in self.nodes:
            x, y = n['x'], n['y']
            pulse = math.sin(n['angle'] + self.phase) > 0
            label = n['name']
            start_x = x - len(label) // 2
            for i, ch in enumerate(label):
                px = start_x + i
                if 0 <= px < self.width and 0 <= y < self.height:
                    grid[y][px] = ch
                    colors[(px, y)] = n['color'] if pulse else 'bright_white'

        result = []
        for y in range(self.height):
            line = []
            for x in range(self.width):
                ch = grid[y][x]
                c = colors.get((x, y), 'white')
                if ch != ' ':
                    line.append(f'[{c}]{ch}[/{c}]')
                else:
                    line.append(' ')
            result.append(''.join(line))
        return '\n'.join(result)


# ============================================
# SYSTEMS
# ============================================
class SystemMonitor:
    SYSTEMS = [
        ("OmniRoute AI", "1.51B tokens", "orange1", True),
        ("GitHub Copilot", "Auto-complete", "bright_cyan", True),
        ("Graphify", "Knowledge graphs", "purple", True),
        ("Semantica", "Decision engine", "cyan", True),
        ("Brain Elite", "Coordinator", "orange3", True),
        ("Ruflo", "100+ AI agents", "green", True),
        ("JCode", "AI code gen", "yellow", True),
        ("Git + GitLens", "Version control", "red", True),
        ("Python 3.14", "Pylance+Black", "bright_blue", True),
        ("Node.js v22", "npm 10.9", "green", True),
        ("LinkedIn", "Automation", "blue", True),
        ("Docker", "Containers", "bright_blue", True),
        ("Voice RSS", "Commands", "bright_red", True),
    ]

    def render(self):
        t = Table(box=box.ROUNDED, border_style="orange1", title="[bold]Active Systems[/]", show_header=True, header_style="bold bright_white")
        t.add_column(" ", width=4, justify="center")
        t.add_column("System", width=16)
        t.add_column("Role", width=16)
        for name, role, color, active in self.SYSTEMS:
            icon = "[green]+[/]" if active else "[red]-[/]"
            t.add_row(icon, f"[{color}]{name}[/]", role)
        return t


# ============================================
# ACTIVITY FEED
# ============================================
class ActivityFeed:
    def __init__(self):
        self.entries = []
        self._seed()

    def _seed(self):
        events = [
            ("SYS", "OmniRoute: 1.51B tokens ready", "green"),
            ("SYS", "Copilot: Auto-complete active", "cyan"),
            ("AI", "Brain: Understanding intent", "orange1"),
            ("AI", "JCode: Generating structure", "yellow"),
            ("GRAPH", "Graphify: 156 nodes mapped", "purple"),
            ("GRAPH", "Graphify: 423 edges connected", "purple"),
            ("SEMA", "Semantica: Decision confidence 94%", "cyan"),
            ("SEMA", "Semantica: Provenance tracking", "bright_cyan"),
            ("SYS", "Git: Auto-fetch enabled", "yellow"),
            ("SYS", "Prettier: Format on save active", "green"),
        ]
        now = datetime.now()
        for i, (tag, msg, color) in enumerate(events):
            self.entries.append((now.strftime("%H:%M:%S"), tag, msg, color))

    def add(self, tag, msg, color="white"):
        self.entries.append((datetime.now().strftime("%H:%M:%S"), tag, msg, color))
        if len(self.entries) > 30:
            self.entries = self.entries[-30:]

    def render(self):
        t = Table(box=box.SIMPLE, border_style="dim", show_header=False, padding=(0, 1))
        t.add_column("Time", width=8, style="dim")
        t.add_column("Tag", width=6)
        t.add_column("Message", ratio=1)
        for time_s, tag, msg, color in self.entries[-12:]:
            t.add_row(time_s, f"[{color}][{tag}][/{color}]", f"[{color}]{msg}[/]")
        return t


# ============================================
# STATS
# ============================================
class StatsPanel:
    STATS = [
        ("Extensions", "109", 100, "orange1"),
        ("Settings", "255", 100, "purple"),
        ("Tokens", "1.51B", 95, "green"),
        ("Graph Nodes", "156", 78, "cyan"),
        ("Graph Edges", "423", 85, "yellow"),
        ("Decisions", "89", 60, "bright_cyan"),
    ]

    def render(self):
        t = Table(box=box.ROUNDED, border_style="orange1", title="[bold]Performance[/]", show_header=True, header_style="bold bright_white")
        t.add_column("Metric", width=12)
        t.add_column("Value", width=8, justify="right")
        t.add_column("Bar", width=18)
        for name, value, pct, color in self.STATS:
            filled = int(pct / 5)
            bar = f"[{color}]{'#' * filled}[/][dim]{'.' * (18 - filled)}[/]"
            t.add_row(name, f"[bold {color}]{value}[/]", bar)
        return t


# ============================================
# SEMANTICA DECISIONS
# ============================================
class DecisionPanel:
    DECISIONS = [
        ("Architecture", "React + FastAPI. Microservices.", "94%", "orange1"),
        ("Testing", "Pytest + coverage >80%.", "91%", "cyan"),
        ("Performance", "Code splitting recommended.", "87%", "yellow"),
        ("Security", "JWT auth + rate limiting.", "96%", "green"),
        ("Deployment", "Vercel + edge functions.", "92%", "purple"),
    ]

    def render(self):
        t = Table(box=box.ROUNDED, border_style="cyan", title="[bold]Semantica[/]", show_header=True, header_style="bold bright_white")
        t.add_column("Decision", width=14)
        t.add_column("Analysis", ratio=1)
        t.add_column("Conf", width=5, justify="right")
        for title, desc, conf, color in self.DECISIONS:
            t.add_row(f"[{color}]{title}[/]", desc, f"[green]{conf}[/]")
        return t


# ============================================
# HEADER
# ============================================
def render_header():
    now = datetime.now().strftime("%H:%M:%S | %Y-%m-%d")
    return f"""[bold orange1]  ================================================================
     MULTIFLY LIVE - Graph Engineering Dashboard
     {now}
  ================================================================[/]"""


# ============================================
# MAIN LOOP
# ============================================
def run_dashboard():
    graph = GraphEngine(width=62, height=16)
    systems = SystemMonitor()
    feed = ActivityFeed()
    stats = StatsPanel()
    decisions = DecisionPanel()

    msgs = [
        ("SYS", "OmniRoute: Processing...", "green"),
        ("AI", "Copilot: Suggesting completion", "orange1"),
        ("GRAPH", "Graphify: Updating graph", "purple"),
        ("SEMA", "Semantica: Analyzing patterns", "cyan"),
        ("AI", "Brain: Command understood", "orange1"),
        ("GRAPH", "Graphify: 423 edges synced", "purple"),
        ("SEMA", "Semantica: Confidence 94%", "bright_cyan"),
        ("SYS", "Prettier: Format active", "green"),
        ("AI", "JCode: Component generated", "yellow"),
        ("SYS", "Git: Auto-fetch done", "yellow"),
    ]

    tick = 0
    try:
        with Live(console=console, refresh_per_second=2, screen=True) as live:
            while True:
                tick += 1
                if tick % 3 == 0:
                    m = msgs[tick % len(msgs)]
                    feed.add(m[0], m[1], m[2])

                graph_art = graph.render()

                graph_panel = Panel(Align.center(Text(graph_art, no_wrap=True)), title="[bold]Knowledge Graph[/]", border_style="orange1", box=box.DOUBLE)
                log_panel = Panel(feed.render(), title="[bold]Activity[/]", border_style="orange1")
                sys_panel = Panel(systems.render(), title="[bold]Systems[/]", border_style="orange1")
                stats_panel = Panel(stats.render(), title="[bold]Stats[/]", border_style="orange1")
                sema_panel = Panel(decisions.render(), title="[bold]Semantica[/]", border_style="cyan")

                layout = Layout()
                layout.split_column(
                    Layout(Text(render_header(), no_wrap=True), size=5),
                    Layout(name="body"),
                )
                layout["body"].split_row(
                    Layout(name="left", ratio=3),
                    Layout(name="right", ratio=2),
                )
                layout["left"].split_column(
                    Layout(graph_panel, ratio=3),
                    Layout(sema_panel, ratio=1),
                )
                layout["right"].split_column(
                    Layout(log_panel, ratio=2),
                    Layout(name="bottom"),
                )
                layout["bottom"].split_row(
                    Layout(sys_panel, ratio=1),
                    Layout(stats_panel, ratio=1),
                )

                live.update(layout)
                time.sleep(0.5)
    except KeyboardInterrupt:
        console.print("\n[orange1]  Dashboard stopped.[/]")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--once":
        graph = GraphEngine(width=62, height=16)
        systems = SystemMonitor()
        stats = StatsPanel()
        decisions = DecisionPanel()
        feed = ActivityFeed()
        console.print(render_header())
        console.print(graph.render())
        console.print()
        console.print(Columns([systems.render(), stats.render()]))
        console.print()
        console.print(decisions.render())
        console.print()
        console.print(feed.render())
    else:
        run_dashboard()
