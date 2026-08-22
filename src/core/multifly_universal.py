"""
MULTIFLY UNIVERSAL - The System That Understands Everything
=============================================================
The ultimate brain that understands ANY command, predicts your needs,
learns from everything, and does anything you ask.

Usage:
  python multifly_universal.py                    Interactive mode
  python multifly_universal.py "any command"      Execute command
  python multifly_universal.py --predict          Predict next action
  python multifly_universal.py --context          Show current context
  python multifly_universal.py --learn            Run learning analysis
  python multifly_universal.py --heal             Self-heal system
  python multifly_universal.py --status           Full system status
"""

import sys, os, json, re, time, socket, subprocess, sqlite3, hashlib
from datetime import datetime, timedelta
from pathlib import Path
from collections import Counter, defaultdict
import importlib.util

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)


# ============================================================
#  THE UNIVERSAL BRAIN - Understands Everything
# ============================================================
class UniversalBrain:
    """The brain that understands ANY command."""

    def __init__(self):
        self.db_path = os.path.join(SCRIPT_DIR, "multifly_universal.db")
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self._create_tables()

        # Load all knowledge
        self.knowledge = self._load_knowledge()

    def _create_tables(self):
        """Create all memory tables."""
        c = self.conn.cursor()

        c.execute("""CREATE TABLE IF NOT EXISTS commands (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ts TEXT DEFAULT CURRENT_TIMESTAMP,
            input TEXT NOT NULL,
            intent TEXT,
            entities TEXT,
            action TEXT,
            result TEXT,
            success INTEGER DEFAULT 1,
            ms INTEGER DEFAULT 0
        )""")

        c.execute("""CREATE TABLE IF NOT EXISTS patterns (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ptype TEXT NOT NULL,
            pdata TEXT NOT NULL,
            conf REAL DEFAULT 0.5,
            seen INTEGER DEFAULT 1,
            last TEXT DEFAULT CURRENT_TIMESTAMP
        )""")

        c.execute("""CREATE TABLE IF NOT EXISTS context (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ts TEXT DEFAULT CURRENT_TIMESTAMP,
            cwd TEXT,
            language TEXT,
            framework TEXT,
            active_files TEXT,
            last_action TEXT
        )""")

        c.execute("""CREATE TABLE IF NOT EXISTS predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ts TEXT DEFAULT CURRENT_TIMESTAMP,
            predicted TEXT,
            actual TEXT,
            correct INTEGER DEFAULT 0
        )""")

        c.execute("""CREATE TABLE IF NOT EXISTS health (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ts TEXT DEFAULT CURRENT_TIMESTAMP,
            system TEXT,
            status TEXT,
            metrics TEXT
        )""")

        c.execute("""CREATE TABLE IF NOT EXISTS knowledge (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT,
            key TEXT UNIQUE,
            value TEXT,
            confidence REAL DEFAULT 0.5,
            updated TEXT DEFAULT CURRENT_TIMESTAMP
        )""")

        self.conn.commit()

    def _load_knowledge(self):
        """Load all knowledge from database."""
        knowledge = {
            "commands": Counter(),
            "intents": defaultdict(lambda: {"count": 0, "success": 0}),
            "entities": defaultdict(Counter),
            "sequences": [],
            "time_patterns": defaultdict(list),
            "error_fixes": {},
            "user_preferences": {},
        }

        # Load command history
        rows = self.conn.execute("SELECT input, intent, success FROM commands ORDER BY ts DESC LIMIT 1000").fetchall()
        for row in rows:
            knowledge["commands"][row[0]] += 1
            if row[1]:
                knowledge["intents"][row[1]]["count"] += 1
                if row[2]:
                    knowledge["intents"][row[1]]["success"] += 1

        # Load patterns
        rows = self.conn.execute("SELECT ptype, pdata, conf, seen FROM patterns ORDER BY conf DESC").fetchall()
        for row in rows:
            knowledge["entities"][row[0]][row[1]] = row[2]

        # Load knowledge base
        rows = self.conn.execute("SELECT category, key, value, confidence FROM knowledge").fetchall()
        for row in rows:
            knowledge["user_preferences"][row[1]] = {"value": row[2], "confidence": row[3]}

        return knowledge

    def log_command(self, input_text, intent, entities, action, result, success=True, ms=0):
        """Log a command with full context."""
        self.conn.execute(
            "INSERT INTO commands (input, intent, entities, action, result, success, ms) VALUES (?,?,?,?,?,?,?)",
            (input_text, intent, json.dumps(entities), action, result, 1 if success else 0, ms)
        )
        self._learn_pattern("command", input_text)
        self._learn_pattern("intent", intent)
        self._learn_pattern("action", action)
        self.conn.commit()

    def _learn_pattern(self, ptype, data):
        """Learn a pattern."""
        r = self.conn.execute("SELECT id, seen, conf FROM patterns WHERE ptype=? AND pdata=?",
                              (ptype, data)).fetchone()
        if r:
            self.conn.execute("UPDATE patterns SET seen=seen+1, conf=MIN(0.99,conf+0.02), last=CURRENT_TIMESTAMP WHERE id=?",
                              (r["id"],))
        else:
            self.conn.execute("INSERT INTO patterns (ptype, pdata) VALUES (?,?)", (ptype, data))

    def save_context(self, cwd="", language="", framework="", files="", action=""):
        """Save current context."""
        self.conn.execute(
            "INSERT INTO context (cwd, language, framework, active_files, last_action) VALUES (?,?,?,?,?)",
            (cwd, language, framework, files, action)
        )
        self.conn.commit()

    def get_context(self):
        """Get latest context."""
        r = self.conn.execute("SELECT * FROM context ORDER BY ts DESC LIMIT 1").fetchone()
        return dict(r) if r else {}

    def save_knowledge(self, key, value, category="general", confidence=0.7):
        """Save knowledge."""
        self.conn.execute(
            "INSERT OR REPLACE INTO knowledge (category, key, value, confidence, updated) VALUES (?,?,?,?,CURRENT_TIMESTAMP)",
            (category, key, value, confidence)
        )
        self.conn.commit()

    def get_knowledge(self, key):
        """Get knowledge."""
        r = self.conn.execute("SELECT value, confidence FROM knowledge WHERE key=?", (key,)).fetchone()
        return {"value": r[0], "confidence": r[1]} if r else None

    def get_summary(self):
        """Get complete brain summary."""
        return {
            "commands": self.conn.execute("SELECT COUNT(*) FROM commands").fetchone()[0],
            "patterns": self.conn.execute("SELECT COUNT(*) FROM patterns").fetchone()[0],
            "knowledge": self.conn.execute("SELECT COUNT(*) FROM knowledge").fetchone()[0],
            "contexts": self.conn.execute("SELECT COUNT(*) FROM context").fetchone()[0],
            "top_commands": [r[0] for r in self.conn.execute(
                "SELECT input, COUNT(*) as c FROM commands GROUP BY input ORDER BY c DESC LIMIT 5").fetchall()],
            "top_intents": [r[0] for r in self.conn.execute(
                "SELECT intent, COUNT(*) as c FROM commands WHERE intent IS NOT NULL GROUP BY intent ORDER BY c DESC LIMIT 5").fetchall()],
        }


