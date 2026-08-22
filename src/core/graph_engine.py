"""
MULTIFLY GRAPH ENGINE
=====================
Unified graph engineering system combining:
- axon: Code analysis, call chains, communities, dead code, flows
- GitNexus: Knowledge graph for AI agents, impact analysis, context
- 3D Graph: Force-directed layout concepts

Features:
- Index any codebase into a knowledge graph
- Trace call chains and dependencies
- Detect communities/clusters
- Find dead code and orphan symbols
- Map execution flows
- Impact analysis (blast radius)
- Natural language queries
- Real-time visualization data
"""

import os
import re
import sys
import json
import sqlite3
from datetime import datetime
from pathlib import Path
from collections import defaultdict, Counter


class GraphNode:
    def __init__(self, uid, name, ntype, file_path, line=0, metadata=None):
        self.uid = uid
        self.name = name
        self.type = ntype
        self.file = file_path
        self.line = line
        self.metadata = metadata or {}
        self.calls = set()
        self.called_by = set()
        self.community = None
        self.health_score = 1.0

    def to_dict(self):
        return {
            "uid": self.uid, "name": self.name, "type": self.type,
            "file": self.file, "line": self.line,
            "calls": list(self.calls), "called_by": list(self.called_by),
            "community": self.community, "health": self.health_score,
        }


class GraphEdge:
    def __init__(self, source, target, etype="calls", weight=1.0):
        self.source = source
        self.target = target
        self.type = etype
        self.weight = weight


class CodeAnalyzer:
    PATTERNS = {
        "python": {
            "function": r"(?:def|async\s+def)\s+(\w+)\s*\(",
            "class": r"class\s+(\w+)\s*(?:\(.*?\))?:",
            "import": r"(?:from\s+(\S+)\s+)?import\s+(.+)",
            "call": r"(\w+)\s*\(",
        },
        "javascript": {
            "function": r"(?:function|const|let|var)\s+(\w+)\s*(?:=\s*(?:async\s*)?\(|=>)",
            "class": r"class\s+(\w+)",
            "import": r"import\s+.*?from\s+['\"](.+?)['\"]",
            "call": r"(\w+)\s*\(",
        },
        "typescript": {
            "function": r"(?:function|const|let|var)\s+(\w+)\s*(?:=\s*(?:async\s*)?\(|=>)",
            "class": r"class\s+(\w+)",
            "interface": r"interface\s+(\w+)",
            "import": r"import\s+.*?from\s+['\"](.+?)['\"]",
            "call": r"(\w+)\s*\(",
        },
        "rust": {
            "function": r"(?:pub\s+)?(?:async\s+)?fn\s+(\w+)",
            "struct": r"(?:pub\s+)?struct\s+(\w+)",
            "trait": r"(?:pub\s+)?trait\s+(\w+)",
            "use": r"use\s+(.+);",
            "call": r"(\w+)\s*\(",
        },
        "go": {
            "function": r"func\s+(?:\([^)]+\)\s+)?(\w+)\s*\(",
            "struct": r"type\s+(\w+)\s+struct",
            "interface": r"type\s+(\w+)\s+interface",
            "import": r"import\s+(?:\(\s*)?\"(.+?)\"",
            "call": r"(\w+)\s*\(",
        },
    }

    EXTENSION_MAP = {
        ".py": "python", ".js": "javascript", ".jsx": "javascript",
        ".ts": "typescript", ".tsx": "typescript",
        ".rs": "rust", ".go": "go",
    }

    def __init__(self):
        self.nodes = {}
        self.edges = []
        self.files = {}

    def analyze_file(self, file_path):
        ext = Path(file_path).suffix
        lang = self.EXTENSION_MAP.get(ext)
        if not lang:
            return
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
        except Exception:
            return

        patterns = self.PATTERNS.get(lang, {})
        lines = content.split("\n")
        defined = {}

        for line_num, line in enumerate(lines, 1):
            ls = line.strip()
            if ls.startswith("#") or ls.startswith("//"):
                continue
            for stype, pattern in patterns.items():
                if stype == "call":
                    continue
                for match in re.finditer(pattern, line):
                    name = match.group(1) if match.lastindex else match.group(0)
                    uid = f"{file_path}:{name}:{line_num}"
                    if uid not in self.nodes:
                        node = GraphNode(uid, name, stype, file_path, line_num, {"language": lang})
                        self.nodes[uid] = node
                        defined[name] = uid

        # Extract calls
        call_pattern = patterns.get("call", r"(\w+)\s*\(")
        for line_num, line in enumerate(lines, 1):
            if line.strip().startswith("#") or line.strip().startswith("//"):
                continue
            calls = re.findall(call_pattern, line)
            for callee in calls:
                if callee in defined:
                    for caller_uid in defined.values():
                        caller_name = self.nodes[caller_uid].name
                        if callee != caller_name:
                            self.edges.append(GraphEdge(caller_uid, defined[callee]))

        self.files[file_path] = {"language": lang, "lines": len(lines), "symbols": len(defined)}

    def analyze_directory(self, directory, exclude=None):
        exclude = exclude or [
            "node_modules", ".git", "__pycache__", "venv", ".venv",
            "dist", "build", ".next", ".obsidian", "target",
            "vendor", "packages", ".build", "coverage",
        ]
        count = 0
        for root, dirs, files in os.walk(directory):
            dirs[:] = [d for d in dirs if d not in exclude]
            for f in files:
                if Path(f).suffix in self.EXTENSION_MAP:
                    self.analyze_file(os.path.join(root, f))
                    count += 1
        return count


