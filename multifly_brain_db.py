"""
MULTIFLY BRAIN DATABASE
SQLite memory that remembers everything:
- Every command you type
- Every action taken
- Every result and error
- Patterns in your behavior
- What works and what doesn't
"""
import sqlite3
import os
import json
from datetime import datetime, timedelta

DB_PATH = os.path.join(os.path.dirname(__file__), "multifly_brain.db")


class MultiflyBrain:
    """The memory of Multifly - remembers everything, learns from everything."""

    def __init__(self):
        self.conn = sqlite3.connect(DB_PATH)
        self.conn.row_factory = sqlite3.Row
        self._create_tables()

    def _create_tables(self):
        """Create all memory tables."""
        c = self.conn.cursor()

        # Commands history
        c.execute("""CREATE TABLE IF NOT EXISTS commands (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
            command TEXT NOT NULL,
            category TEXT,
            result TEXT,
            success INTEGER DEFAULT 1,
            duration_ms INTEGER DEFAULT 0
        )""")

        # System actions
        c.execute("""CREATE TABLE IF NOT EXISTS actions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
            system TEXT NOT NULL,
            action TEXT NOT NULL,
            target TEXT,
            result TEXT,
            success INTEGER DEFAULT 1
        )""")

        # Learning patterns
        c.execute("""CREATE TABLE IF NOT EXISTS patterns (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pattern_type TEXT NOT NULL,
            pattern_data TEXT NOT NULL,
            confidence REAL DEFAULT 0.5,
            times_seen INTEGER DEFAULT 1,
            last_seen TEXT DEFAULT CURRENT_TIMESTAMP
        )""")

        # System health history
        c.execute("""CREATE TABLE IF NOT EXISTS health (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
            system TEXT NOT NULL,
            status TEXT NOT NULL,
            metrics TEXT
        )""")

        # Error tracking
        c.execute("""CREATE TABLE IF NOT EXISTS errors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
            system TEXT NOT NULL,
            error TEXT NOT NULL,
            resolved INTEGER DEFAULT 0,
            fix_used TEXT
        )""")

        # User preferences (learned)
        c.execute("""CREATE TABLE IF NOT EXISTS preferences (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            key TEXT UNIQUE NOT NULL,
            value TEXT NOT NULL,
            confidence REAL DEFAULT 0.5,
            updated TEXT DEFAULT CURRENT_TIMESTAMP
        )""")

        # Daily stats
        c.execute("""CREATE TABLE IF NOT EXISTS daily_stats (
            date TEXT PRIMARY KEY,
            commands_run INTEGER DEFAULT 0,
            actions_taken INTEGER DEFAULT 0,
            errors_fixed INTEGER DEFAULT 0,
            systems_activated INTEGER DEFAULT 0,
            uptime_minutes INTEGER DEFAULT 0
        )""")

        self.conn.commit()

    # ---- COMMANDS ----
    def log_command(self, command, category="unknown", result="", success=True, duration_ms=0):
        """Remember a command that was executed."""
        c = self.conn.cursor()
        c.execute(
            "INSERT INTO commands (command, category, result, success, duration_ms) VALUES (?, ?, ?, ?, ?)",
            (command, category, result, 1 if success else 0, duration_ms)
        )
        self.conn.commit()
        self._update_daily_stats("commands_run")
        self._learn_pattern("command_frequency", command)

    def get_recent_commands(self, limit=20):
        """Get recent command history."""
        c = self.conn.cursor()
        c.execute("SELECT * FROM commands ORDER BY timestamp DESC LIMIT ?", (limit,))
        return [dict(row) for row in c.fetchall()]

    def get_command_stats(self):
        """Get command usage statistics."""
        c = self.conn.cursor()
        c.execute("SELECT category, COUNT(*) as count FROM commands GROUP BY category ORDER BY count DESC")
        return [dict(row) for row in c.fetchall()]

    # ---- ACTIONS ----
    def log_action(self, system, action, target="", result="", success=True):
        """Remember an action taken by a system."""
        c = self.conn.cursor()
        c.execute(
            "INSERT INTO actions (system, action, target, result, success) VALUES (?, ?, ?, ?, ?)",
            (system, action, target, result, 1 if success else 0)
        )
        self.conn.commit()
        self._update_daily_stats("actions_taken")
        self._learn_pattern("system_usage", system)

    def get_system_actions(self, system, limit=50):
        """Get actions for a specific system."""
        c = self.conn.cursor()
        c.execute(
            "SELECT * FROM actions WHERE system = ? ORDER BY timestamp DESC LIMIT ?",
            (system, limit)
        )
        return [dict(row) for row in c.fetchall()]

    # ---- PATTERNS (Learning) ----
    def _learn_pattern(self, pattern_type, data):
        """Learn a pattern from usage."""
        c = self.conn.cursor()
        c.execute(
            "SELECT id, times_seen, confidence FROM patterns WHERE pattern_type = ? AND pattern_data = ?",
            (pattern_type, data)
        )
        existing = c.fetchone()

        if existing:
            new_count = existing["times_seen"] + 1
            new_confidence = min(0.99, existing["confidence"] + 0.05)
            c.execute(
                "UPDATE patterns SET times_seen = ?, confidence = ?, last_seen = CURRENT_TIMESTAMP WHERE id = ?",
                (new_count, new_confidence, existing["id"])
            )
        else:
            c.execute(
                "INSERT INTO patterns (pattern_type, pattern_data) VALUES (?, ?)",
                (pattern_type, data)
            )
        self.conn.commit()

    def get_patterns(self, pattern_type=None, min_confidence=0.3):
        """Get learned patterns."""
        c = self.conn.cursor()
        if pattern_type:
            c.execute(
                "SELECT * FROM patterns WHERE pattern_type = ? AND confidence >= ? ORDER BY confidence DESC",
                (pattern_type, min_confidence)
            )
        else:
            c.execute(
                "SELECT * FROM patterns WHERE confidence >= ? ORDER BY confidence DESC",
                (min_confidence,)
            )
        return [dict(row) for row in c.fetchall()]

    def suggest_next_command(self, last_command=""):
        """Suggest what you might want to do next based on patterns."""
        patterns = self.get_patterns("command_frequency", 0.4)
        if not patterns:
            return ["graph", "fix", "status", "dashboard"]

        suggestions = []
        for p in patterns[:5]:
            suggestions.append(p["pattern_data"])
        return suggestions

    # ---- HEALTH ----
    def log_health(self, system, status, metrics=""):
        """Log system health status."""
        c = self.conn.cursor()
        c.execute(
            "INSERT INTO health (system, status, metrics) VALUES (?, ?, ?)",
            (system, status, metrics)
        )
        self.conn.commit()

    def get_system_health(self):
        """Get latest health for all systems."""
        c = self.conn.cursor()
        c.execute("""
            SELECT system, status, metrics, MAX(timestamp) as last_check
            FROM health GROUP BY system
        """)
        return [dict(row) for row in c.fetchall()]

    # ---- ERRORS ----
    def log_error(self, system, error, fix_used=""):
        """Track errors and their fixes."""
        c = self.conn.cursor()
        c.execute(
            "INSERT INTO errors (system, error, fix_used) VALUES (?, ?, ?)",
            (system, error, fix_used)
        )
        self.conn.commit()
        self._update_daily_stats("errors_fixed")

    def get_recurring_errors(self):
        """Find errors that happen repeatedly."""
        c = self.conn.cursor()
        c.execute("""
            SELECT error, COUNT(*) as occurrences, MIN(timestamp) as first_seen
            FROM errors WHERE resolved = 0
            GROUP BY error HAVING occurrences > 1
            ORDER BY occurrences DESC
        """)
        return [dict(row) for row in c.fetchall()]

    def resolve_error(self, error_text, fix=""):
        """Mark an error as resolved."""
        c = self.conn.cursor()
        c.execute(
            "UPDATE errors SET resolved = 1, fix_used = ? WHERE error = ? AND resolved = 0",
            (fix, error_text)
        )
        self.conn.commit()

    # ---- PREFERENCES ----
    def set_preference(self, key, value, confidence=0.5):
        """Store a learned preference."""
        c = self.conn.cursor()
        c.execute(
            "INSERT OR REPLACE INTO preferences (key, value, confidence, updated) VALUES (?, ?, ?, CURRENT_TIMESTAMP)",
            (key, value, confidence)
        )
        self.conn.commit()

    def get_preference(self, key):
        """Get a stored preference."""
        c = self.conn.cursor()
        c.execute("SELECT value FROM preferences WHERE key = ?", (key,))
        row = c.fetchone()
        return row["value"] if row else None

    # ---- DAILY STATS ----
    def _update_daily_stats(self, field):
        """Increment a daily stat counter."""
        today = datetime.now().strftime("%Y-%m-%d")
        c = self.conn.cursor()
        c.execute(
            f"INSERT OR IGNORE INTO daily_stats (date) VALUES (?)",
            (today,)
        )
        c.execute(
            f"UPDATE daily_stats SET {field} = {field} + 1 WHERE date = ?",
            (today,)
        )
        self.conn.commit()

    def get_daily_stats(self, days=7):
        """Get stats for last N days."""
        c = self.conn.cursor()
        c.execute(
            "SELECT * FROM daily_stats ORDER BY date DESC LIMIT ?",
            (days,)
        )
        return [dict(row) for row in c.fetchall()]

    # ---- SUMMARY ----
    def get_summary(self):
        """Get a complete summary of all brain data."""
        c = self.conn.cursor()

        summary = {
            "total_commands": c.execute("SELECT COUNT(*) FROM commands").fetchone()[0],
            "total_actions": c.execute("SELECT COUNT(*) FROM actions").fetchone()[0],
            "total_errors": c.execute("SELECT COUNT(*) FROM errors").fetchone()[0],
            "resolved_errors": c.execute("SELECT COUNT(*) FROM errors WHERE resolved=1").fetchone()[0],
            "patterns_learned": c.execute("SELECT COUNT(*) FROM patterns").fetchone()[0],
            "systems_tracked": c.execute("SELECT COUNT(DISTINCT system) FROM health").fetchone()[0],
            "preferences_stored": c.execute("SELECT COUNT(*) FROM preferences").fetchone()[0],
            "today_commands": c.execute(
                "SELECT COALESCE(SUM(commands_run),0) FROM daily_stats WHERE date=date('now')"
            ).fetchone()[0],
            "top_commands": self.get_command_stats()[:5],
            "recent_commands": self.get_recent_commands(5),
            "health": self.get_system_health(),
            "recurring_errors": self.get_recurring_errors(),
            "daily_stats": self.get_daily_stats(7)
        }
        return summary

    def close(self):
        """Close the database connection."""
        self.conn.close()