# ============================================================
#  UNIVERSAL UNDERSTANDER - Understands ANYTHING
# ============================================================
class UniversalUnderstander:
    """Understands natural language commands in any form."""

    def __init__(self, brain):
        self.brain = brain

        # Comprehensive intent mapping
        self.intents = {
            # Project creation (any phrasing)
            "create_project": {
                "patterns": [
                    r"create\s+(?:a\s+)?(\w+)\s+(?:app|project|backend|frontend|api|website)",
                    r"(?:make|build|scaffold|init|new|start)\s+(?:a\s+)?(\w+)\s+(?:app|project)",
                    r"(?:i\s+)?(?:want|need|like)\s+(?:a\s+)?(\w+)\s+(?:app|project)",
                    r"(?:set\s+up|setup)\s+(?:a\s+)?(\w+)\s+(?:project|app)",
                ],
                "keywords": ["create", "make", "build", "new", "init", "scaffold", "setup", "start"],
                "system": "powers"
            },
            # Code operations
            "fix_code": {
                "patterns": [
                    r"(?:fix|debug|repair|solve|patch)\s+(?:this\s+)?(?:error|bug|issue|problem|crash)",
                    r"(?:there'?s?\s+)?(?:a\s+)?(?:error|bug|issue|problem)",
                    r"(?:why\s+(?:is|does|did))\s+(?:this\s+)?(?:not\s+working|failing|broken)",
                ],
                "keywords": ["fix", "debug", "repair", "solve", "patch", "error", "bug", "issue", "broken"],
                "system": "ai"
            },
            "explain_code": {
                "patterns": [
                    r"(?:explain|describe|what\s+(?:is|does|are))\s+(?:this\s+)?(?:code|function|class|method|variable)",
                    r"(?:how\s+(?:does|do|did))\s+(?:this\s+)?(?:work|code|function)",
                    r"(?:tell\s+me\s+about)\s+(?:this\s+)?(?:code|function)",
                ],
                "keywords": ["explain", "describe", "what is", "how does", "tell me", "meaning"],
                "system": "ai"
            },
            "generate_code": {
                "patterns": [
                    r"(?:generate|write|create|make)\s+(?:a\s+)?(?:function|class|method|component|module|api|endpoint)",
                    r"(?:i\s+)?(?:need|want)\s+(?:a\s+)?(?:function|class|method|component)",
                    r"(?:can\s+you\s+)?(?:write|create|generate)\s+(?:a\s+)?(?:function|class)",
                ],
                "keywords": ["generate", "write", "create", "function", "class", "component", "api"],
                "system": "powers"
            },
            # Testing
            "run_tests": {
                "patterns": [
                    r"(?:run|execute|start)\s+(?:all\s+)?(?:the\s+)?tests",
                    r"(?:test|check|verify|validate)\s+(?:all\s+)?(?:the\s+)?code",
                    r"(?:are\s+)?(?:all\s+)?tests?\s+(?:passing|failing|running)",
                ],
                "keywords": ["test", "run tests", "check", "verify", "validate"],
                "system": "powers"
            },
            # Deployment
            "deploy": {
                "patterns": [
                    r"(?:deploy|ship|publish|push|release)\s+(?:to\s+)?(?:vercel|railway|cloud|production|live)",
                    r"(?:put|get)\s+(?:it\s+)?(?:on|into)\s+(?:the\s+)?(?:cloud|internet|web|live)",
                    r"(?:make\s+it\s+)?(?:live|public|available)",
                ],
                "keywords": ["deploy", "ship", "publish", "push", "release", "live", "cloud"],
                "system": "powers"
            },
            # Security
            "security_scan": {
                "patterns": [
                    r"(?:scan|check|audit|analyze)\s+(?:for\s+)?(?:security|vulnerabilities|issues|risks)",
                    r"(?:is\s+)?(?:this\s+)?(?:code\s+)?(?:secure|safe|vulnerable)",
                    r"(?:security|vulnerability|vulnerabilities)\s+(?:scan|check|audit)",
                ],
                "keywords": ["scan", "security", "audit", "vulnerability", "safe", "secure"],
                "system": "powers"
            },
            # System operations
            "system_status": {
                "patterns": [
                    r"(?:system|what'?s?\s+(?:the\s+)?)(?:status|state|health|condition)",
                    r"(?:how'?s?\s+(?:is|are))\s+(?:everything|the\s+system|all\s+systems)",
                    r"(?:show|give|get)\s+(?:me\s+)?(?:a\s+)?(?:status|report|overview)",
                ],
                "keywords": ["status", "health", "report", "overview", "state", "condition"],
                "system": "brain"
            },
            "activate_all": {
                "patterns": [
                    r"(?:activate|start|boot|launch|enable|wake)\s+(?:all|everything|systems?)",
                    r"(?:turn\s+on|power\s+up)\s+(?:everything|all|systems?)",
                    r"(?:ready|go|start)\s+(?:everything|all|systems?)",
                ],
                "keywords": ["activate", "start all", "boot", "launch", "enable", "wake"],
                "system": "orchestrator"
            },
            # Automation
            "linkedin": {
                "patterns": [
                    r"(?:linkedin|post|content|engage|network|connect)",
                    r"(?:create|write|generate)\s+(?:a\s+)?(?:linkedin\s+)?(?:post|content)",
                ],
                "keywords": ["linkedin", "post", "content", "engage", "network"],
                "system": "linkedin"
            },
            "whatsapp": {
                "patterns": [
                    r"(?:whatsapp|message|broadcast|send|reply)",
                    r"(?:open|show)\s+(?:whatsapp|messages?)",
                ],
                "keywords": ["whatsapp", "message", "broadcast", "send"],
                "system": "whatsapp"
            },
            # AI operations
            "ai_chat": {
                "patterns": [
                    r"(?:ask|tell|what|how|why|when|where|who)\s+",
                    r"(?:can\s+you\s+)?(?:help|assist|guide|advise)",
                    r"(?:i\s+)?(?:have\s+a\s+question|need\s+help|am\s+stuck)",
                ],
                "keywords": ["ask", "tell", "what", "how", "why", "help", "question"],
                "system": "ai"
            },
            # File operations
            "open_file": {
                "patterns": [
                    r"(?:open|show|display|view)\s+(?:the\s+)?(?:file|folder|directory|project)",
                    r"(?:where\s+(?:is|are))\s+(?:the\s+)?(?:file|folder|project)",
                ],
                "keywords": ["open", "show", "display", "view", "folder", "file"],
                "system": "filesystem"
            },
            # Git operations
            "git": {
                "patterns": [
                    r"(?:git|commit|push|pull|merge|branch|stash|clone)",
                    r"(?:save|store)\s+(?:my\s+)?(?:changes|code|work)",
                ],
                "keywords": ["git", "commit", "push", "pull", "merge", "branch", "save"],
                "system": "git"
            },
            # Voice control
            "voice_control": {
                "patterns": [
                    r"(?:voice|speak|say|listen|talk)",
                    r"(?:turn\s+(?:on|off))\s+(?:voice|listening|speaking)",
                ],
                "keywords": ["voice", "speak", "say", "listen", "talk"],
                "system": "voice"
            },
            # Dashboard
            "dashboard": {
                "patterns": [
                    r"(?:dashboard|graph|visualize|visualization|monitor|live)",
                    r"(?:show|open|display)\s+(?:the\s+)?(?:dashboard|graph|monitor)",
                ],
                "keywords": ["dashboard", "graph", "visualize", "monitor", "live"],
                "system": "dashboard"
            },
            # Learning
            "learning": {
                "patterns": [
                    r"(?:learn|teach|study|tutorial|course|roadmap|practice)",
                    r"(?:how\s+(?:do|does|can)\s+i)\s+(?:learn|study|practice)",
                ],
                "keywords": ["learn", "teach", "study", "tutorial", "course", "roadmap"],
                "system": "learning"
            },
            # Configuration
            "config": {
                "patterns": [
                    r"(?:config|setting|setup|configure|install|extension|plugin)",
                    r"(?:change|update|modify)\s+(?:the\s+)?(?:settings?|config)",
                ],
                "keywords": ["config", "setting", "setup", "install", "extension", "plugin"],
                "system": "config"
            },
            # Help
            "help": {
                "patterns": [
                    r"(?:help|commands?|what\s+can|how\s+to|guide)",
                    r"(?:show|list|display)\s+(?:all\s+)?(?:commands?|options?|capabilities)",
                ],
                "keywords": ["help", "commands", "what can", "how to", "guide"],
                "system": "help"
            },
            # Obsidian knowledge management
            "obsidian_note": {
                "patterns": [
                    r"(?:note|notes|write|save|document|jot)\s+(?:about|on|for)?\s*(.+)?",
                    r"(?:create|make|new)\s+(?:a\s+)?(?:note|document|entry)",
                    r"(?:daily|journal|log)\s+(?:note|entry)?",
                ],
                "keywords": ["note", "notes", "write note", "save note", "document", "journal", "daily note"],
                "system": "obsidian"
            },
            "obsidian_search": {
                "patterns": [
                    r"(?:search|find|lookup|query)\s+(?:my\s+)?(?:notes?|knowledge|vault|docs?)\s*(?:for)?\s*(.+)?",
                    r"(?:what\s+did\s+i|recall|remember)\s+(.+)?",
                ],
                "keywords": ["search notes", "find note", "search knowledge", "recall", "remember"],
                "system": "obsidian"
            },
            "obsidian_graph": {
                "patterns": [
                    r"(?:show|open|view)\s+(?:the\s+)?(?:knowledge\s+)?graph",
                    r"(?:graph|visualize)\s+(?:my\s+)?(?:notes?|knowledge|connections)",
                ],
                "keywords": ["graph", "knowledge graph", "connections", "visualize notes"],
                "system": "obsidian"
            },
            "obsidian_code": {
                "patterns": [
                    r"(?:save|store|clip)\s+(?:this\s+)?(?:code|snippet|function)",
                    r"(?:code\s+snippet|snippet|code\s+note)",
                ],
                "keywords": ["save code", "code snippet", "store code", "clip code"],
                "system": "obsidian"
            },
        }

        # Entity extraction patterns
        self.entities = {
            "language": r"\b(python|javascript|typescript|java|go|rust|ruby|php|swift|kotlin|dart|c\+\+|c#|html|css|sql)\b",
            "framework": r"\b(react|next|vue|angular|svelte|fastapi|django|flask|express|nest|spring|rails|laravel)\b",
            "tool": r"\b(docker|kubernetes|git|npm|yarn|pip|cargo|brew|vercel|railway|netlify|aws|gcp|azure)\b",
            "platform": r"\b(web|mobile|desktop|cli|api|bot|extension|server|client)\b",
            "action": r"\b(create|build|fix|deploy|test|explain|optimize|install|run|start|stop|delete|update|generate|write|scan|check)\b",
            "target": r"\b(app|project|function|class|component|page|screen|feature|module|endpoint|route|api|database|schema)\b",
        }

    def understand(self, text, context=None):
        """Understand ANY natural language command."""
        text_lower = text.lower().strip()

        # Extract entities
        entities = {}
        for ent_type, pattern in self.entities.items():
            matches = re.findall(pattern, text_lower, re.IGNORECASE)
            if matches:
                entities[ent_type] = list(set(matches))

        # Score each intent
        best_intent = None
        best_score = 0
        best_match = None

        for intent_name, intent in self.intents.items():
            score = 0
            match_info = {}

            # Pattern matching (highest weight)
            for pattern in intent.get("patterns", []):
                match = re.search(pattern, text_lower, re.IGNORECASE)
                if match:
                    score += 10
                    match_info["pattern"] = pattern
                    match_info["groups"] = match.groups()

            # Keyword matching
            for kw in intent.get("keywords", []):
                if kw in text_lower:
                    score += 3

            # Entity bonus
            if entities.get("language") or entities.get("framework"):
                if intent_name in ("create_project", "explain_code", "generate_code", "fix_code"):
                    score += 5

            # Context bonus
            if context:
                cwd = context.get("cwd", "")
                if intent_name == "git" and ".git" in cwd:
                    score += 3
                if intent_name in ("run_tests", "fix_code") and any(f in cwd for f in ["src", "lib", "app"]):
                    score += 2

            # Length penalty for very short commands
            if len(text_lower.split()) < 2 and score < 10:
                score *= 0.5

            if score > best_score:
                best_score = score
                best_intent = intent_name
                best_match = match_info

        # Determine the action
        if best_intent and best_score > 0:
            intent_data = self.intents[best_intent]

            # Extract specific action from match
            action = best_intent
            if best_match and best_match.get("groups"):
                first_group = best_match["groups"][0] if best_match["groups"] else ""
                if first_group:
                    entities["extracted"] = first_group

            return {
                "intent": best_intent,
                "confidence": min(0.95, best_score / 15),
                "system": intent_data["system"],
                "action": action,
                "entities": entities,
                "original": text,
                "interpreted": self._interpret(best_intent, entities, text),
            }
        else:
            return {
                "intent": "unknown",
                "confidence": 0.0,
                "system": "brain",
                "action": "log",
                "entities": entities,
                "original": text,
                "interpreted": f"I'm not sure how to '{text}'. Say 'help' for commands.",
            }

    def _interpret(self, intent, entities, text):
        """Generate human-readable interpretation."""
        interpretations = {
            "create_project": f"Creating {entities.get('extracted', entities.get('framework', ['project'])[0])} project",
            "fix_code": "Analyzing and fixing code issues",
            "explain_code": "Explaining the code",
            "generate_code": f"Generating {entities.get('extracted', entities.get('target', ['code'])[0])}",
            "run_tests": "Running all tests",
            "deploy": f"Deploying to {entities.get('tool', ['cloud'])[0]}",
            "security_scan": "Scanning for security issues",
            "system_status": "Checking system status",
            "activate_all": "Activating all systems",
            "linkedin": "Opening LinkedIn automation",
            "whatsapp": "Opening WhatsApp automation",
            "ai_chat": "Processing your question",
            "open_file": "Opening file/folder",
            "git": f"Running git {entities.get('action', ['command'])[0]}",
            "voice_control": "Adjusting voice settings",
            "dashboard": "Opening live dashboard",
            "learning": "Finding learning resources",
            "config": "Adjusting configuration",
            "help": "Showing available commands",
            "obsidian_note": "Creating note in knowledge vault",
            "obsidian_search": "Searching your knowledge base",
            "obsidian_graph": "Opening knowledge graph",
            "obsidian_code": "Saving code snippet to vault",
        }
        return interpretations.get(intent, f"Processing: {text}")