class CommunityDetector:
    @staticmethod
    def detect(nodes, edges):
        adj = defaultdict(set)
        for e in edges:
            adj[e.source].add(e.target)
            adj[e.target].add(e.source)

        community = {uid: uid for uid in nodes}
        for _ in range(20):
            changed = False
            for uid in nodes:
                if uid not in adj:
                    continue
                counts = Counter(community[n] for n in adj[uid] if n in community)
                if counts:
                    best = counts.most_common(1)[0][0]
                    if community[uid] != best:
                        community[uid] = best
                        changed = True
            if not changed:
                break

        for uid, c in community.items():
            nodes[uid].community = c
        return dict(Counter(community.values()))


class DeadCodeDetector:
    @staticmethod
    def detect(nodes, edges):
        called = {e.target for e in edges}
        dead = []
        for uid, node in nodes.items():
            if uid not in called and node.type in ("function", "method", "class"):
                if node.name not in ("main", "__main__", "index", "app", "setup"):
                    dead.append(node.to_dict())
        return dead


class ImpactAnalyzer:
    @staticmethod
    def analyze(nodes, edges, target_uid, max_depth=5):
        adj_up = defaultdict(set)
        adj_down = defaultdict(set)
        for e in edges:
            adj_up[e.target].add(e.source)
            adj_down[e.source].add(e.target)

        upstream = set()
        q = [(target_uid, 0)]
        vis = {target_uid}
        while q:
            uid, d = q.pop(0)
            if d >= max_depth:
                continue
            for c in adj_up.get(uid, set()):
                if c not in vis:
                    vis.add(c)
                    upstream.add(c)
                    q.append((c, d + 1))

        downstream = set()
        q = [(target_uid, 0)]
        vis = {target_uid}
        while q:
            uid, d = q.pop(0)
            if d >= max_depth:
                continue
            for c in adj_down.get(uid, set()):
                if c not in vis:
                    vis.add(c)
                    downstream.add(c)
                    q.append((c, d + 1))

        return {
            "target": nodes[target_uid].to_dict() if target_uid in nodes else None,
            "upstream_count": len(upstream),
            "downstream_count": len(downstream),
            "blast_radius": len(upstream) + len(downstream),
            "risk": "HIGH" if len(upstream) > 10 else "MEDIUM" if len(upstream) > 3 else "LOW",
        }


class FlowTracer:
    @staticmethod
    def trace(nodes, edges, start_patterns=None):
        start_patterns = start_patterns or [
            "main", "app", "setup", "run", "start", "index",
            "__init__", "handle", "process", "execute",
        ]
        adj = defaultdict(list)
        for e in edges:
            adj[e.source].append(e.target)

        flows = []
        for uid, node in nodes.items():
            if node.name and any(p in node.name.lower() for p in start_patterns):
                path = [uid]
                visited = {uid}
                cur = uid
                for _ in range(8):
                    neighbors = [n for n in adj.get(cur, []) if n not in visited]
                    if not neighbors:
                        break
                    nxt = max(neighbors, key=lambda n: len(adj.get(n, [])))
                    path.append(nxt)
                    visited.add(nxt)
                    cur = nxt
                if len(path) > 2:
                    flows.append({
                        "entry": node.name,
                        "file": node.file,
                        "path": [nodes[s].name for s in path if s in nodes],
                    })
        return flows


