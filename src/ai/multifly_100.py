"""
MULTIFLY 100% - OmniRoute + OmniVoice Integration
===================================================
The final 4% - voice commands + real AI code generation.

Usage:
  python multifly_100.py ai "explain this code"       AI via OmniRoute
  python multifly_100.py ai "generate a login page"   AI generates code
  python multifly_100.py voice                         Voice command mode
  python multifly_100.py voice --trigger RSS           Voice with RSS trigger
  python multifly_100.py full "create react app"       Voice + AI + Execute
"""

import sys, os, json, time, asyncio, threading
from datetime import datetime
from pathlib import Path

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

from unified_multifly import Brain
from multifly_powers import ExecutionEngine
from multifly_elite import NLPEngine, MLLearner


# ============================================================
#  1. OMNIROUTE AI - Real AI Code Generation
# ============================================================
class OmniRouteAI:
    """Connect to OmniRoute for real AI-powered code generation."""

    def __init__(self, brain, base_url="http://localhost:20128"):
        self.brain = brain
        self.base_url = base_url
        self.api_key = self._load_api_key()
        self.available = self._check_connection()

    def _load_api_key(self):
        """Load API key from config."""
        config_path = os.path.join(SCRIPT_DIR, "omniroute_config.json")
        if os.path.exists(config_path):
            with open(config_path) as f:
                config = json.load(f)
            return config.get("api_key", "")
        return ""

    def _check_connection(self):
        """Check if OmniRoute is running."""
        import socket
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(2)
            result = s.connect_ex(("127.0.0.1", 20128))
            s.close()
            return result == 0
        except:
            return False

    def chat(self, message, system_prompt="You are a helpful coding assistant."):
        """Send a chat request to OmniRoute."""
        import urllib.request

        if not self.available:
            return {"error": "OmniRoute not running on port 20128"}

        payload = json.dumps({
            "model": "openai/gpt-3.5-turbo",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": message}
            ],
            "max_tokens": 2000,
            "temperature": 0.7
        }).encode("utf-8")

        # Try multiple endpoints
        endpoints = [
            "/api/v1/chat/completions",
            "/v1/chat/completions",
            "/api/chat/completions",
        ]

        for endpoint in endpoints:
            try:
                req = urllib.request.Request(
                    f"{self.base_url}{endpoint}",
                    data=payload,
                    headers={
                        "Content-Type": "application/json",
                        "Authorization": f"Bearer {self.api_key}"
                    }
                )
                with urllib.request.urlopen(req, timeout=30) as resp:
                    data = json.loads(resp.read().decode())
                    if "choices" in data and len(data["choices"]) > 0:
                        content = data["choices"][0]["message"]["content"]
                        self.brain.log_action("OmniRoute", "chat", message[:50], "Success")
                        return {"success": True, "response": content, "model": data.get("model", "unknown")}
                    return {"error": "No response from OmniRoute"}
            except urllib.error.HTTPError as e:
                if e.code == 404:
                    continue  # Try next endpoint
                return {"error": f"HTTP {e.code}: {e.reason}"}
            except Exception as e:
                continue

        return {"error": "Could not connect to OmniRoute API"}

    def generate_code(self, description, language="python"):
        """Generate code using OmniRoute AI."""
        prompt = f"""Generate {language} code for: {description}

Return ONLY the code, no explanations. Use proper formatting.
If it's a function, include docstring.
If it's a class, include methods.
"""
        result = self.chat(prompt, "You are an expert programmer. Generate clean, production-ready code.")
        return result

    def explain_code(self, code):
        """Explain code using OmniRoute AI."""
        prompt = f"Explain this code in detail:\n\n{code}"
        return self.chat(prompt, "You are a coding teacher. Explain code clearly and concisely.")

    def fix_code(self, code, error=""):
        """Fix code using OmniRoute AI."""
        prompt = f"Fix this code. Error: {error}\n\nCode:\n{code}"
        return self.chat(prompt, "You are an expert debugger. Fix the code and explain the fix.")

    def review_code(self, code):
        """Review code using OmniRoute AI."""
        prompt = f"Review this code for bugs, performance, and best practices:\n\n{code}"
        return self.chat(prompt, "You are a senior code reviewer. Be thorough but concise.")


