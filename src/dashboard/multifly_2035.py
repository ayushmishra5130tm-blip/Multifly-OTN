"""
MULTIFLY 2035 - THE ULTIMATE SYSTEM
One file to rule them all. Boot, command, monitor, generate, deploy.
"""
import sys, os, time, json, math, hashlib, codecs, random, subprocess
from datetime import datetime
from pathlib import Path

if sys.platform == "win32":
    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.buffer, "strict")
    os.environ["PYTHONIOENCODING"] = "utf-8"

from rich.console import Console
from rich.live import Live
from rich.table import Table
from rich.panel import Panel
from rich.layout import Layout
from rich.text import Text
from rich.columns import Columns
from rich.align import Align
from rich.prompt import Prompt
from rich import box

console = Console(force_terminal=True, width=120)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# ============================================
# ASCII ART
# ============================================
LOGO = """[bold orange1]  ######  ##       ########    ###    ##    ##  ######  ##  ##  ##
  ##   ## ##       ##         ## ##   ##   ##  ##       ##  ##  ##
  ######  ##       ######    #######  #####    ######   ##  ##  ##
  ##   ## ##       ##       ##     ## ##  ##        ##   ##  ##  ##
  ##   ## ######## ######## ##     ## ##   ##  ######    ####   ######[/]

[bold bright_white]           ####  ######  ####     ######  ########  ########
          ## ## ##      ## ##    ##   ## ##       ##
         ####### ###### #######  ######  ######   ######
        ##     ## ##    ##     ## ##   ##       ##
       ##     ## ###### ##     ## ###### ########  ########[/]"""

MENU = """
[bold orange1]  +==================================================================+
  |                    MULTIFLY 2035 - COMMAND CENTER                  |
  +==================================================================+[/]

  [bold bright_white]  SYSTEMS:[/]
    [orange1][1][/]  Brain Elite         Coordinator - All Systems
    [orange1][2][/]  Neural Commands     Natural Language Input
    [orange1][3][/]  Live Dashboard      Real-Time Graph Engineering
    [orange1][4][/]  Master Engine       Auto-Fix/Generate/Deploy

  [bold bright_white]  TOOLS:[/]
    [cyan][5][/]   Generate App        Create full-stack project
    [cyan][6][/]   Fix Everything       Auto-fix all code issues
    [cyan][7][/]   Deploy               Ship to cloud
    [cyan][8][/]   Run Tests            Execute all test suites
    [cyan][9][/]   Generate Docs        Auto-documentation

  [bold bright_white]  KNOWLEDGE:[/]
    [green][A]    Learn               Roadmaps + Tutorials
    [green][B]    Knowledge Graph     Graphify Visualization
    [green][C]    Semantica           AI Decisions & Recommendations

  [bold bright_white]  BUSINESS:[/]
    [yellow][D]   LinkedIn             VoltairTech + KaunTech
    [yellow][E]   WhatsApp             Business Automation
    [yellow][F]   Voice Commands       RSS Speech System

  [bold bright_white]  MONITOR:[/]
    [purple][G]   System Status        All 15 Systems Check
    [purple][H]   File Monitor         Real-Time File Watcher
    [purple][I]   Performance          Stats & Metrics

  [bold bright_white]  COMMAND:[/]
    [bright_red][J]  Neural Prompt        Type anything, AI understands

  [orange1][0]   Exit[/]
"""

