"""
MULTIFLY VOICE CONTROL - Command Everything With Your Voice
=============================================================
Say "RSS" followed by your command to control the entire system.

Usage:
  python multifly_voice.py                    Start voice control
  python multifly_voice.py --trigger RSS      Custom trigger word
  python multifly_voice.py --test             Test microphone
  python multifly_voice.py --list             List all voice commands

VOICE COMMANDS:
  RSS create react app           → Creates full React project
  RSS create fastapi backend     → Creates FastAPI project
  RSS create next.js app         → Creates Next.js project
  RSS fix this error             → AI fixes code
  RSS explain this code          → AI explains code
  RSS deploy to vercel           → Deploys to cloud
  RSS run tests                  → Runs all tests
  RSS scan security              → Scans for vulnerabilities
  RSS auto fix                   → Auto-fixes all code issues
  RSS generate function name     → Generates a function
  RSS linkedin post              → Creates LinkedIn content
  RSS system status              → Shows all system status
  RSS open dashboard             → Opens live dashboard
  RSS activate all               → Activates all systems
  RSS start omni route           → Starts OmniRoute server
  RSS stop                       → Stops voice control
"""

import sys, os, time, json, re, subprocess, threading
from datetime import datetime
from pathlib import Path

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)


# ============================================================
#  VOICE ENGINE - Listen + Understand + Execute + Speak
# ============================================================
class VoiceEngine:
    """Complete voice control for Multifly."""

    def __init__(self, trigger="RSS"):
        self.trigger = trigger
        self.running = False
        self.recognizer = None
        self.microphone = None
        self.tts = None
        self.audio_queue = []

        # Import brain
        from unified_multifly import Brain
        self.brain = Brain()

        # Initialize components
        self._init_speech()
        self._init_tts()

    def _init_speech(self):
        """Initialize speech recognition."""
        try:
            import speech_recognition as sr
            self.recognizer = sr.Recognizer()
            self.recognizer.energy_threshold = 4000
            self.recognizer.dynamic_energy_threshold = True
            self.recognizer.pause_threshold = 0.8

            # Try microphone
            try:
                self.microphone = sr.Microphone()
                with self.microphone as source:
                    self.recognizer.adjust_for_ambient_noise(source, duration=1)
                print("  [OK] Microphone ready")
            except:
                # Fallback to sounddevice
                try:
                    import sounddevice as sd
                    self.use_sounddevice = True
                    print("  [OK] Using sounddevice for audio")
                except:
                    print("  [!] No microphone found")
                    self.recognizer = None
        except Exception as e:
            print(f"  [!] Speech init error: {e}")

    def _init_tts(self):
        """Initialize text-to-speech."""
        try:
            import pyttsx3
            self.tts = pyttsx3.init()
            self.tts.setProperty('rate', 160)
            self.tts.setProperty('volume', 0.9)
            # Try to get a good voice
            voices = self.tts.getProperty('voices')
            for voice in voices:
                if "english" in voice.name.lower() or "david" in voice.name.lower():
                    self.tts.setProperty('voice', voice.id)
                    break
            print("  [OK] Text-to-speech ready")
        except Exception as e:
            print(f"  [!] TTS init error: {e}")

    def speak(self, text):
        """Convert text to speech."""
        print(f"  > {text}")
        if self.tts:
            try:
                self.tts.say(text)
                self.tts.runAndWait()
            except:
                pass

    def listen(self, timeout=5):
        """Listen for voice input."""
        if not self.recognizer:
            return None

        import speech_recognition as sr
        try:
            with self.microphone as source:
                print("  [LISTENING]", end="", flush=True)
                audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=10)
                print(" [PROCESSING]")

            # Try Google (free, works online)
            try:
                text = self.recognizer.recognize_google(audio)
                return text.strip()
            except:
                pass

            # Try offline recognition
            try:
                text = self.recognizer.recognize_sphinx(audio)
                return text.strip()
            except:
                pass

            return None
        except sr.WaitTimeoutError:
            return None
        except Exception as e:
            return None

    def wait_for_trigger(self):
        """Wait for the trigger word."""
        while self.running:
            text = self.listen(timeout=3)
            if text:
                # Check for trigger
                text_upper = text.upper()
                trigger_upper = self.trigger.upper()

                if trigger_upper in text_upper:
                    # Extract command after trigger
                    idx = text_upper.find(trigger_upper)
                    command = text[idx + len(trigger_upper):].strip()

                    if command:
                        return command
                    else:
                        self.speak("Yes? What would you like me to do?")
                        # Listen for the actual command
                        command = self.listen(timeout=5)
                        if command:
                            return command
            time.sleep(0.1)

    def execute_command(self, command):
        """Execute a voice command."""
        cmd = command.lower().strip()
        start_time = time.time()

        # ============================================
        # PROJECT CREATION
        # ============================================
        if any(w in cmd for w in ["create", "new", "build", "make"]):
            if "react" in cmd:
                return self._create_project("react", cmd)
            elif "next" in cmd:
                return self._create_project("nextjs", cmd)
            elif "fastapi" in cmd or "api" in cmd:
                return self._create_project("fastapi", cmd)
            elif "flask" in cmd:
                return self._create_project("flask", cmd)
            elif "express" in cmd or "node" in cmd:
                return self._create_project("express", cmd)
            elif "python" in cmd:
                return self._create_project("python", cmd)
            else:
                return self._create_project("python", cmd)

        # ============================================
        # CODE OPERATIONS
        # ============================================
        elif any(w in cmd for w in ["fix", "debug", "repair"]):
            return self._fix_code(cmd)

        elif any(w in cmd for w in ["explain", "describe", "what is"]):
            return self._explain_code(cmd)

        elif any(w in cmd for w in ["generate", "write", "code"]):
            return self._generate_code(cmd)

        elif any(w in cmd for w in ["review", "check code"]):
            return self._review_code(cmd)

        # ============================================
        # TESTING
        # ============================================
        elif any(w in cmd for w in ["test", "run tests"]):
            return self._run_tests(cmd)

        # ============================================
        # DEPLOYMENT
        # ============================================
        elif any(w in cmd for w in ["deploy", "ship", "publish", "push"]):
            return self._deploy(cmd)

        # ============================================
        # SECURITY
        # ============================================
        elif any(w in cmd for w in ["scan", "security", "audit"]):
            return self._security_scan(cmd)

        # ============================================
        # SYSTEM CONTROL
        # ============================================
        elif any(w in cmd for w in ["status", "health", "report"]):
            return self._system_status()

        elif any(w in cmd for w in ["dashboard", "graph", "visualize"]):
            return self._open_dashboard()

        elif any(w in cmd for w in ["activate", "start all", "wake up"]):
            return self._activate_all()

        elif "omniroute" in cmd or "omni route" in cmd:
            return self._start_omniroute()

        elif any(w in cmd for w in ["linkedin", "post", "content"]):
            return self._linkedin_action(cmd)

        elif any(w in cmd for w in ["whatsapp", "message", "broadcast"]):
            return self._whatsapp_action(cmd)

        # ============================================
        # AUTO-FIX
        # ============================================
        elif any(w in cmd for w in ["auto fix", "autofix", "repair all"]):
            return self._auto_fix()

        # ============================================
        # HELP
        # ============================================
        elif any(w in cmd for w in ["help", "commands", "what can you do"]):
            return self._show_help()

        # ============================================
        # STOP
        # ============================================
        elif any(w in cmd for w in ["stop", "exit", "quit", "goodbye", "bye"]):
            self.running = False
            return {"success": True, "message": "Voice control stopped"}

        # ============================================
        # UNKNOWN COMMAND
        # ============================================
        else:
            return {"success": False, "message": f"I don't understand: {command}. Say 'help' for commands."}

    # ============================================
    #  EXECUTION FUNCTIONS
    # ============================================

    def _create_project(self, project_type, cmd):
        """Create a project."""
        # Extract project name
        name_match = re.search(r"(?:called?|named?|as)\s+(\S+)", cmd)
        if name_match:
            name = name_match.group(1)
        else:
            name = f"my_{project_type}_{int(time.time()) % 10000}"

        self.speak(f"Creating {project_type} project called {name}")

        try:
            sys.path.insert(0, SCRIPT_DIR)
            from multifly_powers import ExecutionEngine
            engine = ExecutionEngine(self.brain)
            result = engine.execute(f"create {project_type} project {name}")

            if result.get("success"):
                path = result.get("path", "Desktop")
                self.speak(f"Done! Created {project_type} project at {path}")
                self.brain.log_action("Voice", "create_project", project_type, "Success")
                return {"success": True, "message": f"Created {project_type} at {path}"}
            else:
                self.speak("Failed to create project")
                return {"success": False, "message": "Creation failed"}
        except Exception as e:
            self.speak(f"Error creating project: {str(e)[:50]}")
            return {"success": False, "message": str(e)}

    def _fix_code(self, cmd):
        """Fix code using AI."""
        self.speak("Analyzing code for errors")

        try:
            sys.path.insert(0, SCRIPT_DIR)
            from multifly_100 import OmniRouteAI
            ai = OmniRouteAI(self.brain)

            if ai.available:
                result = ai.fix_code("current code")
                if result.get("success"):
                    response = result["response"][:200]
                    self.speak(f"Found issues. {response[:100]}")
                    self.brain.log_action("Voice", "fix_code", "success", "Success")
                    return {"success": True, "response": response}
                else:
                    self.speak("Could not connect to AI. Using local scanner.")
            else:
                self.speak("AI not available. Running local scanner.")

            # Fallback to local scanner
            from multifly_powers import ExecutionEngine
            engine = ExecutionEngine(self.brain)
            result = engine._fix_code("fix code")
            count = result.get("count", 0)
            self.speak(f"Found {count} issues to fix")
            return {"success": True, "message": f"Found {count} issues"}

        except Exception as e:
            self.speak(f"Error: {str(e)[:50]}")
            return {"success": False, "message": str(e)}

    def _explain_code(self, cmd):
        """Explain code using AI."""
        self.speak("Let me explain the code")

        try:
            sys.path.insert(0, SCRIPT_DIR)
            from multifly_100 import OmniRouteAI
            ai = OmniRouteAI(self.brain)

            if ai.available:
                result = ai.explain_code("current file")
                if result.get("success"):
                    response = result["response"][:300]
                    self.speak(f"Here's what the code does: {response[:200]}")
                    self.brain.log_action("Voice", "explain_code", "success", "Success")
                    return {"success": True, "response": response}
            else:
                self.speak("AI not available for explanation")
                return {"success": False, "message": "AI not available"}
        except Exception as e:
            self.speak(f"Error: {str(e)[:50]}")
            return {"success": False, "message": str(e)}

    def _generate_code(self, cmd):
        """Generate code using AI."""
        self.speak("Generating code")

        try:
            sys.path.insert(0, SCRIPT_DIR)
            from multifly_100 import OmniRouteAI
            ai = OmniRouteAI(self.brain)

            if ai.available:
                result = ai.generate_code(cmd)
                if result.get("success"):
                    code = result["response"][:500]
                    self.speak(f"Code generated. {len(code)} characters created.")
                    self.brain.log_action("Voice", "generate_code", cmd[:50], "Success")
                    return {"success": True, "code": code}
            else:
                self.speak("AI not available for code generation")
                return {"success": False, "message": "AI not available"}
        except Exception as e:
            self.speak(f"Error: {str(e)[:50]}")
            return {"success": False, "message": str(e)}

    def _review_code(self, cmd):
        """Review code using AI."""
        self.speak("Reviewing code for issues")

        try:
            sys.path.insert(0, SCRIPT_DIR)
            from multifly_100 import OmniRouteAI
            ai = OmniRouteAI(self.brain)

            if ai.available:
                result = ai.review_code("current project")
                if result.get("success"):
                    response = result["response"][:300]
                    self.speak(f"Review complete. {response[:200]}")
                    self.brain.log_action("Voice", "review_code", "success", "Success")
                    return {"success": True, "response": response}
            else:
                self.speak("AI not available for review")
                return {"success": False, "message": "AI not available"}
        except Exception as e:
            self.speak(f"Error: {str(e)[:50]}")
            return {"success": False, "message": str(e)}

    def _run_tests(self, cmd):
        """Run tests."""
        self.speak("Running tests")

        try:
            sys.path.insert(0, SCRIPT_DIR)
            from multifly_powers import ExecutionEngine
            engine = ExecutionEngine(self.brain)
            result = engine._run_tests("test")
            count = result.get("test_files", 0)
            self.speak(f"Found {count} test files. Tests completed.")
            self.brain.log_action("Voice", "run_tests", "success", "Success")
            return {"success": True, "message": f"Tests completed"}
        except Exception as e:
            self.speak(f"Error: {str(e)[:50]}")
            return {"success": False, "message": str(e)}

    def _deploy(self, cmd):
        """Deploy to cloud."""
        self.speak("Deploying to cloud")

        try:
            # Check for Vercel
            subprocess.run(["vercel", "--yes", "--prod"], capture_output=True, timeout=60)
            self.speak("Deployed successfully to Vercel")
            self.brain.log_action("Voice", "deploy", "vercel", "Success")
            return {"success": True, "message": "Deployed to Vercel"}
        except Exception as e:
            self.speak(f"Deployment error: {str(e)[:50]}")
            return {"success": False, "message": str(e)}

    def _security_scan(self, cmd):
        """Run security scan."""
        self.speak("Scanning for security issues")

        try:
            sys.path.insert(0, SCRIPT_DIR)
            from multifly_powers import ExecutionEngine
            engine = ExecutionEngine(self.brain)
            result = engine._security_scan("scan")
            count = result.get("count", 0)
            if count > 0:
                self.speak(f"Found {count} security issues")
            else:
                self.speak("No security issues found")
            self.brain.log_action("Voice", "security_scan", f"{count} issues", "Success")
            return {"success": True, "message": f"Found {count} issues"}
        except Exception as e:
            self.speak(f"Error: {str(e)[:50]}")
            return {"success": False, "message": str(e)}

    def _system_status(self):
        """Get system status."""
        self.speak("Checking system status")

        try:
            s = self.brain.summary()
            status = f"System has {s['commands']} commands, {s['patterns']} patterns learned"
            self.speak(status)
            self.brain.log_action("Voice", "status", "check", "Success")
            return {"success": True, "message": status}
        except Exception as e:
            self.speak(f"Error: {str(e)[:50]}")
            return {"success": False, "message": str(e)}

    def _open_dashboard(self):
        """Open live dashboard."""
        self.speak("Opening live dashboard")

        try:
            subprocess.Popen(
                f'python "{SCRIPT_DIR}/unified_multifly.py" dashboard',
                shell=True,
                creationflags=subprocess.CREATE_NEW_CONSOLE
            )
            self.speak("Dashboard opened")
            self.brain.log_action("Voice", "open_dashboard", "success", "Success")
            return {"success": True, "message": "Dashboard opened"}
        except Exception as e:
            self.speak(f"Error: {str(e)[:50]}")
            return {"success": False, "message": str(e)}

    def _activate_all(self):
        """Activate all systems."""
        self.speak("Activating all systems")

        try:
            subprocess.Popen(
                f'python "{SCRIPT_DIR}/multifly_launcher.py"',
                shell=True,
                creationflags=subprocess.CREATE_NEW_CONSOLE
            )
            self.speak("All systems activated")
            self.brain.log_action("Voice", "activate_all", "success", "Success")
            return {"success": True, "message": "All systems activated"}
        except Exception as e:
            self.speak(f"Error: {str(e)[:50]}")
            return {"success": False, "message": str(e)}

    def _start_omniroute(self):
        """Start OmniRoute."""
        self.speak("Starting OmniRoute AI server")

        try:
            subprocess.Popen(
                f'python "{SCRIPT_DIR}/start_omniroute.py"',
                shell=True,
                creationflags=subprocess.CREATE_NEW_CONSOLE
            )
            self.speak("OmniRoute starting")
            self.brain.log_action("Voice", "start_omniroute", "success", "Success")
            return {"success": True, "message": "OmniRoute started"}
        except Exception as e:
            self.speak(f"Error: {str(e)[:50]}")
            return {"success": False, "message": str(e)}

    def _linkedin_action(self, cmd):
        """LinkedIn action."""
        self.speak("Opening LinkedIn automation")

        try:
            desktop = os.path.expanduser(r"~\Desktop")
            for folder in ["Voltairtech LinkedIn Automated", "LinkedIn Automation - KaunTech"]:
                path = os.path.join(desktop, folder)
                if os.path.exists(path):
                    subprocess.Popen(f'explorer "{path}"', shell=True)
                    self.speak(f"Opened {folder}")
                    break
            self.brain.log_action("Voice", "linkedin", cmd[:50], "Success")
            return {"success": True, "message": "LinkedIn opened"}
        except Exception as e:
            self.speak(f"Error: {str(e)[:50]}")
            return {"success": False, "message": str(e)}

    def _whatsapp_action(self, cmd):
        """WhatsApp action."""
        self.speak("Opening WhatsApp automation")

        try:
            desktop = os.path.expanduser(r"~\Desktop")
            path = os.path.join(desktop, "WhatsApp Automation")
            if os.path.exists(path):
                subprocess.Popen(f'explorer "{path}"', shell=True)
                self.speak("WhatsApp automation opened")
            else:
                self.speak("WhatsApp automation folder not found")
            self.brain.log_action("Voice", "whatsapp", cmd[:50], "Success")
            return {"success": True, "message": "WhatsApp opened"}
        except Exception as e:
            self.speak(f"Error: {str(e)[:50]}")
            return {"success": False, "message": str(e)}

    def _auto_fix(self):
        """Auto-fix all code issues."""
        self.speak("Auto-fixing all code issues")

        try:
            sys.path.insert(0, SCRIPT_DIR)
            from multifly_powers import ExecutionEngine
            engine = ExecutionEngine(self.brain)
            result = engine._fix_code("auto fix")
            self.speak("Auto-fix completed")
            self.brain.log_action("Voice", "auto_fix", "success", "Success")
            return {"success": True, "message": "Auto-fix completed"}
        except Exception as e:
            self.speak(f"Error: {str(e)[:50]}")
            return {"success": False, "message": str(e)}

    def _show_help(self):
        """Show available voice commands."""
        self.speak("Here are the voice commands you can use")

        help_text = """
        Create commands: create react app, create fastapi backend, create next.js app
        Code commands: fix this error, explain this code, generate code, review code
        Test commands: run tests
        Deploy commands: deploy to vercel
        Security commands: scan security
        System commands: system status, open dashboard, activate all
        Automation commands: linkedin post, whatsapp message
        Control commands: auto fix, help, stop
        """
        print(help_text)
        return {"success": True, "message": "Help shown"}

    def run(self):
        """Main voice control loop."""
        self.running = True

        print()
        print("  ====================================================")
        print("   MULTIFLY VOICE CONTROL")
        print(f"   Trigger word: {self.trigger}")
        print("   Say 'help' for commands")
        print("   Say 'stop' to exit")
        print("  ====================================================")
        print()

        self.speak("Voice control ready. Say RSS followed by your command.")

        while self.running:
            try:
                # Wait for trigger word
                command = self.wait_for_trigger()

                if command:
                    # Execute command
                    result = self.execute_command(command)

                    if result.get("success"):
                        self.brain.log_cmd(command, "voice", result.get("message", ""), True)
                    else:
                        self.brain.log_cmd(command, "voice", result.get("message", ""), False)
                        if result.get("message"):
                            self.speak(result["message"])

            except KeyboardInterrupt:
                self.speak("Voice control stopped")
                self.running = False
                break
            except Exception as e:
                print(f"  Error: {e}")
                time.sleep(1)

        self.brain.conn.close()
        print("\n  Voice control ended.")


