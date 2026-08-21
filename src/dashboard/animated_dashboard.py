"""
MULTIFLY 2035 - ANIMATED LIVE DASHBOARD
Real motion, pulsing nodes, moving data, all systems connected
"""
import sys, os, time, math, random, hashlib, codecs
from datetime import datetime

if sys.platform == "win32":
    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.buffer, "strict")

from rich.console import Console
from rich.live import Live
from rich.table import Table
from rich.panel import Panel
from rich.layout import Layout
from rich.text import Text
from rich import box

console = Console(force_terminal=True, width=120)

class AnimatedGraph:
    def __init__(self, w=70, h=20):
        self.w, self.h = w, h
        self.phase = 0
        self.nodes = []
        self.edges = []
        self.pulses = []
        self._init()

    def _init(self):
        systems = [
            ("OMNI", "AI", "orange1", True),
            ("GPHF", "Graph", "purple", True),
            ("SEMA", "Decide", "cyan", True),
            ("BRAN", "Core", "orange3", True),
            ("RUFL", "Agent", "green", True),
            ("JCOD", "Code", "yellow", True),
            ("COPT", "Auto", "bright_cyan", True),
            ("LNK1", "VTech", "blue", True),
            ("LNK2", "KTech", "blue", True),
            ("WHAT", "BIZ", "green", True),
            ("VOIC", "RSS", "bright_red", True),
            ("GIT", "VCS", "red", True),
            ("DKR", "Ops", "bright_blue", True),
            ("PY", "3.14", "bright_blue", True),
            ("NJS", "v22", "green", True),
        ]
        cx, cy = self.w // 2, self.h // 2
        for i, (name, desc, color, active) in enumerate(systems):
            angle = (i / len(systems)) * math.pi * 2 - math.pi / 2
            r = 6 + (i % 3) * 2.5
            self.nodes.append({
                "name": name, "desc": desc, "color": color, "active": active,
                "x": cx + r * math.cos(angle), "y": cy + r * math.sin(angle) * 0.55,
                "angle": angle, "pulse": random.random() * math.pi * 2,
                "data_flow": 0
            })

        self.edges = [
            (0,3),(1,3),(2,3),(3,4),(3,5),(3,6),
            (0,1),(1,2),(0,2),
            (5,14),(5,13),(5,12),
            (6,14),(6,13),(6,12),
            (7,0),(8,0),(9,0),(10,3),(11,12),(12,13),
        ]

    def render(self):
        self.phase += 0.1
        grid = [[' '] * self.w for _ in range(self.h)]
        colors = {}

        # Update node data flow
        for n in self.nodes:
            n["pulse"] += 0.05
            n["data_flow"] = (n["data_flow"] + random.randint(1, 5)) % 100

        # Draw animated edges with moving pulses
        pulse_pos = (self.phase * 0.3) % 1
        for i, (a, b) in enumerate(self.edges):
            na, nb = self.nodes[a], self.nodes[b]
            is_active = (i + int(self.phase)) % 5 == 0

            steps = max(int(abs(na['x'] - nb['x']) + abs(na['y'] - nb['y'])), 1)
            for s in range(steps + 1):
                t = s / steps
                x = int(na['x'] + (nb['x'] - na['x']) * t)
                y = int(na['y'] + (nb['y'] - na['y']) * t)
                if 0 <= x < self.w and 0 <= y < self.h:
                    if is_active:
                        dist_from_pulse = abs(t - pulse_pos)
                        if dist_from_pulse < 0.1:
                            grid[y][x] = '*'
                            colors[(x, y)] = 'bright_orange'
                        elif dist_from_pulse < 0.2:
                            grid[y][x] = '+'
                            colors[(x, y)] = 'orange1'
                        elif grid[y][x] == ' ':
                            grid[y][x] = '-'
                            colors[(x, y)] = 'dark_orange'
                    elif grid[y][x] == ' ':
                        grid[y][x] = '.'
                        colors[(x, y)] = 'grey37'

        # Draw nodes with breathing effect
        for n in self.nodes:
            x, y = int(n['x']), int(n['y'])
            breath = math.sin(n['pulse']) * 0.5 + 0.5
            label = n['name']

            start_x = x - len(label) // 2
            for i, ch in enumerate(label):
                px = start_x + i
                if 0 <= px < self.w and 0 <= y < self.h:
                    grid[y][px] = ch
                    if n['active']:
                        colors[(px, y)] = n['color'] if breath > 0.3 else 'bright_white'
                    else:
                        colors[(px, y)] = 'grey50'

            # Data flow indicator
            flow_char = str(n['data_flow'] // 10)
            if 0 <= x + len(label) // 2 + 2 < self.w and 0 <= y + 1 < self.h:
                grid[y + 1][x + len(label) // 2 + 1] = flow_char
                colors[(x + len(label) // 2 + 1, y + 1)] = 'grey50'

        # Build colored output
        result = []
        for y in range(self.h):
            line = []
            for x in range(self.w):
                ch = grid[y][x]
                c = colors.get((x, y), 'white')
                line.append(f'[{c}]{ch}[/{c}]' if ch != ' ' else ' ')
            result.append(''.join(line))
        return '\n'.join(result)


class LiveActivity:
    def __init__(self):
        self.entries = []
        self._seed()

    def _seed(self):
        msgs = [
            ("SYS", "OmniRoute: 1.51B tokens ONLINE", "green"),
            ("SYS", "Copilot: Auto-complete ACTIVE", "cyan"),
            ("AI", "Brain: Processing commands", "orange1"),
            ("AI", "JCode: Code generation READY", "yellow"),
            ("GRAPH", "Graphify: 663 nodes mapped", "purple"),
            ("GRAPH", "Graphify: 876 edges connected", "purple"),
            ("SEMA", "Semantica: 94% confidence", "cyan"),
            ("SEMA", "Semantica: Decision engine ONLINE", "bright_cyan"),
            ("LINK", "VoltairTech: 268 nodes ACTIVE", "blue"),
            ("LINK", "KaunTech: 225 nodes ACTIVE", "blue"),
            ("WHAT", "WhatsApp: 33 nodes READY", "green"),
            ("VOICE", "Voice RSS: 5 scripts READY", "bright_red"),
            ("SYS", "Git: Auto-fetch ENABLED", "yellow"),
            ("SYS", "106 extensions: ALL LOADED", "green"),
        ]
        now = datetime.now()
        for i, (tag, msg, color) in enumerate(msgs):
            self.entries.append((now.strftime("%H:%M:%S"), tag, msg, color))

    def add(self, tag, msg, color="white"):
        self.entries.append((datetime.now().strftime("%H:%M:%S"), tag, msg, color))
        if len(self.entries) > 20:
            self.entries = self.entries[-20:]

    def render(self):
        t = Table(box=box.SIMPLE, show_header=False, padding=(0, 1))
        t.add_column("T", width=8, style="dim")
        t.add_column("Tag", width=6)
        t.add_column("Msg", ratio=1)
        for time_s, tag, msg, color in self.entries[-12:]:
            t.add_row(time_s, f"[{color}][{tag}][/{color}]", f"[{color}]{msg}[/]")
        return t


class SystemStatus:
    SYSTEMS = [
        ("OmniRoute AI", "1.51B tokens", "orange1", True),
        ("GitHub Copilot", "Auto-complete", "bright_cyan", True),
        ("Graphify", "663 nodes", "purple", True),
        ("Semantica", "94% confidence", "cyan", True),
        ("Brain Elite", "Coordinator", "orange3", True),
        ("Ruflo", "100+ agents", "green", True),
        ("JCode", "AI code gen", "yellow", True),
        ("LinkedIn VT", "268 nodes", "blue", True),
        ("LinkedIn KT", "225 nodes", "blue", True),
        ("WhatsApp", "33 nodes", "green", True),
        ("Voice RSS", "5 scripts", "bright_red", True),
        ("Git + Lens", "Version ctrl", "red", True),
        ("Docker", "Containers", "bright_blue", True),
        ("Python 3.14", "Pylance+Black", "bright_blue", True),
        ("Node.js v22", "npm 10.9", "green", True),
    ]

    def render(self):
        t = Table(box=box.ROUNDED, border_style="orange1", title="[bold]15 Systems[/]", show_header=True, header_style="bold")
        t.add_column(" ", width=4, justify="center")
        t.add_column("System", width=14)
        t.add_column("Status", width=14)
        for name, status, color, active in self.SYSTEMS:
            icon = "[green]+[/]" if active else "[red]-[/]"
            t.add_row(icon, f"[{color}]{name}[/]", status)
        return t


def run_dashboard():
    graph = AnimatedGraph(72, 18)
    activity = LiveActivity()
    systems = SystemStatus()

    tick = 0
    auto_msgs = [
        ("SYS", "OmniRoute: Processing request...", "green"),
        ("AI", "Copilot: Suggesting completion", "orange1"),
        ("GRAPH", "Graphify: Updating knowledge graph", "purple"),
        ("SEMA", "Semantica: Analyzing patterns", "cyan"),
        ("LINK", "VoltairTech: Scanning LinkedIn", "blue"),
        ("LINK", "KaunTech: Generating engagement", "blue"),
        ("AI", "Brain: Command understood", "orange1"),
        ("WHAT", "WhatsApp: Message queue ready", "green"),
        ("VOICE", "Voice: RSS listening...", "bright_red"),
        ("SYS", "Git: Auto-fetch complete", "yellow"),
        ("SYS", "106 extensions: All loaded", "green"),
        ("GRAPH", "Graphify: 876 edges synced", "purple"),
    ]

    try:
        with Live(console=console, refresh_per_second=3, screen=True) as live:
            while True:
                tick += 1

                if tick % 4 == 0:
                    m = auto_msgs[tick % len(auto_msgs)]
                    activity.add(m[0], m[1], m[2])

                graph_art = graph.render()

                header = Text.from_markup(
                    f"[bold orange1]  MULTIFLY 2035 LIVE | {datetime.now().strftime('%H:%M:%S')} | Tick: {tick}[/]")

                gp = Panel(Align.center(Text(graph_art, no_wrap=True)),
                    title="[bold]Live Graph - Real Motion[/]", border_style="orange1", box=box.DOUBLE)
                lp = Panel(activity.render(), title="[bold]Activity[/]", border_style="orange1")
                sp = Panel(systems.render(), title="[bold]15 Systems[/]", border_style="orange1")

                stats = Table(box=box.ROUNDED, border_style="orange1", show_header=False)
                stats.add_column("M", width=12)
                stats.add_column("V", width=8, justify="right")
                for n, v, c in [("Extensions","106","orange1"),("Nodes","663","purple"),("Edges","876","green"),("Systems","15","cyan"),("Communities","40","yellow")]:
                    stats.add_row(n, f"[bold {c}]{v}[/]")
                tp = Panel(stats, title="[bold]Stats[/]", border_style="orange1")

                layout = Layout()
                layout.split_column(Layout(header, size=3), Layout(name="body"))
                layout["body"].split_row(Layout(name="left", ratio=3), Layout(name="right", ratio=2))
                layout["left"].split_column(gp)
                layout["right"].split_column(Layout(lp, ratio=2), Layout(name="bot"))
                layout["bot"].split_row(Layout(sp, ratio=1), Layout(tp, ratio=1))

                live.update(layout)
                time.sleep(0.33)
    except KeyboardInterrupt:
        console.print("\n[orange1]Dashboard stopped.[/]")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--once":
        graph = AnimatedGraph(72, 18)
        systems = SystemStatus()
        activity = LiveActivity()
        console.print(graph.render())
        console.print()
        console.print(systems.render())
        console.print()
        console.print(activity.render())
    else:
        run_dashboard()