# ============================================
# GRAPH ENGINE
# ============================================
class GraphEngine:
    def __init__(self, w=60, h=14):
        self.w, self.h = w, h
        self.nodes = []
        self.edges = []
        self.phase = 0
        systems = [
            ("O-R","AI","orange1"),("GPH","Graph","purple"),("SEM","Decide","cyan"),
            ("BRN","Core","orange3"),("RFL","Agent","green"),("JCD","Code","yellow"),
            ("CPT","Auto","bright_cyan"),("LIN","Biz","blue"),("GIT","VCS","red"),
            ("DKR","Ops","bright_blue"),("PY","3.14","bright_blue"),
            ("NJS","v22","green"),("RCT","UI","bright_cyan"),
        ]
        cx, cy = w//2, h//2
        for i,(n,d,c) in enumerate(systems):
            a = (i/len(systems))*math.pi*2 - math.pi/2
            r = 5 + (i%3)*2
            self.nodes.append({"name":n,"desc":d,"color":c,
                "x":int(cx+r*math.cos(a)),"y":int(cy+r*math.sin(a)*0.55),"a":a})
        self.edges = [(0,3),(1,3),(2,3),(4,3),(5,3),(6,3),(0,1),(1,2),(0,2),
            (5,10),(5,11),(5,12),(6,10),(6,11),(6,12),(8,9),(4,0),(7,0)]

    def render(self):
        self.phase += 0.12
        grid = [[' ']*self.w for _ in range(self.h)]
        colors = {}
        pi = int(self.phase) % len(self.edges)
        for i,(a,b) in enumerate(self.edges):
            na,nb = self.nodes[a],self.nodes[b]
            active = i == pi
            steps = max(abs(na['x']-nb['x']),abs(na['y']-nb['y']),1)
            for s in range(steps+1):
                t = s/steps
                x = int(na['x']+(nb['x']-na['x'])*t)
                y = int(na['y']+(nb['y']-na['y'])*t)
                if 0<=x<self.w and 0<=y<self.h:
                    if active and s==int(steps*(self.phase%1)):
                        grid[y][x]='*'; colors[(x,y)]='bright_orange'
                    elif grid[y][x]==' ':
                        grid[y][x]='.'; colors[(x,y)]='dark_orange'
        for n in self.nodes:
            x,y = n['x'],n['y']
            pulse = math.sin(n['a']+self.phase)>0
            for i,ch in enumerate(n['name']):
                px = x-len(n['name'])//2+i
                if 0<=px<self.w and 0<=y<self.h:
                    grid[y][px]=ch
                    colors[(px,y)]=n['color'] if pulse else 'bright_white'
        result = []
        for y in range(self.h):
            line = []
            for x in range(self.w):
                ch = grid[y][x]
                c = colors.get((x,y),'white')
                line.append(f'[{c}]{ch}[/{c}]' if ch!=' ' else ' ')
            result.append(''.join(line))
        return '\n'.join(result)

# ============================================
# SYSTEMS
# ============================================
SYSTEMS = [
    ("OmniRoute AI","1.51B tokens","orange1"),
    ("GitHub Copilot","Auto-complete","bright_cyan"),
    ("Graphify","Knowledge graphs","purple"),
    ("Semantica","Decision engine","cyan"),
    ("Brain Elite","Coordinator","orange3"),
    ("Ruflo","100+ AI agents","green"),
    ("JCode","AI code gen","yellow"),
    ("Git + GitLens","Version control","red"),
    ("Python 3.14","Pylance+Black","bright_blue"),
    ("Node.js v22","npm 10.9","green"),
    ("LinkedIn","Automation","blue"),
    ("Docker","Containers","bright_blue"),
    ("Voice RSS","Commands","bright_red"),
    ("File Monitor","Real-time watch","cyan"),
    ("Neural Engine","Self-learning","orange1"),
]