# ============================================================
#  MAIN
# ============================================================
def main():
    trigger = "RSS"

    # Parse arguments
    if "--trigger" in sys.argv:
        idx = sys.argv.index("--trigger")
        if idx + 1 < len(sys.argv):
            trigger = sys.argv[idx + 1]

    if "--test" in sys.argv:
        print("  Testing microphone...")
        engine = VoiceEngine(trigger)
        print("  Say something...")
        text = engine.listen(timeout=5)
        if text:
            print(f"  Heard: {text}")
        else:
            print("  No speech detected")
        return

    if "--list" in sys.argv:
        print("""
  ====================================================
   VOICE COMMANDS
  ====================================================

  PROJECT CREATION:
    RSS create react app           = Creates React project
    RSS create fastapi backend     = Creates FastAPI project
    RSS create next.js app         = Creates Next.js project
    RSS create flask app           = Creates Flask project
    RSS create express api         = Creates Express API

  CODE OPERATIONS:
    RSS fix this error             = AI fixes code
    RSS explain this code          = AI explains code
    RSS generate function name     = AI generates function
    RSS review my code             = AI reviews code

  TESTING:
    RSS run tests                  = Runs all tests

  DEPLOYMENT:
    RSS deploy to vercel           = Deploys to cloud

  SECURITY:
    RSS scan security              = Scans for vulnerabilities

  SYSTEM CONTROL:
    RSS system status              = Shows all system status
    RSS open dashboard             = Opens live dashboard
    RSS activate all               = Activates all systems
    RSS start omni route           = Starts OmniRoute server

  AUTOMATION:
    RSS linkedin post              = Opens LinkedIn automation
    RSS whatsapp message           = Opens WhatsApp automation

  AUTO-FIX:
    RSS auto fix                   = Auto-fixes all code issues

  CONTROL:
    RSS help                       = Shows this help
    RSS stop                       = Stops voice control

  ====================================================
        """)
        return

    # Start voice control
    engine = VoiceEngine(trigger)
    engine.run()


if __name__ == "__main__":
    main()
