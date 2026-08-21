"""
MULTIFLY 2035 - ONE UNIFIED GRAPH
All 15 systems connected, real motion, pure terminal
"""
import sys, os, time, math, random, codecs
from datetime import datetime

# Import brain database
try:
    sys.path.insert(0, os.path.dirname(__file__))
    from multifly_brain_db import get_brain
except ImportError:
    get_brain = None

if sys.platform == "win32":
    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.buffer, "strict")

from rich.console import Console
from rich.live import Live
from rich.table import Table
from rich.panel import Panel
from rich.layout import Layout
from rich.text import Text
from rich.columns import Columns
from rich.align import Align
from rich import box

console = Console(force_terminal=True, width=120)

class UnifiedGraph:
    def __init__(self, w=74, h=22):
        self.w, self.h = w, h
        self.phase = 0
        self.nodes = []
        self.edges = []
        self._init()

    def _init(self):
        # ALL 15 systems in ONE graph
        systems = [
            ("OMNIROUTE", "AI", "orange1", "1.51B tokens"),
            ("GRAPHIFY", "Graph", "purple", "274 nodes"),
            ("SEMANTICA", "Decide", "cyan", "94% conf"),
            ("BRAIN", "Core", "orange3", "Coordinator"),
            ("RUFLO", "Agent", "green", "100+ agents"),
            ("JCODE", "Code", "yellow", "AI code gen"),
            ("COPILOT", "Auto", "bright_cyan", "Complete"),
            ("LINKEDIN-VT", "BIZ", "blue", "268 nodes"),
            ("LINKEDIN-KT", "BIZ", "blue", "225 nodes"),
            ("WHATSAPP", "MSG", "green", "33 nodes"),
            ("VOICE-RSS", "CMD", "bright_red", "Speech"),
            ("GIT", "VCS", "red", "Version ctrl"),
            ("DOCKER", "OPS", "bright_blue", "Containers"),
            ("PYTHON", "3.14", "bright_blue", "Pylance"),
            ("NODEJS", "v22", "green", "npm 10.9"),
        ]

        cx, cy = self.w // 2, self.h // 2 - 1

        # Layer 1: Core (center)
        self.nodes.append({"name": "BRAIN", "desc": "CORE", "color": "orange3", "x": cx, "y": cy, "pulse": 0, "layer": 0})

        # Layer 2: AI ring
        ai_systems = systems[:3]
        for i, (name, desc, color, detail) in enumerate(ai_systems):
            angle = (i / 3) * math.pi * 2 - math.pi / 2
            r = 5
            self.nodes.append({"name": name, "desc": desc, "color": color, "x": cx + r * math.cos(angle), "y": cy + r * math.sin(angle) * 0.5, "pulse": random.random() * 6, "layer": 1, "detail": detail})

        # Layer 3: Code ring
        code_systems = systems[4:7]
        for i, (name, desc, color, detail) in enumerate(code_systems):
            angle = (i / 3) * math.pi * 2 + math.pi / 6
            r = 9
            self.nodes.append({"name": name, "desc": desc, "color": color, "x": cx + r * math.cos(angle), "y": cy + r * math.sin(angle) * 0.5, "pulse": random.random() * 6, "layer": 2, "detail": detail})

        # Layer 4: Business ring
        biz_systems = systems[7:10]
        for i, (name, desc, color, detail) in enumerate(biz_systems):
            angle = (i / 3) * math.pi * 2
            r = 13
            self.nodes.append({"name": name, "desc": desc, "color": color, "x": cx + r * math.cos(angle), "y": cy + r * math.sin(angle) * 0.5, "pulse": random.random() * 6, "layer": 3, "detail": detail})

        # Layer 5: Outer ring
        outer_systems = systems[10:]
        for i, (name, desc, color, detail) in enumerate(outer_systems):
            angle = (i / 5) * math.pi * 2 + math.pi / 5
            r = 16
            self.nodes.append({"name": name, "desc": desc, "color": color, "x": cx + r * math.cos(angle), "y": cy + r * math.sin(angle) * 0.5, "pulse": random.random() * 6, "layer": 4, "detail": detail})

        # ALL connections
        self.edges = [
            # Core to AI
            (0,1),(0,2),(0,3),
            # AI to Code
            (1,4),(1,5),(1,6),(2,4),(2,5),(3,6),
            # Code to Business
            (4,7),(4,8),(5,7),(5,9),(6,7),(6,8),
            # Business to Outer
            (7,10),(8,10),(9,10),(7,11),(8,12),(9,13),(7,14),(8,14),
            # Cross connections
            (1,6),(2,5),(4,9),(11,12),(13,14),
        ]

    def render(self):
        self.phase += 0.08
        grid = [[' '] * self.w for _ in range(self.h)]
        colors = {}

        # Update pulses
        for n in self.nodes:
            n["pulse"] += 0.04

        # Draw edges with moving data
        pulse_t = (self.phase * 0.4) % 1
        for i, (a, b) in enumerate(self.edges):
            na, nb = self.nodes[a], self.nodes[b]
            is_active = (i + int(self.phase * 2)) % 8 == 0

            steps = max(int(abs(na['x'] - nb['x']) + abs(na['y'] - nb['y'])), 1)
            for s in range(steps + 1):
                t = s / steps
                x = int(na['x'] + (nb['x'] - na['x']) * t)
                y = int(na['y'] + (nb['y'] - na['y']) * t)
                if 0 <= x < self.w and 0 <= y < self.h:
                    if is_active:
                        dist = abs(t - pulse_t)
                        if dist < 0.08:
                            grid[y][x] = '@'
                            colors[(x, y)] = 'bright_orange'
                        elif dist < 0.15:
                            grid[y][x] = '*'
                            colors[(x, y)] = 'orange1'
                        elif dist < 0.25:
                            grid[y][x] = '+'
                            colors[(x, y)] = 'dark_orange'
                        elif grid[y][x] == ' ':
                            grid[y][x] = '-'
                            colors[(x, y)] = 'grey37'
                    elif grid[y][x] == ' ':
                        grid[y][x] = '.'
                        colors[(x, y)] = 'grey27'

        # Draw nodes
        for n in self.nodes:
            x, y = int(n['x']), int(n['y'])
            breath = math.sin(n['pulse']) * 0.5 + 0.5
            label = n['name']

            # Center the label
            start_x = x - len(label) // 2
            for i, ch in enumerate(label):
                px = start_x + i
                if 0 <= px < self.w and 0 <= y < self.h:
                    grid[y][px] = ch
                    if breath > 0.4:
                        colors[(px, y)] = n['color']
                    else:
                        colors[(px, y)] = 'bright_white'

            # Show detail below node
            detail = n.get('detail', '')
            if detail and 0 <= y + 1 < self.h:
                detail_short = detail[:10]
                dx = x - len(detail_short) // 2
                for i, ch in enumerate(detail_short):
                    if 0 <= dx + i < self.w:
                        grid[y + 1][dx + i] = ch
                        colors[(dx + i, y + 1)] = 'grey50'

        # Build output
        result = []
        for y in range(self.h):
            line = []
            for x in range(self.w):
                ch = grid[y][x]
                c = colors.get((x, y), 'white')
                line.append(f'[{c}]{ch}[/{c}]' if ch != ' ' else ' ')
            result.append(''.join(line))
        return '\n'.join(result)