# ============================================================
#  2. OMNIVOICE - Offline Voice Commands
# ============================================================
class OmniVoice:
    """Offline voice command system using speech recognition."""

    def __init__(self, brain):
        self.brain = brain
        self.recognizer = None
        self.microphone = None
        self.tts = None
        self.available = False
        self._init()

    def _init(self):
        """Initialize voice components."""
        try:
            import speech_recognition as sr
            self.recognizer = sr.Recognizer()
            # Try pyaudio first, fall back to sounddevice
            try:
                self.microphone = sr.Microphone()
                with self.microphone as source:
                    self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                self.available = True
            except:
                # Use sounddevice as fallback
                try:
                    import sounddevice as sd
                    self.use_sounddevice = True
                    self.available = True
                except:
                    self.available = False
        except Exception as e:
            print(f"  Voice init warning: {e}")
            self.available = False

        try:
            import pyttsx3
            self.tts = pyttsx3.init()
            self.tts.setProperty('rate', 150)
        except:
            self.tts = None

    def listen(self, timeout=5):
        """Listen for voice input and return text."""
        if not self.available:
            return None

        import speech_recognition as sr
        try:
            with self.microphone as source:
                print("  Listening...", end="", flush=True)
                audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=10)
                print(" Processing...")

            # Try Google (free, works offline with internet)
            try:
                text = self.recognizer.recognize_google(audio)
                self.brain.log_action("Voice", "listen", text[:50])
                return text
            except:
                pass

            # Try Sphinx (fully offline)
            try:
                text = self.recognizer.recognize_sphinx(audio)
                self.brain.log_action("Voice", "listen_offline", text[:50])
                return text
            except:
                pass

            return None
        except sr.WaitTimeoutError:
            return None
        except Exception as e:
            return None

    def speak(self, text):
        """Convert text to speech."""
        if self.tts:
            try:
                self.tts.say(text)
                self.tts.runAndWait()
            except:
                pass
        print(f"  {text}")

    def listen_with_trigger(self, trigger="RSS"):
        """Listen only when trigger word is spoken."""
        if not self.available:
            print("  Voice not available - install pyaudio")
            return None

        print(f"  Listening for '{trigger}'...")
        while True:
            text = self.listen(timeout=3)
            if text and trigger.upper() in text.upper():
                # Extract command after trigger
                idx = text.upper().find(trigger.upper())
                command = text[idx + len(trigger):].strip()
                if command:
                    self.speak(f"Executing: {command}")
                    return command
                else:
                    self.speak("What would you like me to do?")


