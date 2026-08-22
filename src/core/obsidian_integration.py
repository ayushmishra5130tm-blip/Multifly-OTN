"""
OBSIDIAN INTEGRATION - MULTIFLY UNIVERSAL
==========================================
Connects Obsidian knowledge management with all Multifly systems.

Features:
- Auto-document commands and projects in Obsidian
- Knowledge retrieval for AI responses
- Plugin ecosystem management
- Graph visualization
- Daily notes automation
- LinkedIn content drafts
- Code snippet library
"""

import json
import os
import sys
import sqlite3
from datetime import datetime
from pathlib import Path

# Add parent to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try:
    from obsidian_bridge import ObsidianBridge
except ImportError:
    from core.obsidian_bridge import ObsidianBridge


class MultiflyObsidian:
    """Full Obsidian integration for Multifly."""

    def __init__(self):
        self.bridge = ObsidianBridge()
        self.vault = self.bridge.vault_path
        self._setup_templates()
        self._create_welcome_note()

    def _setup_templates(self):
        """Create templates for auto-generated notes."""
        templates_dir = os.path.join(self.vault, "Templates")
        os.makedirs(templates_dir, exist_ok=True)

        templates = {
            "daily_note.md": """---
type: daily
created: {{date}}
tags: [daily, log]
---

# {{date}} - Daily Note

## Morning Goals
- [ ] 

## Commands Executed
- 

## Learning
- 

## Notes
- 

## End of Day Review
- What went well:
- What to improve:
""",
            "project_note.md": """---
type: project
created: {{date}}
tags: [project, {{project_name}}]
---

# {{project_name}}

## Overview


## Tech Stack


## Progress
- [ ] Setup
- [ ] Development
- [ ] Testing
- [ ] Deployment

## Notes


## Links
- Repo: 
- Deploy: 
""",
            "code_snippet.md": """---
type: code
language: {{language}}
tags: [code, {{language}}]
created: {{date}}
---

# {{title}}

```{{language}}
{{code}}
```

## Usage


## Notes
""",
            "linkedin_post.md": """---
type: linkedin
status: draft
created: {{date}}
tags: [linkedin, content]
---

# LinkedIn Post Draft

## Hook


## Body


## CTA


## Hashtags

""",
            "voice_command_log.md": """---
type: command-log
created: {{date}}
tags: [voice, command, log]
---

# Voice Command Log - {{date}}

| Time | Command | Result |
|------|---------|--------|
| {{time}} | {{command}} | {{result}} |
""",
        }

        for name, content in templates.items():
            path = os.path.join(templates_dir, name)
            if not os.path.exists(path):
                with open(path, "w", encoding="utf-8") as f:
                    f.write(content)

    def _create_welcome_note(self):
        """Create welcome note in vault."""
        welcome_path = os.path.join(self.vault, "WELCOME.md")
        if not os.path.exists(welcome_path):
            with open(welcome_path, "w", encoding="utf-8") as f:
                f.write("""---
type: system
tags: [welcome, multifly]
---

# Welcome to Multifly Knowledge Vault

This is your AI-powered knowledge management system.

## Quick Commands

Say "RSS" + command:

- **"RSS note [topic]"** - Create a note
- **"RSS search [query]"** - Search your knowledge
- **"RSS daily"** - Create daily note
- **"RSS project [name]"** - Create project note
- **"RSS code [snippet]"** - Save code snippet
- **"RSS linkedin [topic]"** - Draft LinkedIn post
- **"RSS graph"** - View knowledge graph

## Vault Structure

- **Daily Notes/** - Auto-generated daily logs
- **Projects/** - Project documentation
- **AI Knowledge/** - AI learning and insights
- **Code Snippets/** - Saved code snippets
- **LinkedIn Content/** - LinkedIn post drafts
- **Voice Commands/** - Command history
- **Self Learning/** - Self-improvement notes
- **System Logs/** - System activity logs
- **Graph Data/** - Knowledge graph data
- **Templates/** - Note templates

## Integration

This vault is connected to:
- OmniRoute AI Server
- Voice Command System
- LinkedIn Automation
- WhatsApp Automation
- Self-Learning Engine
- Knowledge Graph

All notes are searchable by the AI brain.
""")

    def process_command(self, command, result=""):
        """Process a voice/system command and log it."""
        date_str = datetime.now().strftime("%Y-%m-%d")
        time_str = datetime.now().strftime("%H:%M:%S")

        # Log command
        self.bridge.log_command(command)

        # Auto-create note based on command type
        if "create" in command.lower() or "project" in command.lower():
            project_name = command.replace("create", "").replace("project", "").strip()
            self.bridge.auto_note(
                "project",
                f"Project - {project_name}",
                f"# {project_name}\n\nCreated via voice command.\n\nCommand: {command}\nResult: {result}\n",
                "voice-command",
            )
        elif "linkedin" in command.lower():
            self.bridge.auto_note(
                "linkedin",
                f"LinkedIn - {date_str}",
                f"# LinkedIn Activity\n\nCommand: {command}\nResult: {result}\n",
                "voice-command",
            )
        elif "code" in command.lower() or "function" in command.lower():
            self.bridge.auto_note(
                "code",
                f"Code - {date_str} {time_str}",
                f"# Code Snippet\n\nCommand: {command}\n\n```\n{result}\n```\n",
                "voice-command",
            )
        else:
            self.bridge.auto_note(
                "command",
                f"Command - {date_str} {time_str}",
                f"# Command Log\n\n**Command:** {command}\n**Time:** {time_str}\n**Result:** {result}\n",
                "voice-command",
            )

    def search(self, query):
        """Search knowledge base."""
        return self.bridge.search_knowledge(query)

    def get_context(self, query):
        """Get AI context from knowledge base."""
        return self.bridge.get_ai_context(query)

    def daily_note(self):
        """Create or update today's daily note."""
        date_str = datetime.now().strftime("%Y-%m-%d")
        day_name = datetime.now().strftime("%A")

        template_path = os.path.join(
            self.vault, "Templates", "daily_note.md"
        )
        if os.path.exists(template_path):
            with open(template_path, "r", encoding="utf-8") as f:
                content = f.read()
            content = content.replace("{{date}}", f"{date_str} ({day_name})")
        else:
            content = f"# {date_str} ({day_name})\n\n## Notes\n\n"

        note_path = os.path.join(
            self.vault, "Daily Notes", f"{date_str}.md"
        )

        # Append if exists
        if os.path.exists(note_path):
            with open(note_path, "r", encoding="utf-8") as f:
                existing = f.read()
            content = existing + f"\n\n---\n\nUpdated at {datetime.now().strftime('%H:%M:%S')}\n"

        with open(note_path, "w", encoding="utf-8") as f:
            f.write(content)

        return note_path

    def project_note(self, project_name):
        """Create a project note."""
        template_path = os.path.join(
            self.vault, "Templates", "project_note.md"
        )
        if os.path.exists(template_path):
            with open(template_path, "r", encoding="utf-8") as f:
                content = f.read()
            content = content.replace("{{project_name}}", project_name)
            content = content.replace(
                "{{date}}", datetime.now().strftime("%Y-%m-%d")
            )
        else:
            content = f"# {project_name}\n\n## Overview\n\n"

        note_path = os.path.join(
            self.vault, "Projects", f"{project_name}.md"
        )
        os.makedirs(os.path.dirname(note_path), exist_ok=True)
        with open(note_path, "w", encoding="utf-8") as f:
            f.write(content)

        return note_path

    def code_snippet(self, title, code, language="python"):
        """Save a code snippet."""
        template_path = os.path.join(
            self.vault, "Templates", "code_snippet.md"
        )
        if os.path.exists(template_path):
            with open(template_path, "r", encoding="utf-8") as f:
                content = f.read()
            content = content.replace("{{title}}", title)
            content = content.replace("{{language}}", language)
            content = content.replace("{{code}}", code)
            content = content.replace(
                "{{date}}", datetime.now().strftime("%Y-%m-%d")
            )
        else:
            content = f"# {title}\n\n```{language}\n{code}\n```\n"

        note_path = os.path.join(
            self.vault, "Code Snippets", f"{title}.md"
        )
        os.makedirs(os.path.dirname(note_path), exist_ok=True)
        with open(note_path, "w", encoding="utf-8") as f:
            f.write(content)

        return note_path

    def linkedin_draft(self, topic, content=""):
        """Create a LinkedIn post draft."""
        date_str = datetime.now().strftime("%Y-%m-%d")
        template_path = os.path.join(
            self.vault, "Templates", "linkedin_post.md"
        )
        if os.path.exists(template_path):
            with open(template_path, "r", encoding="utf-8") as f:
                note_content = f.read()
            note_content = note_content.replace("{{date}}", date_str)
        else:
            note_content = f"# LinkedIn Post - {topic}\n\n"

        if content:
            note_content += f"\n{content}\n"

        note_path = os.path.join(
            self.vault, "LinkedIn Content", f"{topic} - {date_str}.md"
        )
        os.makedirs(os.path.dirname(note_path), exist_ok=True)
        with open(note_path, "w", encoding="utf-8") as f:
            f.write(note_content)

        return note_path

    def stats(self):
        """Get vault statistics."""
        return self.bridge.get_vault_stats()

    def graph_data(self):
        """Get knowledge graph data."""
        return self.bridge.export_graph_data()

    def list_plugins(self):
        """List recommended plugins for Multifly."""
        recommended = {
            "AI Power": [
                ("copilot", "AI assistant for your notes"),
                ("smart-connections", "AI-powered note connections"),
                ("text-generator", "GPT text generation"),
            ],
            "Dev Tools": [
                ("obsidian-git", "Git integration"),
                ("obsidian-execute-code", "Run code in notes"),
                ("obsidian-code-styler", "Code block styling"),
            ],
            "Automation": [
                ("obsidian-templater", "Advanced templates"),
                ("obsidian-dataview", "Query your notes"),
                ("obsidian-kanban", "Kanban boards"),
                ("obsidian-tasks", "Task management"),
            ],
            "Knowledge": [
                ("excalidraw", "Draw diagrams"),
                ("obsidian-juggl", "Advanced graph view"),
                ("obsidian-mind-map", "Mind maps"),
            ],
        }
        return recommended


