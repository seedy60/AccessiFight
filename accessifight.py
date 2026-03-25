"""AccessiFight - Accessibility companion for fighting games.

Captures the active game window and describes UI elements via TTS
using offline OCR, Google Gemini, or Cloudflare Workers AI.

Hotkeys (global, no admin required):
    Ctrl+Shift+Win+M  -  Describe menus
    Ctrl+Shift+Win+H  -  Describe health/life bars
    Ctrl+Shift+Win+S  -  Describe super/special meters
    Ctrl+Shift+Win+O  -  Describe options/settings screen
    Ctrl+Shift+Win+R  -  Describe round timer
    Ctrl+Shift+Win+P  -  Open settings
    Ctrl+Shift+Win+Q  -  Quit
"""

import sys
import wx

from config import load_config
from gui import show_setup_wizard, show_settings
from hotkeys import HotkeyFrame
from tts import speaker


def main():
    app = wx.App(False)
    cfg = load_config()

    # First-launch setup
    if not cfg.get("setup_complete"):
        if not show_setup_wizard():
            print("Setup cancelled. Exiting.")
            sys.exit(0)
        speaker.reload()

    def open_settings():
        speaker.say("Opening settings.")
        show_settings(frame)
        speaker.reload()
        speaker.say("Settings saved.")

    frame = HotkeyFrame(settings_callback=open_settings)
    speaker.say("AccessiFight is running. Press Control Shift Windows and a letter to scan the game.")
    print("AccessiFight is running.")
    print("Hotkeys:")
    print("  Ctrl+Shift+Win+M  -  Menus")
    print("  Ctrl+Shift+Win+H  -  Health bars")
    print("  Ctrl+Shift+Win+S  -  Super meters")
    print("  Ctrl+Shift+Win+O  -  Options/settings")
    print("  Ctrl+Shift+Win+R  -  Round timer")
    print("  Ctrl+Shift+Win+P  -  Open settings")
    print("  Ctrl+Shift+Win+Q  -  Quit")
    print()

    app.MainLoop()


if __name__ == "__main__":
    main()
