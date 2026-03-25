"""Text-to-speech output for AccessiFight via accessible_output2."""

import accessible_output2.outputs.auto as ao2
import accessible_output2.outputs.sapi5 as sapi5

from config import load_config


def list_sapi5_voices() -> list[str]:
    """Return a list of installed SAPI 5 voice names."""
    try:
        output = sapi5.SAPI5()
        return list(output.list_voices())
    except Exception:
        return []


class Speaker:
    def __init__(self):
        self._screen_reader = ao2.Auto()
        self._sapi = None
        self._mode = "screen_reader"
        self.reload()

    def reload(self):
        """Reload speech settings from config."""
        cfg = load_config()
        self._mode = cfg.get("speech_output", "screen_reader")
        if self._mode == "sapi5":
            voice = cfg.get("sapi5_voice", "")
            try:
                self._sapi = sapi5.SAPI5()
                if voice:
                    self._sapi.set_voice(voice)
            except Exception:
                self._sapi = None

    def say(self, text: str, interrupt: bool = True):
        """Speak text through the configured output."""
        if self._mode == "sapi5" and self._sapi:
            self._sapi.speak(text, interrupt=interrupt)
        else:
            self._screen_reader.speak(text, interrupt=interrupt)

    def say_sync(self, text: str):
        """Alias for say."""
        self.say(text)


# Global speaker instance
speaker = Speaker()