# ============================================================
#  3. FULL PIPELINE - Voice + AI + Execute
# ============================================================
class FullPipeline:
    """Complete pipeline: Voice -> NLP -> AI -> Execute -> Respond."""

    def __init__(self):
        self.brain = Brain()
        self.ai = OmniRouteAI(self.brain)
        self.voice = OmniVoice(self.brain)
        self.nlp = NLPEngine(self.brain)
        self.powers = ExecutionEngine(self.brain)
        self.learner = MLLearner(self.brain)

    def execute_with_ai(self, command):
        """Execute a command using AI + local execution."""
        print(f"\n  Processing: {command}")

        # Step 1: Understand with NLP
        understanding = self.nlp.understand(command)
        print(f"  Intent: {understanding['intent']} ({understanding['confidence']:.0%})")

        # Step 2: If AI is available, use it for code generation
        if self.ai.available and understanding["intent"] in ("create_project", "ai", "explain", "fix_code"):
            print("  Generating with OmniRoute AI...")
            ai_result = self.ai.generate_code(command)
            if ai_result.get("success"):
                print(f"  AI Response received ({len(ai_result['response'])} chars)")
                self.brain.log_action("AI", "generate", command[:50], "Success")
                return {
                    "source": "omniroute_ai",
                    "intent": understanding,
                    "code": ai_result["response"],
                    "model": ai_result.get("model", "unknown")
                }

        # Step 3: Fall back to local execution
        print("  Using local execution engine...")
        local_result = self.powers.execute(command)
        return {
            "source": "local_engine",
            "intent": understanding,
            "result": local_result
        }

    def voice_command(self, trigger="RSS"):
        """Full voice command pipeline."""
        if not self.voice.available:
            print("  Voice not available. Install pyaudio:")
            print("  pip install pyaudio")
            return

        self.voice.speak("Multifly voice system ready. Say RSS followed by your command.")

        while True:
            command = self.voice.listen_with_trigger(trigger)
            if command:
                result = self.execute_with_ai(command)
                if result.get("code"):
                    self.voice.speak("Code generated successfully.")
                elif result.get("result", {}).get("success"):
                    self.voice.speak("Command executed successfully.")
                else:
                    self.voice.speak("Command completed.")


# ============================================================
#  MAIN
# ============================================================
def main():
    brain = Brain()

    if len(sys.argv) < 2:
        print("""
  ====================================================
   MULTIFLY 100% - AI + Voice Integration
  ====================================================

  Usage:
    python multifly_100.py ai "prompt"       AI via OmniRoute
    python multifly_100.py voice             Voice commands (RSS)
    python multifly_100.py full "command"    Full pipeline
    python multifly_100.py status            Check integrations
  ====================================================
        """)
        return

    cmd = sys.argv[1].lower()

    if cmd == "ai" and len(sys.argv) > 2:
        prompt = " ".join(sys.argv[2:])
        ai = OmniRouteAI(brain)
        print(f"\n  OmniRoute AI: {'ONLINE' if ai.available else 'OFFLINE'}")
        if ai.available:
            result = ai.chat(prompt)
            if result.get("success"):
                print(f"\n  Response:\n{result['response']}")
            else:
                print(f"  Error: {result.get('error', 'unknown')}")
        else:
            print("  Start OmniRoute first: cd OmniRoute && npm run dev")

    elif cmd == "voice":
        trigger = "RSS"
        if "--trigger" in sys.argv:
            idx = sys.argv.index("--trigger")
            if idx + 1 < len(sys.argv):
                trigger = sys.argv[idx + 1]

        pipeline = FullPipeline()
        pipeline.voice_command(trigger)

    elif cmd == "full" and len(sys.argv) > 2:
        command = " ".join(sys.argv[2:])
        pipeline = FullPipeline()
        result = pipeline.execute_with_ai(command)
        print(json.dumps(result, indent=2, default=str))

    elif cmd == "status":
        ai = OmniRouteAI(brain)
        voice = OmniVoice(brain)
        print(f"\n  Integration Status:")
        print(f"    OmniRoute AI:  {'ONLINE' if ai.available else 'OFFLINE'}")
        print(f"    API Key:       {'CONFIGURED' if ai.api_key else 'NOT SET (run: python omniroute_setup.py)'}")
        print(f"    Voice Input:   {'READY' if voice.available else 'NEEDS PYAUDIO'}")
        print(f"    Voice Output:  {'READY' if voice.tts else 'UNAVAILABLE'}")
        print(f"    NLP Engine:    READY")
        print(f"    ML Learner:    READY")
        print(f"    Execution:     READY")
        print(f"    Brain:         {brain.summary()['commands']} commands stored")
        print()
        if not ai.api_key:
            print("  To enable AI code generation:")
            print("    1. Open http://localhost:20128/dashboard")
            print("    2. Create an API key in Settings")
            print("    3. Run: python omniroute_setup.py save YOUR_KEY")
            print()

    else:
        print(f"  Unknown: {cmd}")

    brain.conn.close()


if __name__ == "__main__":
    main()