class GraphDB:
    def __init__(self, db_path=None):
        self.db_path = db_path or os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "graph_engine.db"
        )
        self._init()

    def _init(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("""CREATE TABLE IF NOT EXISTS nodes (
            uid TEXT PRIMARY KEY, name TEXT, type TEXT, file TEXT,
            line INTEGER, community TEXT, health REAL DEFAULT 1.0
        )""")
        c.execute("""CREATE TABLE IF NOT EXISTS edges (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source TEXT, target TEXT, type TEXT, weight REAL DEFAULT 1.0
        )""")
        c.execute("""CREATE TABLE IF NOT EXISTS analyses (
            id INTEGER PRIMARY KEY AUTOINCREMENT, repo TEXT,
            nodes_count INTEGER, edges_count INTEGER, analyzed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )""")
        conn.commit()
        conn.close()

    def save(self, nodes, edges):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("DELETE FROM nodes")
        c.execute("DELETE FROM edges")
        for uid, n in nodes.items():
            c.execute("INSERT INTO nodes VALUES (?,?,?,?,?,?,?)",
                      (uid, n.name, n.type, n.file, n.line, n.community, n.health_score))
        for e in edges:
            c.execute("INSERT INTO edges (source, target, type, weight) VALUES (?,?,?,?)",
                      (e.source, e.target, e.type, e.weight))
        conn.commit()
        conn.close()

    def stats(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        s = {
            "nodes": c.execute("SELECT COUNT(*) FROM nodes").fetchone()[0],
            "edges": c.execute("SELECT COUNT(*) FROM edges").fetchone()[0],
            "analyses": c.execute("SELECT COUNT(*) FROM analyses").fetchone()[0],
        }
        conn.close()
        return s


class MultiflyGraphEngine:
    def __init__(self):
        self.analyzer = CodeAnalyzer()
        self.db = GraphDB()
        self.communities = {}

    def analyze(self, repo_path, exclude=None):
        count = self.analyzer.analyze_directory(repo_path, exclude)
        self.communities = CommunityDetector.detect(
            self.analyzer.nodes, self.analyzer.edges
        )
        dead = DeadCodeDetector.detect(self.analyzer.nodes, self.analyzer.edges)
        flows = FlowTracer.trace(self.analyzer.nodes, self.analyzer.edges)
        self.db.save(self.analyzer.nodes, self.analyzer.edges)

        stats = {
            "files": count,
            "nodes": len(self.analyzer.nodes),
            "edges": len(self.analyzer.edges),
            "communities": len(self.communities),
            "dead_code": len(dead),
            "flows": len(flows),
        }
        return {"stats": stats, "dead_code": dead[:20], "flows": flows[:10],
                "top_communities": dict(sorted(self.communities.items(), key=lambda x: -x[1])[:10])}

    def query(self, text):
        matches = []
        for uid, node in self.analyzer.nodes.items():
            if not node.name or not node.file:
                continue
            score = 0
            if text.lower() in node.name.lower():
                score += 10
            if text.lower() in node.file.lower():
                score += 5
            if score > 0:
                matches.append({"node": node.to_dict(), "score": score})
        matches.sort(key=lambda x: -x["score"])
        return matches[:10]

    def impact(self, symbol_name):
        for uid, node in self.analyzer.nodes.items():
            if node.name and node.name == symbol_name:
                return ImpactAnalyzer.analyze(self.analyzer.nodes, self.analyzer.edges, uid)
        return {"error": f"Symbol '{symbol_name}' not found"}

    def health(self):
        nodes = self.analyzer.nodes
        edges = self.analyzer.edges
        total = len(nodes)
        dead = DeadCodeDetector.detect(nodes, edges)
        high_coupling = sum(1 for n in nodes.values() if len(n.calls) + len(n.called_by) > 10)
        health_score = max(0, min(100, 100 - len(dead) * 2 - high_coupling * 3))
        return {
            "score": health_score,
            "symbols": total,
            "edges": len(edges),
            "dead_code": len(dead),
            "high_coupling": high_coupling,
            "communities": len(self.communities),
            "rating": "EXCELLENT" if health_score >= 90 else "GOOD" if health_score >= 70 else "NEEDS WORK",
        }

    def graph_data(self):
        nodes = [{"id": uid, "label": n.name, "type": n.type,
                  "file": os.path.basename(n.file), "community": n.community,
                  "size": len(n.calls) + len(n.called_by) + 1}
                 for uid, n in self.analyzer.nodes.items()]
        edges = [{"source": e.source, "target": e.target, "type": e.type}
                 for e in self.analyzer.edges]
        return {"nodes": nodes, "edges": edges}


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python graph_engine.py [analyze|query|impact|health|stats|graph|dead|flows] [path/symbol]")
        sys.exit(0)

    engine = MultiflyGraphEngine()
    cmd = sys.argv[1]

    if cmd == "analyze":
        path = sys.argv[2] if len(sys.argv) > 2 else os.getcwd()
        result = engine.analyze(path)
        print(json.dumps(result, indent=2, default=str))
    elif cmd == "query":
        q = " ".join(sys.argv[2:])
        print(json.dumps(engine.query(q), indent=2, default=str))
    elif cmd == "impact":
        s = sys.argv[2] if len(sys.argv) > 2 else ""
        print(json.dumps(engine.impact(s), indent=2, default=str))
    elif cmd == "health":
        print(json.dumps(engine.health(), indent=2))
    elif cmd == "stats":
        print(json.dumps(engine.db.stats(), indent=2))
    elif cmd == "graph":
        d = engine.graph_data()
        print(f"Nodes: {len(d['nodes'])}, Edges: {len(d['edges'])}")
    elif cmd == "dead":
        result = engine.analyze(os.getcwd())
        for d in result["dead_code"][:20]:
            print(f"  [DEAD] {d['name']} ({d['type']}) at {d['file']}:{d['line']}")
    elif cmd == "flows":
        result = engine.analyze(os.getcwd())
        for f in result["flows"][:10]:
            print(f"  Flow: {' -> '.join(f['path'][:6])}")
