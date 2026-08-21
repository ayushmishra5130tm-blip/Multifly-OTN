"""
OMNIROUTE SETUP - Get API Key for AI Integration
=================================================
Helps you get an API key from OmniRoute dashboard.

Usage:
  python omniroute_setup.py          Show setup instructions
  python omniroute_setup.py test     Test your API key
"""
import sys
import os
import json
import urllib.request

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "omniroute_config.json")

def show_instructions():
    """Show how to get an API key."""
    print("""
  ====================================================
   OMNIROUTE API KEY SETUP
  ====================================================

  Step 1: Open OmniRoute Dashboard
    http://localhost:20128/dashboard

  Step 2: Login (create account if needed)

  Step 3: Go to Settings -> API Keys

  Step 4: Create a new API key

  Step 5: Copy the key and run:
    python omniroute_setup.py save YOUR_API_KEY_HERE

  ====================================================
    """)

def save_key(api_key):
    """Save the API key to config."""
    config = {"api_key": api_key, "base_url": "http://localhost:20128"}
    with open(CONFIG_PATH, "w") as f:
        json.dump(config, f, indent=2)
    print(f"  [OK] API key saved to {CONFIG_PATH}")

def test_key():
    """Test the API key."""
    if not os.path.exists(CONFIG_PATH):
        print("  [!] No API key saved. Run: python omniroute_setup.py save YOUR_KEY")
        return

    with open(CONFIG_PATH) as f:
        config = json.load(f)

    api_key = config.get("api_key", "")
    base_url = config.get("base_url", "http://localhost:20128")

    payload = json.dumps({
        "model": "openai/gpt-3.5-turbo",
        "messages": [{"role": "user", "content": "Say hello in one word"}],
        "max_tokens": 10
    }).encode("utf-8")

    try:
        req = urllib.request.Request(
            f"{base_url}/api/v1/chat/completions",
            data=payload,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}"
            }
        )
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode())
            if "choices" in data:
                print(f"  [OK] API key works!")
                print(f"  Response: {data['choices'][0]['message']['content']}")
            else:
                print(f"  [!] Unexpected response: {data}")
    except Exception as e:
        print(f"  [!] Error: {e}")

def get_key():
    """Get the saved API key."""
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH) as f:
            config = json.load(f)
        return config.get("api_key", "")
    return ""

if __name__ == "__main__":
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        if cmd == "save" and len(sys.argv) > 2:
            save_key(sys.argv[2])
        elif cmd == "test":
            test_key()
        elif cmd == "get":
            key = get_key()
            print(key if key else "No key saved")
        else:
            show_instructions()
    else:
        show_instructions()
