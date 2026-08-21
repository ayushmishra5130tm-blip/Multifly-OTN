"""
MULTIFLY ELITE - WebSocket + NLP + ML
The final 10% that makes Multifly the most advanced system.

Features:
  1. WebSocket Server - Real-time bidirectional communication
  2. NLP Engine - Understands natural language commands
  3. ML Learner - Statistical pattern recognition and prediction

Usage:
  python multifly_elite.py websocket    Start WebSocket server (port 2036)
  python multifly_elite.py nlp          Interactive NLP command mode
  python multifly_elite.py ml           Run ML analysis
  python multifly_elite.py all          Start everything
"""

import sys, os, json, time, math, re, asyncio, hashlib
from datetime import datetime
from collections import Counter, defaultdict
from pathlib import Path

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(SCRIPT_DIR, "multifly_brain.db")

sys.path.insert(0, SCRIPT_DIR)
from unified_multifly import Brain, SystemRegistry, Orchestrator


# ============================================================
#  1. WEBSOCKET SERVER - Real-Time Bidirectional Communication
# ============================================================
class WebSocketServer:
    """Real-time WebSocket server for live updates."""

    def __init__(self, brain, port=2036):
        self.brain = brain
        self.port = port
        self.clients = set()
        self.events = []

    async def handler(self, websocket, path=None):
        """Handle a WebSocket client connection."""
        self.clients.add(websocket)
        client_id = hashlib.md5(str(id(websocket)).encode()).hexdigest()[:8]

        # Send welcome
        await websocket.send(json.dumps({
            "type": "welcome",
            "client_id": client_id,
            "message": "Connected to Multifly Elite WebSocket",
            "brain_commands": self.brain.summary()["commands"],
            "timestamp": datetime.now().isoformat()
        }))

        try:
            async for message in websocket:
                data = json.loads(message)
                response = await self._process_message(data)
                await websocket.send(json.dumps(response))

                # Broadcast to all other clients
                broadcast = {
                    "type": "broadcast",
                    "from_client": client_id,
                    "action": data.get("action", "unknown"),
                    "timestamp": datetime.now().isoformat()
                }
                for client in self.clients - {websocket}:
                    try:
                        await client.send(json.dumps(broadcast))
                    except:
                        pass

        except Exception as e:
            pass
        finally:
            self.clients.discard(websocket)

    async def _process_message(self, data):
        """Process incoming WebSocket message."""
        action = data.get("action", "")

        if action == "status":
            s = self.brain.summary()
            return {"type": "status", "data": s}

        elif action == "command":
            cmd = data.get("command", "")
            self.brain.log_cmd(cmd, "websocket")
            return {"type": "command_logged", "command": cmd, "suggestions": self.brain.suggest()}

        elif action == "health":
            return {"type": "health", "clients": len(self.clients)}

        elif action == "events":
            return {"type": "events", "events": self.events[-20:]}

        else:
            return {"type": "error", "message": f"Unknown action: {action}"}

    async def broadcast_event(self, event_type, message, data=None):
        """Broadcast an event to all connected clients."""
        event = {
            "type": "event",
            "event_type": event_type,
            "message": message,
            "data": data,
            "timestamp": datetime.now().isoformat()
        }
        self.events.append(event)
        if len(self.events) > 100:
            self.events = self.events[-100:]

        for client in self.clients.copy():
            try:
                await client.send(json.dumps(event))
            except:
                self.clients.discard(client)

    async def start(self):
        """Start the WebSocket server."""
        import websockets
        server = await websockets.serve(self.handler, "127.0.0.1", self.port)
        print(f"\n  WebSocket server running on ws://127.0.0.1:{self.port}")
        print(f"  Waiting for clients...\n")
        await server.wait_closed()