class SystemTable:
    SYSTEMS = [
        ("OmniRoute AI", "1.51B tokens", "orange1", True),
        ("Graphify", "274 nodes", "purple", True),
        ("Semantica", "94% confidence", "cyan", True),
        ("Brain Elite", "Coordinator", "orange3", True),
        ("Ruflo", "100+ agents", "green", True),
        ("JCode", "AI code gen", "yellow", True),
        ("Copilot", "Auto-complete", "bright_cyan", True),
        ("LinkedIn VT", "268 nodes", "blue", True),
        ("LinkedIn KT", "225 nodes", "blue", True),
        ("WhatsApp", "33 nodes", "green", True),
        ("Voice RSS", "Speech", "bright_red", True),
        ("Git + Lens", "Version ctrl", "red", True),
        ("Docker", "Containers", "bright_blue", True),
        ("Python 3.14", "Pylance+Black", "bright_blue", True),
        ("Node.js v22", "npm 10.9", "green", True),
    ]

    def render(self):
        t = Table(box=box.ROUNDED, border_style="orange1", title="[bold]15 Systems - ONE Graph[/]", show_header=True, header_style="bold")
        t.add_column(" ", width=3, justify="center")
        t.add_column("System", width=14)
        t.add_column("Status", width=14)
        for name, status, color, active in self.SYSTEMS:
            icon = "[green]+[/]" if active else "[red]-[/]"
            t.add_row(icon, f"[{color}]{name}[/]", status)
        return t


