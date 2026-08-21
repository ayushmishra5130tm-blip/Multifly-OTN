#!/usr/bin/env python3
"""
Multifly OTN - Command Line Interface
The Most Advanced AI-Powered Developer System
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

def main():
    """Main entry point for Multifly CLI"""
    if len(sys.argv) < 2:
        show_help()
        return
    
    command = sys.argv[1].lower()
    
    commands = {
        "start": cmd_start,
        "dashboard": cmd_dashboard,
        "voice": cmd_voice,
        "api": cmd_api,
        "status": cmd_status,
        "learn": cmd_learn,
        "scan": cmd_scan,
        "fix": cmd_fix,
        "ai": cmd_ai,
        "help": show_help,
    }
    
    if command in commands:
        commands[command]()
    else:
        print(f"Unknown command: {command}")
        show_help()

def show_help():
    """Show help message"""
    print("""
╔══════════════════════════════════════════════════════════════╗
║                  MULTIFLY OTN - CLI                        ║
║            The Most Advanced AI Developer System           ║
╚══════════════════════════════════════════════════════════════╝

Usage: python cli.py <command>

COMMANDS:
  start       Start all Multifly systems
  dashboard   Open live TUI dashboard
  voice       Start voice control (RSS trigger)
  api         Start REST API server
  status      Check system status
  learn       Run self-learning engine
  scan        Scan for security vulnerabilities
  fix         Auto-fix code issues
  ai          AI code generation (requires OmniRoute)
  help        Show this help message

EXAMPLES:
  python cli.py start              # Start everything
  python cli.py dashboard          # Open live dashboard
  python cli.py voice              # Start voice control
  python cli.py ai "create app"    # AI code generation
  python cli.py scan               # Security scan

For more info, visit: https://github.com/ayushmishra5130tm-blip/Multifly-OTN
""")

def cmd_start():
    """Start all systems"""
    from src.core.multifly_launcher import main as launcher
    launcher()

def cmd_dashboard():
    """Open dashboard"""
    from src.dashboard.animated_dashboard import main as dashboard
    dashboard()

def cmd_voice():
    """Start voice control"""
    from src.voice.multifly_voice import main as voice
    voice()

def cmd_api():
    """Start REST API"""
    from src.core.unified_multifly import main as api
    api()

def cmd_status():
    """Check status"""
    from src.core.multifly_universal import main as universal
    sys.argv = [sys.argv[0], "--status"]
    universal()

def cmd_learn():
    """Run self-learning"""
    from src.security.self_improve import main as learn
    learn()

def cmd_scan():
    """Security scan"""
    from src.security.multifly_powers import main as powers
    sys.argv = [sys.argv[0], "scan"]
    powers()

def cmd_fix():
    """Auto-fix"""
    from src.security.multifly_powers import main as powers
    sys.argv = [sys.argv[0], "fix"]
    powers()

def cmd_ai():
    """AI code generation"""
    if len(sys.argv) < 3:
        print("Usage: python cli.py ai <prompt>")
        print("Example: python cli.py ai 'create a login page'")
        return
    
    prompt = " ".join(sys.argv[2:])
    from src.ai.multifly_100 import AIEngine
    ai = AIEngine()
    print(f"Generating: {prompt}")
    result = ai.generate(prompt)
    print(result)

if __name__ == "__main__":
    main()