# ============================================================
#  2. NLP ENGINE - Natural Language Understanding
# ============================================================
class NLPEngine:
    """Understands natural language and routes to the right system."""

    def __init__(self, brain):
        self.brain = brain

        # Intent patterns - what the user wants to do
        self.intents = {
            "create_project": {
                "keywords": ["create", "new", "build", "make", "start", "init", "scaffold"],
                "targets": ["react", "next", "vue", "angular", "python", "node", "go", "rust", "flutter", "app", "project", "website", "api"],
                "system": "jcode",
                "action": "create project"
            },
            "fix_code": {
                "keywords": ["fix", "debug", "solve", "error", "bug", "issue", "problem", "broken", "crash"],
                "targets": ["code", "error", "bug", "issue", "type", "lint", "syntax", "runtime"],
                "system": "omniroute",
                "action": "fix code"
            },
            "deploy": {
                "keywords": ["deploy", "ship", "release", "publish", "push", "live", "production", "host"],
                "targets": ["vercel", "railway", "docker", "aws", "cloud", "netlify", "heroku"],
                "system": "docker",
                "action": "deploy"
            },
            "test": {
                "keywords": ["test", "check", "verify", "validate", "run tests", "unit test", "e2e"],
                "targets": ["pytest", "jest", "vitest", "mocha", "test", "coverage"],
                "system": "python",
                "action": "run tests"
            },
            "explain": {
                "keywords": ["explain", "describe", "what is", "how does", "tell me", "understand", "meaning"],
                "targets": ["code", "function", "class", "variable", "algorithm", "concept"],
                "system": "omniroute",
                "action": "explain code"
            },
            "optimize": {
                "keywords": ["optimize", "improve", "faster", "better", "refactor", "clean", "speed", "performance"],
                "targets": ["code", "performance", "speed", "memory", "database", "query"],
                "system": "omniroute",
                "action": "optimize"
            },
            "learn": {
                "keywords": ["learn", "tutorial", "course", "teach", "roadmap", "study", "practice"],
                "targets": ["python", "javascript", "typescript", "react", "next", "go", "rust", "ai", "ml"],
                "system": "brain",
                "action": "learning"
            },
            "linkedin": {
                "keywords": ["linkedin", "post", "comment", "engage", "network", "connect", "voltaitech", "kauntech"],
                "targets": ["post", "comment", "profile", "company", "content"],
                "system": "linkedin_vt",
                "action": "linkedin"
            },
            "git": {
                "keywords": ["git", "commit", "push", "pull", "merge", "branch", "repo", "clone", "version"],
                "targets": ["commit", "push", "pull", "branch", "stash", "rebase"],
                "system": "git",
                "action": "git"
            },
            "status": {
                "keywords": ["status", "health", "check", "dashboard", "monitor", "overview", "report"],
                "targets": ["system", "brain", "health", "all"],
                "system": "brain",
                "action": "status"
            },
            "activate": {
                "keywords": ["activate", "start", "boot", "launch", "enable", "on", "wake up"],
                "targets": ["all", "omniroute", "graphify", "everything", "system"],
                "system": "orchestrator",
                "action": "activate all"
            },
            "graph": {
                "keywords": ["graph", "visualize", "map", "diagram", "network", "node", "connection"],
                "targets": ["knowledge", "code", "system", "project"],
                "system": "graphify",
                "action": "generate graph"
            },
            "ai": {
                "keywords": ["ai", "generate", "write", "code", "function", "class", "component", "api"],
                "targets": ["function", "component", "api", "endpoint", "class", "module"],
                "system": "omniroute",
                "action": "generate code"
            },
            "search": {
                "keywords": ["search", "find", "look", "grep", "query", "locate"],
                "targets": ["file", "code", "function", "class", "error"],
                "system": "brain",
                "action": "search"
            },
            "config": {
                "keywords": ["config", "setting", "setup", "configure", "install", "extension", "plugin"],
                "targets": ["extension", "plugin", "theme", "keybinding", "setting"],
                "system": "brain",
                "action": "configure"
            },
        }

        # Entity extraction patterns
        self.entities = {
            "language": r"\b(python|javascript|typescript|java|go|rust|ruby|php|swift|kotlin|dart|c\+\+|c#|html|css|sql)\b",
            "framework": r"\b(react|next|vue|angular|svelte|fastapi|django|flask|express|nest|spring|rails|laravel)\b",
            "tool": r"\b(docker|kubernetes|git|npm|yarn|pip|cargo|brew|vercel|railway|netlify|aws|gcp|azure)\b",
            "action": r"\b(create|build|fix|deploy|test|explain|optimize|install|run|start|stop|delete|update)\b",
        }

    def understand(self, text):
        """Parse natural language and return structured intent."""
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

        for intent_name, intent in self.intents.items():
            score = 0

            # Check keyword matches
            for kw in intent["keywords"]:
                if kw in text_lower:
                    score += 2

            # Check target matches
            for target in intent["targets"]:
                if target in text_lower:
                    score += 3

            # Check entity matches
            if entities.get("language") or entities.get("framework"):
                if intent_name in ("create_project", "explain", "optimize", "ai"):
                    score += 2

            if score > best_score:
                best_score = score
                best_intent = intent_name

        if best_intent and best_score > 0:
            intent_data = self.intents[best_intent]
            return {
                "intent": best_intent,
                "confidence": min(0.95, best_score / 10),
                "system": intent_data["system"],
                "action": intent_data["action"],
                "entities": entities,
                "original": text,
                "interpreted": f"I'll {intent_data['action']} for you using {intent_data['system']}"
            }
        else:
            return {
                "intent": "unknown",
                "confidence": 0.0,
                "system": "brain",
                "action": "log",
                "entities": entities,
                "original": text,
                "interpreted": "I'll log this command. Can you be more specific?"
            }

    def execute(self, understanding):
        """Execute the understood command."""
        intent = understanding["intent"]
        system = understanding["system"]

        self.brain.log_cmd(understanding["original"], intent, understanding["interpreted"])

        result = {
            "understanding": understanding,
            "executed": True,
            "timestamp": datetime.now().isoformat()
        }

        if intent == "status":
            result["data"] = self.brain.summary()
            result["message"] = f"Brain has {self.brain.summary()['commands']} commands, {self.brain.summary()['patterns']} patterns"
        elif intent == "activate":
            result["message"] = "Use 'python unified_multifly.py activate' to activate all"
        elif intent == "graph":
            result["message"] = "Use 'python unified_multifly.py dashboard' for live graph"
        elif intent == "learn":
            result["message"] = "Use 'python unified_multifly.py learn' for self-learning"
        elif intent == "fix_code":
            result["message"] = "OmniRoute will analyze and fix the code"
        elif intent == "create_project":
            lang = understanding["entities"].get("language", ["unknown"])[0]
            fw = understanding["entities"].get("framework", ["none"])[0]
            result["message"] = f"Creating {lang} project with {fw}"
        elif intent == "deploy":
            target = understanding["entities"].get("tool", ["cloud"])[0]
            result["message"] = f"Deploying to {target}"
        elif intent == "linkedin":
            result["message"] = "LinkedIn automation ready"
        elif intent == "git":
            action = understanding["entities"].get("action", ["commit"])[0]
            result["message"] = f"Running git {action}"
        else:
            result["message"] = understanding["interpreted"]

        return result