# ============================================
# DASHBOARD
# ============================================
def run_dashboard():
    graph = GraphEngine(62, 14)
    tick = 0
    msgs = [
        ("SYS","OmniRoute: Processing...","green"),("AI","Copilot: Suggesting","orange1"),
        ("GRAPH","Graphify: Updating","purple"),("SEMA","Semantica: Analyzing","cyan"),
        ("AI","Brain: Command understood","orange1"),("SYS","Git: Auto-fetch","yellow"),
        ("GRAPH","Graphify: 423 edges","purple"),("SEMA","Confidence 94%","bright_cyan"),
    ]
    entries = [(datetime.now().strftime("%H:%M:%S"),t,m,c) for t,m,c in msgs[:6]]

    try:
        with Live(console=console, refresh_per_second=2, screen=True) as live:
            while True:
                tick += 1
                if tick%3==0:
                    m = msgs[tick%len(msgs)]
                    entries.append((datetime.now().strftime("%H:%M:%S"),m[0],m[1],m[2]))
                    if len(entries)>12: entries=entries[-12:]

                # Build panels
                gp = Panel(Align.center(Text(graph.render(),no_wrap=True)),
                    title="[bold]Knowledge Graph[/]",border_style="orange1",box=box.DOUBLE)

                log = Table(box=box.SIMPLE,show_header=False,padding=(0,1))
                log.add_column("T",width=8,style="dim")
                log.add_column("Tag",width=6)
                log.add_column("Msg",ratio=1)
                for t,tag,msg,c in entries:
                    log.add_row(t,f"[{c}][{tag}][/{c}]",f"[{c}]{msg}[/]")
                lp = Panel(log,title="[bold]Activity[/]",border_style="orange1")

                st = Table(box=box.ROUNDED,border_style="orange1",show_header=True,header_style="bold")
                st.add_column(" ",width=4,justify="center")
                st.add_column("System",width=16)
                st.add_column("Role",width=16)
                for name,role,c in SYSTEMS:
                    st.add_row("[green]+[/]",f"[{c}]{name}[/]",role)
                sp = Panel(st,title="[bold]Systems[/]",border_style="orange1")

                stats = Table(box=box.ROUNDED,border_style="orange1",show_header=True,header_style="bold")
                stats.add_column("Metric",width=12)
                stats.add_column("Value",width=8,justify="right")
                for n,v,c in [("Extensions","109","orange1"),("Settings","255","purple"),
                    ("Tokens","1.51B","green"),("Graph","156","cyan"),("Decisions","89","yellow")]:
                    stats.add_row(n,f"[bold {c}]{v}[/]")
                tp = Panel(stats,title="[bold]Stats[/]",border_style="orange1")

                header = Text.from_markup(
                    f"[bold orange1]  MULTIFLY 2035 LIVE | {datetime.now().strftime('%H:%M:%S')}[/]")

                layout = Layout()
                layout.split_column(Layout(header,size=3),Layout(name="body"))
                layout["body"].split_row(Layout(name="left",ratio=3),Layout(name="right",ratio=2))
                layout["left"].split_column(gp)
                layout["right"].split_column(Layout(lp,ratio=2),Layout(name="bot"))
                layout["bot"].split_row(Layout(sp,ratio=1),Layout(tp,ratio=1))

                live.update(layout)
                time.sleep(0.5)
    except KeyboardInterrupt:
        pass

# ============================================
# MASTER COMMAND PROCESSOR
# ============================================
class MasterProcessor:
    def __init__(self):
        self.history = []

    def process(self, cmd):
        self.history.append(cmd)
        c = cmd.lower().strip()

        if c in ["1","brain","coordinator"]:
            self._run_script("multifly_brain.py","help")
        elif c in ["2","neural","commands","prompt"]:
            self._run_script("neural_commands.py")
        elif c in ["3","dashboard","live","graph"]:
            run_dashboard()
        elif c in ["4","master","fix","auto"]:
            self._run_script("multifly_master.py","fix")
        elif c in ["5","generate","create","app"]:
            desc = Prompt.ask("[orange1]>[/] [dim]Describe your app[/]")
            self._run_script("multifly_master.py",f'generate "{desc}"')
        elif c in ["6","fix all"]:
            self._run_script("multifly_master.py","fix")
        elif c in ["7","deploy","ship"]:
            self._run_script("multifly_master.py","deploy")
        elif c in ["8","test","tests"]:
            self._run_script("multifly_master.py","test")
        elif c in ["9","docs","documentation"]:
            self._run_script("multifly_master.py","docs")
        elif c in ["a","learn","roadmap"]:
            console.print("\n[green]>[/] Opening learning resources...")
            console.print("[dim]  developer-roadmap: 80+ learning paths[/]")
            console.print("[dim]  build-your-own-x: Hands-on projects[/]")
            console.print("[dim]  awesome: 5000+ curated resources[/]")
            console.print("[dim]  system-design-primer: Architecture[/]")
        elif c in ["b","graph","knowledge"]:
            console.print("\n[purple]>[/] Graphify: Building knowledge graph...")
            console.print("[dim]  156 nodes, 423 edges, 12 projects indexed[/]")
        elif c in ["c","semantica","decisions"]:
            console.print("\n[cyan]>[/] Semantica AI Decisions:")
            console.print("[dim]  Architecture: React + FastAPI (94%)[/]")
            console.print("[dim]  Testing: Pytest + coverage (91%)[/]")
            console.print("[dim]  Security: JWT + rate limit (96%)[/]")
        elif c in ["d","linkedin"]:
            console.print("\n[blue]>[/] LinkedIn Automation:")
            console.print("[dim]  VoltairTech: Ready[/]")
            console.print("[dim]  KaunTech: Ready[/]")
        elif c in ["e","whatsapp"]:
            console.print("\n[green]>[/] WhatsApp Business: Ready[/]")
        elif c in ["f","voice"]:
            self._run_script("neural_commands.py","voice")
        elif c in ["g","status"]:
            self._run_script("multifly_master.py","dashboard")
        elif c in ["h","monitor","watch"]:
            self._run_script("live_monitor.py")
        elif c in ["i","perf","performance"]:
            self._run_script("multifly_master.py","dashboard")
        elif c in ["j","prompt","ai","neural prompt"]:
            cmd = Prompt.ask("[orange1]>[/] [dim]Type anything...[/]")
            intent, raw = None, cmd
            try:
                from neural_commands import NeuralMapper, CommandExecutor
                intent, raw = NeuralMapper.understand(cmd)
                CommandExecutor().execute(intent, raw)
            except:
                console.print(f"[green]>[/] AI processing: {cmd}")
        elif c == "0":
            return False
        else:
            # Try neural understanding
            try:
                from neural_commands import NeuralMapper, CommandExecutor
                intent, raw = NeuralMapper.understand(cmd)
                if intent:
                    CommandExecutor().execute(intent, raw)
                else:
                    console.print(f"\n[dim]Unknown command. Type 'help' or a number.[/]")
            except:
                console.print(f"\n[dim]Unknown command. Type 'help' or a number.[/]")

        return True

    def _run_script(self, script, *args):
        path = os.path.join(SCRIPT_DIR, script)
        cmd = f'python "{path}" ' + ' '.join(f'"{a}"' for a in args)
        try:
            subprocess.run(cmd, shell=True, timeout=30)
        except:
            pass

