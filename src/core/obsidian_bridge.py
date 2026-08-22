"""
OBSIDIAN-MULTIFLY BRIDGE
========================
Deep integration between Obsidian knowledge base and Multifly AI system.

This connects:
- Obsidian notes → AI Brain (knowledge retrieval)
- Multifly commands → Obsidian notes (auto-documentation)
- Plugin ecosystem → Enhanced capabilities
- Graph view → System visualization
- All connected via OmniRoute
"""

import json
import os
import sqlite3
import hashlib
from datetime import datetime
from pathlib import Path


class ObsidianBridge:
    """Bridge between Obsidian knowledge base and Multifly AI system."""

    VAULT_PATHS = [
        os.path.expanduser(r"~\Documents\Obsidian"),
        os.path.expanduser(r"~\Documents\MyVault"),
        os.path.expanduser(r"~\Multifly-OTN\vault"),
    ]

    PLUGIN_CATEGORIES = {
        "ai_power": [
            "copilot",
            "obsidian-ai",
            "smart-connections",
            "text-generator",
            "chatgpt-md",
        ],
        "dev_tools": [
            "obsidian-git",
            "obsidian-code-styler",
            "obsidian-marp-export",
            "obsidian-execute-code",
        ],
        "automation": [
            "obsidian-templater",
            "obsidian-kanban",
            "obsidian-tasks",
            "obsidian-dataview",
            "obsidian-advanced-tables",
        ],
        "knowledge": [
            "obsidian-excalidraw",
            "obsidian-graph-analysis",
            "obsidian-juggl",
            "obsidian-mind-map",
        ],
        "sync_publish": [
            "obsidian-git",
            "obsidian-smart-connections",
            "obsidian-readwise",
        ],
    }

    def __init__(self, brain_db=None):
        self.brain_db = brain_db or os.path.expanduser(
            r"~\Multifly-OTN\brain.db"
        )
        self.vault_path = self._find_vault()
        self.plugins_dir = self._get_plugins_dir()
        self._init_bridge_db()

    def _find_vault(self):
        """Find or create the Multifly vault."""
        vault = os.path.join(os.path.dirname(self.brain_db), "obsidian_vault")
        os.makedirs(vault, exist_ok=True)

        # Create vault structure
        dirs = [
            "Daily Notes",
            "Projects",
            "AI Knowledge",
            "Code Snippets",
            "System Logs",
            "LinkedIn Content",
            "Voice Commands",
            "Self Learning",
            "Graph Data",
            "Templates",
        ]
        for d in dirs:
            os.makedirs(os.path.join(vault, d), exist_ok=True)

        return vault

    def _get_plugins_dir(self):
        """Get Obsidian plugins directory."""
        for path in self.VAULT_PATHS:
            plugins = os.path.join(path, ".obsidian", "plugins")
            if os.path.exists(plugins):
                return plugins
        return None

    def _init_bridge_db(self):
        """Initialize bridge database tables."""
        try:
            conn = sqlite3.connect(self.brain_db)
            c = conn.cursor()

            # Knowledge table - stores Obsidian notes indexed for AI
            c.execute("""
                CREATE TABLE IF NOT EXISTS obsidian_knowledge (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    note_path TEXT UNIQUE,
                    title TEXT,
                    content TEXT,
                    tags TEXT,
                    links TEXT,
                    indexed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    relevance_score REAL DEFAULT 0.0
                )
            """)

            # Command history linked to notes
            c.execute("""
                CREATE TABLE IF NOT EXISTS command_notes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    command TEXT,
                    note_path TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Plugin registry
            c.execute("""
                CREATE TABLE IF NOT EXISTS obsidian_plugins (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    plugin_id TEXT UNIQUE,
                    name TEXT,
                    description TEXT,
                    category TEXT,
                    installed BOOLEAN DEFAULT 0,
                    enabled BOOLEAN DEFAULT 0
                )
            """)

            # Auto-generated notes
            c.execute("""
                CREATE TABLE IF NOT EXISTS auto_notes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    note_type TEXT,
                    title TEXT,
                    content TEXT,
                    source TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Bridge DB init error: {e}")

    def index_vault(self):
        """Index all Obsidian notes for AI retrieval."""
        count = 0
        for root, dirs, files in os.walk(self.vault_path):
            # Skip .obsidian folder
            if ".obsidian" in root:
                continue
            for f in files:
                if f.endswith(".md"):
                    filepath = os.path.join(root, f)
                    self._index_note(filepath)
                    count += 1
        return count

    def _index_note(self, filepath):
        """Index a single note for AI retrieval."""
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()

            title = Path(filepath).stem
            tags = self._extract_tags(content)
            links = self._extract_links(content)

            # Calculate relevance based on content
            relevance = min(1.0, len(content) / 5000)

            conn = sqlite3.connect(self.brain_db)
            c = conn.cursor()
            c.execute(
                """INSERT OR REPLACE INTO obsidian_knowledge 
                   (note_path, title, content, tags, links, relevance_score)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (filepath, title, content[:50000], json.dumps(tags),
                 json.dumps(links), relevance),
            )
            conn.commit()
            conn.close()
        except Exception:
            pass

    def _extract_tags(self, content):
        """Extract hashtags from content."""
        import re
        return re.findall(r"#(\w+)", content)

    def _extract_links(self, content):
        """Extract [[wiki links]] from content."""
        import re
        return re.findall(r"\[\[([^\]]+)\]\]", content)

    def search_knowledge(self, query, limit=10):
        """Search indexed knowledge for AI context."""
        conn = sqlite3.connect(self.brain_db)
        c = conn.cursor()
        c.execute(
            """SELECT title, content, relevance_score 
               FROM obsidian_knowledge 
               WHERE content LIKE ? OR title LIKE ?
               ORDER BY relevance_score DESC LIMIT ?""",
            (f"%{query}%", f"%{query}%", limit),
        )
        results = c.fetchall()
        conn.close()
        return results

    def auto_note(self, note_type, title, content, source="multifly"):
        """Auto-generate a note in the vault."""
        date_str = datetime.now().strftime("%Y-%m-%d")
        folder_map = {
            "command": "Voice Commands",
            "project": "Projects",
            "learning": "Self Learning",
            "log": "System Logs",
            "linkedin": "LinkedIn Content",
            "code": "Code Snippets",
            "daily": "Daily Notes",
        }
        folder = folder_map.get(note_type, "Daily Notes")
        note_path = os.path.join(self.vault_path, folder, f"{title}.md")

        # Create note with frontmatter
        frontmatter = f"""---
type: {note_type}
source: {source}
created: {date_str}
tags: [{note_type}, multifly, auto-generated]
---

"""
        full_content = frontmatter + content

        os.makedirs(os.path.dirname(note_path), exist_ok=True)
        with open(note_path, "w", encoding="utf-8") as f:
            f.write(full_content)

        # Log in brain
        try:
            conn = sqlite3.connect(self.brain_db)
            c = conn.cursor()
            c.execute(
                """INSERT INTO auto_notes (note_type, title, content, source)
                   VALUES (?, ?, ?, ?)""",
                (note_type, title, content[:5000], source),
            )
            conn.commit()
            conn.close()
        except Exception:
            pass

        return note_path

    def get_ai_context(self, query):
        """Get relevant knowledge context for AI queries."""
        results = self.search_knowledge(query, limit=5)
        if not results:
            return "No relevant knowledge found in vault."

        context = "RELEVANT KNOWLEDGE FROM VAULT:\n\n"
        for title, content, score in results:
            context += f"### {title} (relevance: {score:.2f})\n"
            context += content[:1000] + "\n\n"
        return context

    def log_command(self, command, note_path=None):
        """Log a voice/system command and optionally create a note."""
        try:
            conn = sqlite3.connect(self.brain_db)
            c = conn.cursor()
            c.execute(
                "INSERT INTO command_notes (command, note_path) VALUES (?, ?)",
                (command, note_path),
            )
            conn.commit()
            conn.close()
        except Exception:
            pass

    def get_vault_stats(self):
        """Get statistics about the vault."""
        stats = {
            "total_notes": 0,
            "total_folders": 0,
            "total_size": 0,
            "by_folder": {},
        }

        for root, dirs, files in os.walk(self.vault_path):
            if ".obsidian" in root:
                continue
            stats["total_folders"] += len(dirs)
            for f in files:
                if f.endswith(".md"):
                    stats["total_notes"] += 1
                    folder = os.path.basename(root)
                    stats["by_folder"][folder] = (
                        stats["by_folder"].get(folder, 0) + 1
                    )
                    stats["total_size"] += os.path.getsize(
                        os.path.join(root, f)
                    )

        return stats

    def export_graph_data(self):
        """Export knowledge graph data for visualization."""
        notes = []
        edges = []

        for root, dirs, files in os.walk(self.vault_path):
            if ".obsidian" in root:
                continue
            for f in files:
                if f.endswith(".md"):
                    filepath = os.path.join(root, f)
                    title = Path(filepath).stem
                    notes.append({"id": title, "group": os.path.basename(root)})

                    try:
                        with open(filepath, "r", encoding="utf-8") as fh:
                            content = fh.read()
                        links = self._extract_links(content)
                        for link in links:
                            edges.append({"source": title, "target": link})
                    except Exception:
                        pass

        return {"nodes": notes, "edges": edges}


class ObsidianPluginManager:
    """Manage Obsidian plugins from Multifly."""

    def __init__(self, plugins_dir):
        self.plugins_dir = plugins_dir

    def list_installed(self):
        """List all installed plugins."""
        if not self.plugins_dir or not os.path.exists(self.plugins_dir):
            return []
        return [
            d
            for d in os.listdir(self.plugins_dir)
            if os.path.isdir(os.path.join(self.plugins_dir, d))
        ]

    def is_enabled(self, plugin_id):
        """Check if a plugin is enabled."""
        manifest = os.path.join(
            self.plugins_dir, plugin_id, "manifest.json"
        )
        return os.path.exists(manifest)

    def get_community_plugins(self):
        """Get the full community plugin list."""
        plugins_json = os.path.join(
            os.path.dirname(self.plugins_dir),
            "..",
            "..",
            "..",
            "obsidian-releases",
            "community-plugins.json",
        )
        if os.path.exists(plugins_json):
            with open(plugins_json, "r", encoding="utf-8") as f:
                return json.load(f)
        return []


if __name__ == "__main__":
    bridge = ObsidianBridge()

    print("=== OBSIDIAN-MULTIFLY BRIDGE ===")
    print(f"Vault: {bridge.vault_path}")
    print(f"Plugins: {bridge.plugins_dir}")

    # Index vault
    count = bridge.index_vault()
    print(f"Indexed {count} notes")

    # Get stats
    stats = bridge.get_vault_stats()
    print(f"Total notes: {stats['total_notes']}")
    print(f"Total folders: {stats['total_folders']}")
    print(f"Vault size: {stats['total_size'] / 1024:.1f} KB")
    print(f"By folder: {json.dumps(stats['by_folder'], indent=2)}")

    # Test auto-note
    note = bridge.auto_note(
        "daily",
        f"System Status {datetime.now().strftime('%Y-%m-%d')}",
        f"# System Status\n\nAll systems operational.\n\n- OmniRoute: Online\n- Voice: Active\n- Brain: Learning\n",
        "multifly-auto",
    )
    print(f"Auto-note created: {note}")
