"""Global hotkey registration and dispatch for AccessiFight.

Uses keyboard_handler's WXKeyboardHandler for global hotkeys,
which works reliably with wx's event loop and SAPI5 COM.
"""

import threading
import wx
from keyboard_handler.wx_handler import WXKeyboardHandler

from capture import capture_foreground_window
from describe import describe_image
from tts import speaker

# Prompts for each hotkey action
HOTKEY_PROMPTS = {
    "control+shift+win+m": (
        "You are analyzing a fighting game screenshot. "
        "Identify any menu on screen. Report: the menu title, "
        "all visible menu items listed in order, and which item is "
        "currently highlighted or selected. Be concise."
    ),
    "control+shift+win+h": (
        "You are analyzing a fighting game screenshot. "
        "Describe the health bars or life bars visible on screen. "
        "For each bar, state which player it belongs to (e.g. Player 1 left side, "
        "Player 2 right side), its approximate fill percentage, and its screen position. "
        "Be concise."
    ),
    "control+shift+win+s": (
        "You are analyzing a fighting game screenshot. "
        "Describe any super meters, special move meters, EX gauges, or similar "
        "resource bars. For each, state which player it belongs to and its "
        "approximate fill level. Be concise."
    ),
    "control+shift+win+o": (
        "You are analyzing a fighting game screenshot showing an options or settings screen. "
        "List all visible menu items in order. Identify the currently highlighted item. "
        "For any sliders or adjustable values, state the option name and its current value. "
        "Be concise."
    ),
    "control+shift+win+r": (
        "You are analyzing a fighting game screenshot. "
        "Describe the round timer if visible. State the remaining time and its "
        "position on screen. Be concise."
    ),
}


def _handle_describe(key):
    """Capture screen and describe using the appropriate prompt."""
    prompt = HOTKEY_PROMPTS.get(key, "Describe what you see on screen.")
    speaker.say("Scanning...")
    img = capture_foreground_window()
    if img is None:
        speaker.say("Could not capture the active window.")
        return
    result = describe_image(img, prompt)
    speaker.say(result)


class HotkeyFrame(wx.Frame):
    """Hidden frame that owns the global hotkeys."""

    def __init__(self, settings_callback=None):
        super().__init__(None, title="AccessiFight", style=0)
        self._settings_callback = settings_callback
        self.Show(False)
        self.hndlr = WXKeyboardHandler(self)
        self._register()

    def _register(self):
        for key in HOTKEY_PROMPTS:
            self.hndlr.register_key(key, lambda k=key: self._on_describe(k))
        self.hndlr.register_key("control+shift+win+p", self._on_settings)
        self.hndlr.register_key("control+shift+win+q", self._on_quit)

    def _on_describe(self, key):
        threading.Thread(target=_handle_describe, args=(key,), daemon=True).start()

    def _on_settings(self):
        if self._settings_callback:
            self._settings_callback()

    def _on_quit(self):
        speaker.say("AccessiFight shutting down.")
        wx.CallAfter(self.Close)