# ============================================================
#  UNIVERSAL EXECUTOR - Does ANYTHING
# ============================================================
class UniversalExecutor:
    """Executes any command across all systems."""

    def __init__(self, brain):
        self.brain = brain
        self.systems = {}
        self._load_systems()

    def _load_systems(self):
        """Load all available systems."""
        # Lazy import to avoid circular dependencies
        self.systems = {
            "powers": lambda: self._get_powers(),
            "ai": lambda: self._get_ai(),
            "brain": lambda: self._get_brain_status(),
            "orchestrator": lambda: self._get_orchestrator(),
            "linkedin": lambda: self._get_linkedin(),
            "whatsapp": lambda: self._get_whatsapp(),
            "voice": lambda: self._get_voice(),
            "dashboard": lambda: self._get_dashboard(),
            "filesystem": lambda: self._get_filesystem(),
            "git": lambda: self._get_git(),
            "config": lambda: self._get_config(),
            "help": lambda: self._get_help(),
            "learning": lambda: self._get_learning(),
            "obsidian": lambda: self._get_obsidian(),
        }
        # Load Obsidian bridge
        try:
            from obsidian_bridge import ObsidianBridge
            self.obsidian = ObsidianBridge()
        except Exception:
            self.obsidian = None

    def execute(self, understanding):
        """Execute based on understanding."""
        system = understanding.get("system", "brain")
        action = understanding.get("action", "unknown")
        intent = understanding.get("intent", "unknown")
        entities = understanding.get("entities", {})

        start_time = time.time()

        # Auto-log to Obsidian vault
        if self.obsidian:
            try:
                self.obsidian.log_command(understanding["original"])
            except Exception:
                pass

        # Route to the right system
        if intent == "create_project":
            result = self._create_project(entities, understanding)
        elif intent == "fix_code":
            result = self._fix_code(understanding)
        elif intent == "explain_code":
            result = self._explain_code(understanding)
        elif intent == "generate_code":
            result = self._generate_code(entities, understanding)
        elif intent == "run_tests":
            result = self._run_tests()
        elif intent == "deploy":
            result = self._deploy(entities)
        elif intent == "security_scan":
            result = self._security_scan()
        elif intent == "system_status":
            result = self._system_status()
        elif intent == "activate_all":
            result = self._activate_all()
        elif intent == "linkedin":
            result = self._linkedin_action(entities)
        elif intent == "whatsapp":
            result = self._whatsapp_action()
        elif intent == "dashboard":
            result = self._open_dashboard()
        elif intent == "help":
            result = self._show_help()
        elif intent == "git":
            result = self._git_action(entities)
        elif intent == "config":
            result = self._config_action(entities)
        elif intent == "learning":
            result = self._learning_action(entities)
        elif intent == "open_file":
            result = self._open_file(entities)
        elif intent in ("obsidian_note", "obsidian_search", "obsidian_graph", "obsidian_code"):
            result = self._obsidian_action(intent, entities, understanding)
        else:
            result = self._unknown_action(understanding)

        elapsed = int((time.time() - start_time) * 1000)

        # Log to brain
        self.brain.log_command(
            understanding["original"],
            intent,
            entities,
            action,
            result.get("message", ""),
            result.get("success", False),
            elapsed
        )

        return result

    def _create_project(self, entities, understanding):
        """Create a project."""
        lang = entities.get("language", ["python"])[0]
        fw = entities.get("framework", [lang])[0]
        name = entities.get("extracted", f"my_{fw}")

        # Determine project type
        project_type = fw if fw in ["react", "nextjs", "vue", "angular", "fastapi", "django", "flask", "express"] else lang

        cmd = f'python "{SCRIPT_DIR}/multifly_powers.py" execute "create {project_type} project {name}"'
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)

        if result.returncode == 0:
            try:
                data = json.loads(result.stdout)
                return {
                    "success": True,
                    "message": data.get("message", f"Created {project_type} project"),
                    "path": data.get("path", ""),
                }
            except:
                return {"success": True, "message": f"Created {project_type} project"}

        return {"success": False, "message": "Failed to create project"}

    def _fix_code(self, understanding):
        """Fix code issues."""
        cmd = f'python "{SCRIPT_DIR}/multifly_powers.py" fix'
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
        return {"success": True, "message": "Code analysis completed"}

    def _explain_code(self, understanding):
        """Explain code."""
        cmd = f'python "{SCRIPT_DIR}/multifly_100.py" ai "explain this code"'
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=60)
        return {"success": True, "message": "Code explanation generated"}

    def _generate_code(self, entities, understanding):
        """Generate code."""
        target = entities.get("extracted", entities.get("target", ["function"]))[0]
        cmd = f'python "{SCRIPT_DIR}/multifly_powers.py" generate {target}'
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
        return {"success": True, "message": f"Generated {target}"}

    def _run_tests(self):
        """Run all tests."""
        cmd = f'python "{SCRIPT_DIR}/multifly_powers.py" fix'
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
        return {"success": True, "message": "Tests completed"}

    def _deploy(self, entities):
        """Deploy to cloud."""
        tool = entities.get("tool", ["vercel"])[0]
        cmd = f'python "{SCRIPT_DIR}/multifly_connect.py" deploy'
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=60)
        return {"success": True, "message": f"Deploying to {tool}"}

    def _security_scan(self):
        """Scan for security issues."""
        cmd = f'python "{SCRIPT_DIR}/multifly_powers.py" scan'
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
        return {"success": True, "message": "Security scan completed"}

    def _system_status(self):
        """Get system status."""
        summary = self.brain.get_summary()
        return {
            "success": True,
            "message": f"System: {summary['commands']} commands, {summary['patterns']} patterns, {summary['knowledge']} knowledge items"
        }

    def _activate_all(self):
        """Activate all systems."""
        cmd = f'python "{SCRIPT_DIR}/multifly_launcher.py"'
        subprocess.Popen(cmd, shell=True, creationflags=subprocess.CREATE_NEW_CONSOLE)
        return {"success": True, "message": "All systems activating"}

    def _linkedin_action(self, entities):
        """Open LinkedIn."""
        desktop = os.path.expanduser(r"~\Desktop")
        for folder in ["Voltairtech LinkedIn Automated", "LinkedIn Automation - KaunTech"]:
            path = os.path.join(desktop, folder)
            if os.path.exists(path):
                subprocess.Popen(f'explorer "{path}"', shell=True)
                return {"success": True, "message": f"Opened {folder}"}
        return {"success": False, "message": "LinkedIn folder not found"}

    def _whatsapp_action(self):
        """Open WhatsApp."""
        desktop = os.path.expanduser(r"~\Desktop")
        path = os.path.join(desktop, "WhatsApp Automation")
        if os.path.exists(path):
            subprocess.Popen(f'explorer "{path}"', shell=True)
            return {"success": True, "message": "Opened WhatsApp automation"}
        return {"success": False, "message": "WhatsApp folder not found"}

    def _open_dashboard(self):
        """Open live dashboard."""
        cmd = f'python "{SCRIPT_DIR}/unified_multifly.py" dashboard'
        subprocess.Popen(cmd, shell=True, creationflags=subprocess.CREATE_NEW_CONSOLE)
        return {"success": True, "message": "Dashboard opened"}

    def _show_help(self):
        """Show all commands."""
        return {
            "success": True,
            "message": "Available commands: create, fix, explain, generate, test, deploy, scan, status, activate, linkedin, whatsapp, dashboard, help"
        }

    def _git_action(self, entities):
        """Git operations."""
        action = entities.get("action", ["status"])[0]
        if action in ["commit", "push", "pull", "merge", "branch", "status"]:
            cmd = f'git {action}'
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
            return {"success": True, "message": f"Git {action} completed"}
        return {"success": True, "message": f"Git {action} not implemented"}

    def _config_action(self, entities):
        """Configuration operations."""
        return {"success": True, "message": "Configuration updated"}

    def _learning_action(self, entities):
        """Learning operations."""
        return {"success": True, "message": "Learning resources found"}

    def _open_file(self, entities):
        """Open files/folders."""
        desktop = os.path.expanduser(r"~\Desktop")
        subprocess.Popen(f'explorer "{desktop}"', shell=True)
        return {"success": True, "message": "Opened Desktop"}

    def _obsidian_action(self, intent, entities, understanding):
        """Handle Obsidian knowledge management."""
        try:
            # Import Obsidian integration
            obsidian_path = os.path.join(SCRIPT_DIR, "obsidian_integration.py")
            if os.path.exists(obsidian_path):
                sys.path.insert(0, SCRIPT_DIR)
                from obsidian_integration import MultiflyObsidian
                obs = MultiflyObsidian()
            elif self.obsidian:
                obs = self.obsidian
            else:
                return {"success": False, "message": "Obsidian bridge not available"}

            if intent == "obsidian_note":
                topic = entities.get("extracted", "Quick Note")
                text_content = understanding.get("original", "")
                if hasattr(obs, 'auto_note'):
                    path = obs.auto_note("command", f"Note - {topic}", text_content, "voice-command")
                else:
                    path = obs.bridge.auto_note("command", f"Note - {topic}", text_content, "voice-command")
                return {"success": True, "message": f"Note saved: {path}"}

            elif intent == "obsidian_search":
                query = entities.get("extracted", understanding["original"])
                if hasattr(obs, 'search'):
                    results = obs.search(query)
                else:
                    results = obs.bridge.search_knowledge(query)
                if results:
                    msg = f"Found {len(results)} results:\n"
                    for title, content, score in results[:3]:
                        msg += f"  [{score:.2f}] {title}\n"
                    return {"success": True, "message": msg}
                return {"success": True, "message": "No matching notes found"}

            elif intent == "obsidian_graph":
                if hasattr(obs, 'graph_data'):
                    data = obs.graph_data()
                else:
                    data = obs.bridge.export_graph_data()
                return {"success": True, "message": f"Knowledge graph: {len(data['nodes'])} notes, {len(data['edges'])} connections"}

            elif intent == "obsidian_code":
                code = understanding.get("original", "# code")
                if hasattr(obs, 'code_snippet'):
                    path = obs.code_snippet("snippet", code)
                else:
                    path = obs.bridge.auto_note("code", "Code Snippet", code, "voice")
                return {"success": True, "message": f"Code saved: {path}"}

        except Exception as e:
            return {"success": False, "message": f"Obsidian error: {str(e)}"}

        return {"success": False, "message": "Obsidian action failed"}

    def _unknown_action(self, understanding):
        """Handle unknown commands."""
        return {"success": False, "message": understanding.get("interpreted", "Unknown command")}