# Singleton - everyone shares the same brain
_brain = None

def get_brain():
    """Get the shared brain instance."""
    global _brain
    if _brain is None:
        _brain = MultiflyBrain()
    return _brain


if __name__ == "__main__":
    brain = MultiflyBrain()

    # Demo: log some data
    brain.log_command("brain create react app", "project", "Created React app", True, 1200)
    brain.log_command("graph", "visualization", "Graph opened", True, 50)
    brain.log_command("fix", "code_quality", "Fixed 3 issues", True, 3000)
    brain.log_action("OmniRoute", "started", "port 20128", "Online", True)
    brain.log_action("Graphify", "graph_generated", "274 nodes", "Success", True)
    brain.log_health("OmniRoute", "running", '{"port": 20128, "uptime": 3600}')
    brain.log_health("Brain", "active", '{"patterns": 15, "confidence": 0.85}')

    # Print summary
    s = brain.get_summary()
    print("=" * 50)
    print("  MULTIFLY BRAIN STATUS")
    print("=" * 50)
    print(f"  Commands logged:    {s['total_commands']}")
    print(f"  Actions tracked:    {s['total_actions']}")
    print(f"  Patterns learned:   {s['patterns_learned']}")
    print(f"  Errors resolved:    {s['resolved_errors']}/{s['total_errors']}")
    print(f"  Systems monitored:  {s['systems_tracked']}")
    print(f"  Preferences:        {s['preferences_stored']}")
    print()

    if s["top_commands"]:
        print("  Top Command Categories:")
        for c in s["top_commands"]:
            print(f"    {c['category']}: {c['count']}x")

    print()
    suggestions = brain.suggest_next_command()
    print(f"  Suggested next: {', '.join(suggestions)}")

    brain.close()
    print()
    print("Brain memory ready!")