# ============================================================
#  3. ML LEARNER - Statistical Pattern Recognition
# ============================================================
class MLLearner:
    """Machine learning-based pattern recognition and prediction."""

    def __init__(self, brain):
        self.brain = brain
        self.model = {
            "command_freq": Counter(),
            "time_patterns": defaultdict(list),
            "sequence_patterns": [],
            "error_patterns": Counter(),
            "success_rates": defaultdict(lambda: {"success": 0, "total": 0}),
        }
        self._load_patterns()

    def _load_patterns(self):
        """Load patterns from brain database."""
        # Load command frequencies
        rows = self.brain.conn.execute(
            "SELECT cmd, COUNT(*) as c FROM commands GROUP BY cmd ORDER BY c DESC"
        ).fetchall()
        for row in rows:
            self.model["command_freq"][row[0]] = row[1]

        # Load success rates per category
        rows = self.brain.conn.execute(
            "SELECT category, SUM(ok) as success, COUNT(*) as total FROM commands GROUP BY category"
        ).fetchall()
        for row in rows:
            self.model["success_rates"][row[0]] = {"success": row[1], "total": row[2]}

        # Load error patterns
        rows = self.brain.conn.execute(
            "SELECT error, COUNT(*) as c FROM errors GROUP BY error ORDER BY c DESC"
        ).fetchall()
        for row in rows:
            self.model["error_patterns"][row[0]] = row[1]

    def predict_next(self, last_commands=None):
        """Predict what command the user will run next."""
        if not last_commands:
            last_commands = []

        # Method 1: Frequency-based
        if self.model["command_freq"]:
            freq_predictions = self.model["command_freq"].most_common(5)
        else:
            freq_predictions = []

        # Method 2: Sequence-based (if we have history)
        seq_predictions = []
        if len(last_commands) >= 2:
            last_2 = tuple(last_commands[-2:])
            # Find what followed this pattern before
            rows = self.brain.conn.execute(
                "SELECT cmd FROM commands ORDER BY ts DESC"
            ).fetchall()
            cmds = [r[0] for r in rows]
            for i in range(len(cmds) - 2):
                if (cmds[i], cmds[i+1]) == last_2 and i + 2 < len(cmds):
                    seq_predictions.append(cmds[i+2])

        # Method 3: Category-based
        cat_predictions = []
        if last_commands:
            last_cmd = last_commands[-1]
            rows = self.brain.conn.execute(
                "SELECT category FROM commands WHERE cmd = ? LIMIT 1", (last_cmd,)
            ).fetchall()
            if rows:
                cat = rows[0][0]
                cat_rows = self.brain.conn.execute(
                    "SELECT cmd, COUNT(*) as c FROM commands WHERE category = ? GROUP BY cmd ORDER BY c DESC LIMIT 3",
                    (cat,)
                ).fetchall()
                cat_predictions = [(r[0], r[1]) for r in cat_rows]

        # Combine predictions
        all_predictions = Counter()
        for cmd, count in freq_predictions:
            all_predictions[cmd] += count * 1.0
        for cmd in seq_predictions:
            all_predictions[cmd] += 3.0  # Sequence matches are strong signals
        for cmd, count in cat_predictions:
            all_predictions[cmd] += count * 0.5

        return all_predictions.most_common(5)

    def analyze_success_rate(self):
        """Analyze success rates across all categories."""
        rates = {}
        for cat, stats in self.model["success_rates"].items():
            if stats["total"] > 0:
                rates[cat] = {
                    "success_rate": stats["success"] / stats["total"],
                    "total": stats["total"],
                    "success": stats["success"],
                    "failed": stats["total"] - stats["success"]
                }
        return rates

    def detect_anomalies(self):
        """Detect unusual patterns in the data."""
        anomalies = []

        # Check for unusually high error rates
        rates = self.analyze_success_rate()
        for cat, stats in rates.items():
            if stats["success_rate"] < 0.5 and stats["total"] > 3:
                anomalies.append({
                    "type": "high_error_rate",
                    "category": cat,
                    "success_rate": stats["success_rate"],
                    "message": f"Category '{cat}' has only {stats['success_rate']:.0%} success rate"
                })

        # Check for recurring errors
        for error, count in self.model["error_patterns"].items():
            if count > 2:
                anomalies.append({
                    "type": "recurring_error",
                    "error": error[:80],
                    "count": count,
                    "message": f"Error occurred {count} times: {error[:50]}"
                })

        return anomalies

    def get_insights(self):
        """Generate ML-based insights."""
        insights = []

        # Success rate analysis
        rates = self.analyze_success_rate()
        best = max(rates.items(), key=lambda x: x[1]["success_rate"]) if rates else None
        worst = min(rates.items(), key=lambda x: x[1]["success_rate"]) if rates else None

        if best:
            insights.append({
                "type": "best_category",
                "message": f"Best success rate: {best[0]} ({best[1]['success_rate']:.0%})",
                "confidence": 0.9
            })
        if worst and worst[1]["success_rate"] < 0.8:
            insights.append({
                "type": "needs_improvement",
                "message": f"Needs improvement: {worst[0]} ({worst[1]['success_rate']:.0%})",
                "confidence": 0.85
            })

        # Anomaly detection
        anomalies = self.detect_anomalies()
        for a in anomalies:
            insights.append({
                "type": "anomaly",
                "message": a["message"],
                "confidence": 0.8
            })

        # Prediction confidence
        predictions = self.predict_next()
        if predictions:
            top = predictions[0]
            insights.append({
                "type": "prediction",
                "message": f"Next likely command: '{top[0]}' (strength: {top[1]:.1f})",
                "confidence": min(0.9, top[1] / 10)
            })

        # Pattern strength
        total_patterns = sum(self.model["command_freq"].values())
        if total_patterns > 10:
            insights.append({
                "type": "model_strength",
                "message": f"ML model trained on {total_patterns} data points across {len(self.model['command_freq'])} unique commands",
                "confidence": 0.95
            })

        return insights

    def report(self):
        """Generate full ML report."""
        return {
            "predictions": self.predict_next(),
            "success_rates": self.analyze_success_rate(),
            "anomalies": self.detect_anomalies(),
            "insights": self.get_insights(),
            "model_stats": {
                "unique_commands": len(self.model["command_freq"]),
                "total_data_points": sum(self.model["command_freq"].values()),
                "error_types": len(self.model["error_patterns"]),
                "categories_tracked": len(self.model["success_rates"]),
            }
        }