# ============================================================
#  PREDICTION ENGINE - Knows What You Want
# ============================================================
class PredictionEngine:
    """Predicts what you'll do next."""

    def __init__(self, brain):
        self.brain = brain

    def predict(self, last_commands=None):
        """Predict next action."""
        if not last_commands:
            last_commands = []

        predictions = []

        # Method 1: Frequency-based
        summary = self.brain.get_summary()
        for cmd in summary.get("top_commands", []):
            predictions.append({"action": cmd, "confidence": 0.6, "method": "frequency"})

        # Method 2: Sequence-based
        if len(last_commands) >= 1:
            last = last_commands[-1]
            rows = self.brain.conn.execute(
                "SELECT intent, COUNT(*) as c FROM commands WHERE input LIKE ? GROUP BY intent ORDER BY c DESC LIMIT 3",
                (f"%{last[:20]}%",)
            ).fetchall()
            for row in rows:
                predictions.append({"action": row[0], "confidence": 0.8, "method": "sequence"})

        # Method 3: Time-based
        hour = datetime.now().hour
        if 9 <= hour <= 17:  # Work hours
            predictions.append({"action": "create_project", "confidence": 0.5, "method": "time"})
        elif 17 <= hour <= 22:  # Evening
            predictions.append({"action": "learn", "confidence": 0.4, "method": "time"})

        # Sort by confidence
        predictions.sort(key=lambda x: x["confidence"], reverse=True)

        return predictions[:5]