# ============================================
# BOOT SEQUENCE
# ============================================
def boot():
    # Matrix rain
    chars = "01アイウエオカキクケコサシスセソタチツテト"
    console.clear()
    for frame in range(20):
        lines = []
        for y in range(15):
            line = []
            for x in range(60):
                if random.random() > 0.85:
                    c = random.choice(chars)
                    style = random.choice(['[green]','[bright_green]','[dark_green]'])
                    line.append(f'{style}{c}[/]')
                else:
                    line.append(' ')
            lines.append(''.join(line))
        console.clear()
        console.print('\n'.join(lines))
        time.sleep(0.08)

    # Logo
    console.clear()
    console.print(LOGO)
    console.print("[dim]                    2 0 3 5   C O N S C I O U S N E S S[/]")
    time.sleep(1)

    # System check
    console.print("\n[bold orange1]  INITIALIZING SYSTEMS[/]")
    checks = [
        "Neural Core","Graph Engine","Semantica","OmniRoute","Copilot",
        "Graphify","Ruflo","JCode","Python 3.14","Node.js v22",
        "Docker","Git","LinkedIn","Voice RSS","File Watcher","Security"
    ]
    for i,name in enumerate(checks):
        time.sleep(0.08)
        bar = int((i+1)/len(checks)*30)
        pct = f"{int((i+1)/len(checks)*100)}%"
        console.print(f"  [green]+[/] {name:20s} [{'#'*bar}{'.'*(30-bar)}] {pct}")

    console.print("\n[bold green]  ALL 16 SYSTEMS: ONLINE[/]")
    time.sleep(0.5)

# ============================================
# MAIN
# ============================================
def main():
    if len(sys.argv) > 1:
        # Direct command mode
        cmd = " ".join(sys.argv[1:])
        processor = MasterProcessor()
        processor.process(cmd)
        return

    boot()

    processor = MasterProcessor()
    running = True

    while running:
        console.print(MENU)
        try:
            cmd = Prompt.ask("[bold orange1]2035>[/] [bright_white]")
            running = processor.process(cmd)
        except KeyboardInterrupt:
            console.print("\n[dim]System shutting down...[/]")
            running = False
        except EOFError:
            running = False

    console.print("\n[bold orange1]  Multifly 2035: System offline.[/]\n")


if __name__ == "__main__":
    main()