def main():
    """CLI for Obsidian integration."""
    if len(sys.argv) < 2:
        print("=== MULTIFLY OBSIDIAN ===")
        print("Usage:")
        print("  python obsidian_integration.py stats")
        print("  python obsidian_integration.py search [query]")
        print("  python obsidian_integration.py daily")
        print("  python obsidian_integration.py project [name]")
        print("  python obsidian_integration.py code [title]")
        print("  python obsidian_integration.py linkedin [topic]")
        print("  python obsidian_integration.py graph")
        print("  python obsidian_integration.py plugins")
        return

    obs = MultiflyObsidian()
    cmd = sys.argv[1]

    if cmd == "stats":
        stats = obs.stats()
        print(json.dumps(stats, indent=2))

    elif cmd == "search":
        query = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else ""
        results = obs.search(query)
        for title, content, score in results:
            print(f"\n[{score:.2f}] {title}")
            print(content[:200] + "...")

    elif cmd == "daily":
        path = obs.daily_note()
        print(f"Daily note: {path}")

    elif cmd == "project":
        name = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else "New Project"
        path = obs.project_note(name)
        print(f"Project note: {path}")

    elif cmd == "code":
        title = sys.argv[2] if len(sys.argv) > 2 else "snippet"
        path = obs.code_snippet(title, "# Your code here")
        print(f"Code snippet: {path}")

    elif cmd == "linkedin":
        topic = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else "Post"
        path = obs.linkedin_draft(topic)
        print(f"LinkedIn draft: {path}")

    elif cmd == "graph":
        data = obs.graph_data()
        print(f"Nodes: {len(data['nodes'])}")
        print(f"Edges: {len(data['edges'])}")

    elif cmd == "plugins":
        plugins = obs.list_plugins()
        for category, items in plugins.items():
            print(f"\n{category}:")
            for pid, desc in items:
                print(f"  - {pid}: {desc}")


if __name__ == "__main__":
    main()