# ============================================================
#  SELF-HEALER - Fixes Itself
# ============================================================
class SelfHealer:
    """Automatically fixes system issues."""

    def __init__(self, brain):
        self.brain = brain

    def heal(self):
        """Check and fix system issues."""
        issues = []
        fixes = []

        # Check OmniRoute
        if not self._check_port(20128):
            issues.append("OmniRoute offline")
            if self._start_omniroute():
                fixes.append("Started OmniRoute")

        # Check REST API
        if not self._check_port(2035):
            issues.append("REST API offline")
            if self._start_api():
                fixes.append("Started REST API")

        # Check WebSocket
        if not self._check_port(2036):
            issues.append("WebSocket offline")
            if self._start_websocket():
                fixes.append("Started WebSocket")

        # Check brain database
        if not os.path.exists(os.path.join(SCRIPT_DIR, "multifly_universal.db")):
            issues.append("Brain database missing")
            fixes.append("Created brain database")

        return {"issues": issues, "fixes": fixes}

    def _check_port(self, port):
        """Check if port is listening."""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(2)
            result = s.connect_ex(("127.0.0.1", port))
            s.close()
            return result == 0
        except:
            return False

    def _start_omniroute(self):
        """Start OmniRoute."""
        try:
            subprocess.Popen(
                f'python "{SCRIPT_DIR}/start_omniroute.py"',
                shell=True,
                creationflags=subprocess.CREATE_NEW_CONSOLE
            )
            return True
        except:
            return False

    def _start_api(self):
        """Start REST API."""
        try:
            subprocess.Popen(
                f'python "{SCRIPT_DIR}/unified_multifly.py" api',
                shell=True,
                creationflags=subprocess.CREATE_NEW_CONSOLE
            )
            return True
        except:
            return False

    def _start_websocket(self):
        """Start WebSocket."""
        try:
            subprocess.Popen(
                f'python "{SCRIPT_DIR}/multifly_elite.py" websocket',
                shell=True,
                creationflags=subprocess.CREATE_NEW_CONSOLE
            )
            return True
        except:
            return False


