# Installation Guide

## Prerequisites

- Python 3.8 or higher
- Windows 10/11 (primary support)
- Microphone (for voice commands)
- Internet connection (for AI features)

## Quick Install

```bash
# Clone the repository
git clone https://github.com/ayushmishra5130tm-blip/Multifly-OTN.git
cd Multifly-OTN

# Install dependencies
pip install -r requirements.txt

# Or install as package
pip install -e .
```

## Configuration

1. Copy `config/default.json` to `config/local.json`
2. Edit `config/local.json` with your settings
3. Set environment variables for API keys:

```bash
# Windows
set OMNIRUTE_API_KEY=your_key_here

# Linux/Mac
export OMNIRUTE_API_KEY=your_key_here
```

## Verify Installation

```bash
# Check status
python cli.py status

# Run tests
python -m pytest tests/
```

## Optional: OmniRoute Setup

For AI code generation features:

1. Install OmniRoute
2. Start OmniRoute server
3. Get API key from OmniRoute dashboard
4. Set environment variable: `OMNIRUTE_API_KEY=your_key`

## Optional: Voice Setup

For voice commands:

1. Install PyAudio: `pip install pyaudio`
2. Ensure microphone is connected
3. Test: `python cli.py voice`

## Troubleshooting

### Issue: Module not found
```bash
# Add src to PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"
```

### Issue: Permission denied
```bash
# Run as administrator (Windows)
# Or use sudo (Linux/Mac)
```

### Issue: Microphone not working
```bash
# Check microphone permissions
# Windows: Settings > Privacy > Microphone
# Linux: Check ALSA/PulseAudio settings
```