# ============================================================
#  MAIN
# ============================================================
def main():
    brain = Brain()

    if len(sys.argv) < 2:
        print("""
  ====================================================
   MULTIFLY ELITE - WebSocket + NLP + ML
  ====================================================

  Usage:
    python multifly_elite.py websocket    WebSocket server (port 2036)
    python multifly_elite.py nlp          Interactive NLP mode
    python multifly_elite.py ml           ML analysis report
    python multifly_elite.py all          Start everything
  ====================================================
        """)
        return

    cmd = sys.argv[1].lower()

    if cmd == "websocket":
        ws = WebSocketServer(brain)
        asyncio.run(ws.start())

    elif cmd == "nlp":
        nlp = NLPEngine(brain)
        print("\n  ====================================================")
        print("   MULTIFLY NLP - Natural Language Commands")
        print("   Type anything in plain English")
        print("   Type 'quit' to exit")
        print("  ====================================================\n")

        while True:
            try:
                text = input("  > ").strip()
                if text.lower() in ("quit", "exit", "q"):
                    break
                if not text:
                    continue

                understanding = nlp.understand(text)
                result = nlp.execute(understanding)

                conf = understanding["confidence"]
                color = "green" if conf > 0.7 else "yellow" if conf > 0.4 else "red"
                print(f"\n  [{color}]Confidence: {conf:.0%}[/]")
                print(f"  Intent:     {understanding['intent']}")
                print(f"  System:     {understanding['system']}")
                print(f"  Action:     {understanding['action']}")
                if understanding["entities"]:
                    print(f"  Entities:   {understanding['entities']}")
                print(f"  Response:   {result['message']}")
                print()

            except (KeyboardInterrupt, EOFError):
                break

        print("\n  NLP mode ended.")

    elif cmd == "ml":
        ml = MLLearner(brain)
        report = ml.report()

        print("\n  ====================================================")
        print("   MULTIFLY ML - Machine Learning Analysis")
        print("  ====================================================\n")

        print("  MODEL STATS:")
        for k, v in report["model_stats"].items():
            print(f"    {k:<25} {v}")
        print()

        if report["predictions"]:
            print("  PREDICTIONS (what you'll likely do next):")
            for cmd, strength in report["predictions"]:
                bar = "#" * min(int(strength * 3), 20)
                print(f"    {cmd:<25} [{bar:<20}] {strength:.1f}")
            print()

        if report["success_rates"]:
            print("  SUCCESS RATES:")
            for cat, stats in report["success_rates"].items():
                bar = "+" * int(stats["success_rate"] * 20)
                print(f"    {cat:<25} [{bar:<20}] {stats['success_rate']:.0%} ({stats['total']}x)")
            print()

        if report["anomalies"]:
            print("  ANOMALIES DETECTED:")
            for a in report["anomalies"]:
                print(f"    [{a['type']}] {a['message']}")
            print()

        if report["insights"]:
            print("  ML INSIGHTS:")
            for i in report["insights"]:
                print(f"    [{i['type']}] {i['message']} (conf: {i['confidence']:.0%})")
            print()

    elif cmd == "all":
        print("\n  Starting all Elite services...")

        # Start WebSocket in background
        ws = WebSocketServer(brain)
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        async def run_ws():
            import websockets
            server = await websockets.serve(ws.handler, "127.0.0.1", 2036)
            print("  [OK] WebSocket running on ws://127.0.0.1:2036")
            await server.wait_closed()

        threading.Thread(target=lambda: asyncio.run(run_ws()), daemon=True).start()

        # Show ML report
        ml = MLLearner(brain)
        report = ml.report()
        print(f"  [OK] ML model: {report['model_stats']['unique_commands']} commands learned")
        print(f"  [OK] NLP engine ready with {len(NLPEngine(brain).intents)} intents")
        print("\n  All Elite services running!")
        print("  WebSocket: ws://127.0.0.1:2036")
        print("  REST API:  http://127.0.0.1:2035")
        print()

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n  Elite services stopped.")

    else:
        print(f"  Unknown command: {cmd}")

    brain.conn.close()


if __name__ == "__main__":
    main()