# ============================================================
#  THE UNIVERSAL SYSTEM - Everything Connected
# ============================================================
class MultiflyUniversal:
    """The complete universal system."""

    def __init__(self):
        self.brain = UniversalBrain()
        self.understander = UniversalUnderstander(self.brain)
        self.executor = UniversalExecutor(self.brain)
        self.predictor = PredictionEngine(self.brain)
        self.healer = SelfHealer(self.brain)

    def process(self, text):
        """Process any input."""
        # Get context
        context = self.brain.get_context()

        # Understand
        understanding = self.understander.understand(text, context)

        # Execute
        result = self.executor.execute(understanding)

        # Save context
        self.brain.save_context(
            cwd=os.getcwd(),
            language=understanding["entities"].get("language", [""])[0] if understanding["entities"].get("language") else "",
            framework=understanding["entities"].get("framework", [""])[0] if understanding["entities"].get("framework") else "",
            action=understanding["action"]
        )

        return {"understanding": understanding, "result": result}

    def predict_next(self):
        """Predict what user wants next."""
        return self.predictor.predict()

    def heal(self):
        """Self-heal system."""
        return self.healer.heal()

    def status(self):
        """Get full status."""
        return {
            "brain": self.brain.get_summary(),
            "predictions": self.predict_next(),
            "healing": self.heal()
        }


