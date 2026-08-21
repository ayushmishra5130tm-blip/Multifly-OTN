"""
Plugin: hello
Description: [Add description here]
"""
PLUGIN_INFO = {"name": "hello", "version": "1.0", "description": "[Add description]"}

def register(manager):
    """Register this plugin with Multifly."""
    manager.register_system("hello", activate, PLUGIN_INFO["description"])

def activate():
    """Called when this plugin is activated."""
    print(f"  hello plugin activated!")