class ActivityLog:
    def __init__(self):
        self.entries = []
        self._seed()

    def _seed(self):
        msgs = [
            ("SYS", "OmniRoute: ONLINE", "green"),
            ("SYS", "Copilot: ACTIVE", "cyan"),
            ("AI", "Brain: Processing", "orange1"),
            ("GRAPH", "Graphify: 274 nodes", "purple"),
            ("SEMA", "Semantica: 94%", "cyan"),
            ("LINK", "VT: 268 nodes", "blue"),
            ("LINK", "KT: 225 nodes", "blue"),
            ("WHAT", "WhatsApp: 33 nodes", "green"),
            ("VOICE", "Voice: RSS ready", "bright_red"),
            ("SYS", "Git: Auto-fetch", "yellow"),
            ("SYS", "106 extensions", "green"),
            ("GRAPH", "336 edges synced", "purple"),
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


def run():
    graph = UnifiedGraph(74, 22)
    systems = SystemTable()
    activity = ActivityLog()

    auto_msgs = [
        ("SYS", "OmniRoute: Processing...", "green"),
        ("AI", "Copilot: Suggesting", "orange1"),
        ("GRAPH", "Graphify: Updating", "purple"),
        ("SEMA", "Semantica: Analyzing", "cyan"),
        ("LINK", "VT: Scanning LinkedIn", "blue"),
        ("LINK", "KT: Generating", "blue"),
        ("AI", "Brain: Command OK", "orange1"),
        ("WHAT", "WhatsApp: Ready", "green"),
        ("VOICE", "Voice: Listening", "bright_red"),
        ("SYS", "Git: Fetch done", "yellow"),
        ("GRAPH", "336 edges synced", "purple"),
        ("SEMA", "Decision: 94%", "cyan"),
    ]

    tick = 0
    try:
        with Live(console=console, refresh_per_second=3, screen=True) as live:
            while True:
                tick += 1
                if tick % 4 == 0:
                    m = auto_msgs[tick % len(auto_msgs)]
                    activity.add(m[0], m[1], m[2])

                header = Text.from_markup(
                    f"[bold orange1]  MULTIFLY 2035 | ONE UNIFIED GRAPH | {datetime.now().strftime('%H:%M:%S')} | All 15 Systems Connected[/]")

                gp = Panel(Align.center(Text(graph.render(), no_wrap=True)),
                    title="[bold]Unified Graph - All Systems Connected[/]", border_style="orange1", box=box.DOUBLE)
                lp = Panel(activity.render(), title="[bold]Activity[/]", border_style="orange1")
                sp = Panel(systems.render(), title="[bold]Systems[/]", border_style="orange1")

                # Live brain stats
                try:
                    import sys as _sys
                    _sys.path.insert(0, os.path.dirname(__file__))
                    from multifly_brain_db import get_brain
                    brain = get_brain()
                    bs = brain.get_summary()
                    brain_stats = True
                except:
                    bs = {"total_commands": 0, "total_actions": 0, "patterns_learned": 0, "today_commands": 0}
                    brain_stats = False

                stats = Table(box=box.ROUNDED, border_style="orange1", show_header=False)
                stats.add_column("M", width=14)
                stats.add_column("V", width=8, justify="right")
                for n, v, c in [
                    ("Nodes", "274", "orange1"), ("Edges", "336", "purple"),
                    ("Communities", "18", "green"), ("Systems", "15", "cyan"),
                    ("Commands", str(bs["total_commands"]), "bright_white"),
                    ("Actions", str(bs["total_actions"]), "bright_white"),
                    ("Patterns", str(bs["patterns_learned"]), "yellow"),
                    ("Today", str(bs["today_commands"]), "bright_green"),
                ]:
                    stats.add_row(n, f"[bold {c}]{v}[/]")
                tp = Panel(stats, title="[bold]Live Stats (Brain)[/]", border_style="orange1")

                layout = Layout()
                layout.split_column(Layout(header, size=3), Layout(name="body"))
                layout["body"].split_row(Layout(name="left", ratio=3), Layout(name="right", ratio=2))
                layout["left"].split_column(gp)
                layout["right"].split_column(Layout(lp, ratio=2), Layout(name="bot"))
                layout["bot"].split_row(Layout(sp, ratio=1), Layout(tp, ratio=1))

                live.update(layout)
                time.sleep(0.33)
    except KeyboardInterrupt:
        console.print("\n[orange1]Graph stopped.[/]")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--once":
        graph = UnifiedGraph(74, 22)
        systems = SystemTable()
        activity = ActivityLog()
        console.print(graph.render())
        console.print()
        console.print(Columns([systems.render(), Table(box=box.ROUNDED, border_style="orange1", show_header=False)]))
        console.print()
        console.print(activity.render())
    else:
        run()
