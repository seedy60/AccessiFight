"""Configuration management for AccessiFight."""

import json
import os

CONFIG_DIR = os.path.join(os.environ.get("APPDATA", os.path.expanduser("~")), "AccessiFight")
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")

DEFAULTS = {
    "method": "",  # "ocr", "gemini", or "cloudflare"
    "speech_output": "screen_reader",  # "screen_reader" or "sapi5"
    "sapi5_voice": "",
    "gemini_api_key": "",
    "gemini_model": "gemini-2.0-flash",
    "cloudflare_account_id": "",
    "cloudflare_api_token": "",
    "cloudflare_model": "@cf/meta/llama-4-scout-17b-16e-instruct",
    "tesseract_path": "",
    "setup_complete": False,
}


def ensure_config_dir():
    os.makedirs(CONFIG_DIR, exist_ok=True)


def load_config() -> dict:
    ensure_config_dir()
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            stored = json.load(f)
        merged = {**DEFAULTS, **stored}
        return merged
    return dict(DEFAULTS)


def save_config(cfg: dict):
    ensure_config_dir()
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2)