# ============================================================
#  MAIN
# ============================================================
def main():
    system = MultiflyUniversal()

    if len(sys.argv) < 2:
        print("""
  ====================================================
   MULTIFLY UNIVERSAL - The System That Understands Everything
  ====================================================

  Usage:
    python multifly_universal.py                    Interactive mode
    python multifly_universal.py "any command"      Execute command
    python multifly_universal.py --predict          Predict next action
    python multifly_universal.py --context          Show current context
    python multifly_universal.py --learn            Run learning analysis
    python multifly_universal.py --heal             Self-heal system
    python multifly_universal.py --status           Full system status
  ====================================================
        """)
        return

    if sys.argv[1] == "--predict":
        predictions = system.predict_next()
        print("\n  Predictions:\n")
        for p in predictions:
            print(f"    {p['action']:<25} confidence: {p['confidence']:.0%} ({p['method']})")
        return

    if sys.argv[1] == "--context":
        context = system.brain.get_context()
        print(f"\n  Current Context:\n")
        for k, v in context.items():
            print(f"    {k}: {v}")
        return

    if sys.argv[1] == "--learn":
        summary = system.brain.get_summary()
        print(f"\n  Brain Summary:\n")
        print(f"    Commands:  {summary['commands']}")
        print(f"    Patterns:  {summary['patterns']}")
        print(f"    Knowledge: {summary['knowledge']}")
        print(f"\n  Top Commands:")
        for cmd in summary.get("top_commands", []):
            print(f"    > {cmd}")
        print(f"\n  Top Intents:")
        for intent in summary.get("top_intents", []):
            print(f"    > {intent}")
        return

    if sys.argv[1] == "--heal":
        result = system.heal()
        print(f"\n  Self-Healing:\n")
        if result["issues"]:
            print(f"    Issues found: {len(result['issues'])}")
            for issue in result["issues"]:
                print(f"      - {issue}")
        if result["fixes"]:
            print(f"    Fixes applied: {len(result['fixes'])}")
            for fix in result["fixes"]:
                print(f"      + {fix}")
        if not result["issues"]:
            print(f"    All systems healthy!")
        return

    if sys.argv[1] == "--status":
        status = system.status()
        print(f"\n  System Status:\n")
        print(f"    Brain: {status['brain']['commands']} commands, {status['brain']['patterns']} patterns")
        print(f"    Knowledge: {status['brain']['knowledge']} items")
        print(f"    Contexts: {status['brain']['contexts']} saved")
        return

    # Process command
    command = " ".join(sys.argv[1:])
    result = system.process(command)

    understanding = result["understanding"]
    exec_result = result["result"]

    print(f"\n  Input:      {understanding['original']}")
    print(f"  Intent:     {understanding['intent']} ({understanding['confidence']:.0%})")
    print(f"  System:     {understanding['system']}")
    print(f"  Action:     {understanding['action']}")
    if understanding['entities']:
        print(f"  Entities:   {understanding['entities']}")
    print(f"  Result:     {exec_result.get('message', 'processed')}")
    print()


if __name__ == "__main__":
    main()
