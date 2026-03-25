"""Image description backends: Offline OCR, Google Gemini, Cloudflare Workers AI."""

import base64

import pytesseract
from PIL import Image

from capture import image_to_png_bytes
from config import load_config


# ---------------------------------------------------------------------------
# Offline OCR
# ---------------------------------------------------------------------------

def describe_ocr(img: Image.Image, prompt: str) -> str:
    """Extract text from the image using Tesseract OCR.

    The prompt is ignored since OCR can only extract visible text.
    Returns whatever text is found on screen.
    """
    cfg = load_config()
    tess_path = cfg.get("tesseract_path", "")
    if tess_path:
        pytesseract.pytesseract.tesseract_cmd = tess_path
    try:
        text = pytesseract.image_to_string(img).strip()
    except pytesseract.TesseractNotFoundError:
        return (
            "Tesseract OCR is not installed. "
            "Download it from https://github.com/UB-Mannheim/tesseract/wiki "
            "and either add it to your PATH or set the path in AccessiFight settings."
        )
    if not text:
        return "No readable text detected on screen."
    return text


# ---------------------------------------------------------------------------
# Google Gemini
# ---------------------------------------------------------------------------

def describe_gemini(img: Image.Image, prompt: str) -> str:
    """Send the screenshot to Google Gemini for description."""
    import json as _json
    import urllib.request

    cfg = load_config()
    api_key = cfg.get("gemini_api_key", "")
    model_name = cfg.get("gemini_model", "gemini-2.0-flash")

    if not api_key:
        return "Gemini API key not configured. Please open settings."

    png_bytes = image_to_png_bytes(img)
    b64_image = base64.b64encode(png_bytes).decode("utf-8")

    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
    payload = {
        "contents": [
            {
                "parts": [
                    {"text": prompt},
                    {
                        "inline_data": {
                            "mime_type": "image/png",
                            "data": b64_image,
                        }
                    },
                ]
            }
        ]
    }
    body = _json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=body, method="POST")
    req.add_header("Content-Type", "application/json")

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = _json.loads(resp.read())
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8", errors="replace")
        return f"Gemini API error ({e.code}): {error_body}"

    candidates = data.get("candidates", [])
    if candidates:
        parts = candidates[0].get("content", {}).get("parts", [])
        texts = [p["text"] for p in parts if "text" in p]
        if texts:
            return " ".join(texts).strip()
    return "Gemini returned no response."


def list_gemini_models(api_key: str) -> list[str]:
    """Return a list of Gemini model names that support generateContent."""
    import json as _json
    import urllib.request

    models = []
    url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}&pageSize=100"
    while url:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = _json.loads(resp.read())
        for m in data.get("models", []):
            methods = m.get("supportedGenerationMethods", [])
            if "generateContent" in methods:
                name = m.get("name", "").replace("models/", "")
                if name:
                    models.append(name)
        next_token = data.get("nextPageToken")
        if next_token:
            url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}&pageSize=100&pageToken={next_token}"
        else:
            url = None
    return sorted(models)


# ---------------------------------------------------------------------------
# Cloudflare Workers AI
# ---------------------------------------------------------------------------

def describe_cloudflare(img: Image.Image, prompt: str) -> str:
    """Send the screenshot to Cloudflare Workers AI for description."""
    import json as _json
    import urllib.request

    cfg = load_config()
    account_id = cfg.get("cloudflare_account_id", "")
    api_token = cfg.get("cloudflare_api_token", "")
    model = cfg.get("cloudflare_model", "@cf/meta/llama-4-scout-17b-16e-instruct")

    if not account_id or not api_token:
        return "Cloudflare credentials not configured. Please open settings."

    png_bytes = image_to_png_bytes(img)
    b64_image = base64.b64encode(png_bytes).decode("utf-8")

    url = f"https://api.cloudflare.com/client/v4/accounts/{account_id}/ai/run/{model}"
    payload = {
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{b64_image}"
                        },
                    },
                ],
            }
        ]
    }
    body = _json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=body, method="POST")
    req.add_header("Authorization", f"Bearer {api_token}")
    req.add_header("Content-Type", "application/json")

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = _json.loads(resp.read())
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8", errors="replace")
        # Auto-accept model license agreements (error code 5016)
        try:
            err_data = _json.loads(error_body)
            err_code = (err_data.get("errors") or [{}])[0].get("code")
        except Exception:
            err_code = None
        if e.code == 403 and err_code == 5016:
            agree_err = _cloudflare_agree(url, api_token)
            if agree_err:
                return f"Failed to accept model license: {agree_err}"
            # Retry the original request
            req2 = urllib.request.Request(url, data=body, method="POST")
            req2.add_header("Authorization", f"Bearer {api_token}")
            req2.add_header("Content-Type", "application/json")
            try:
                with urllib.request.urlopen(req2, timeout=30) as resp2:
                    data = _json.loads(resp2.read())
            except urllib.error.HTTPError as e2:
                error_body2 = e2.read().decode("utf-8", errors="replace")
                return f"Cloudflare API error ({e2.code}): {error_body2}"
        else:
            return f"Cloudflare API error ({e.code}): {error_body}"

    if data.get("success"):
        result = data.get("result", {})
        if isinstance(result, dict):
            return result.get("response", str(result))
        return str(result)
    errors = data.get("errors", [])
    return f"Cloudflare API error: {errors}"


def _cloudflare_agree(url: str, api_token: str) -> str | None:
    """Send the 'agree' prompt to accept a Cloudflare model license.

    Returns None on success, or an error string on failure.
    """
    import json as _json
    import urllib.request

    payload = {"prompt": "agree"}
    body = _json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=body, method="POST")
    req.add_header("Authorization", f"Bearer {api_token}")
    req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = _json.loads(resp.read())
            if data.get("success"):
                return None
            return f"Agree response: {data}"
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8", errors="replace")
        if "Thank you for agreeing" in error_body:
            return None
        return f"Agree failed ({e.code}): {error_body}"
    except Exception as e:
        return f"Agree failed: {e}"


CLOUDFLARE_VISION_MODELS = [
    "@cf/meta/llama-4-scout-17b-16e-instruct",
    "@cf/meta/llama-3.2-11b-vision-instruct",
    "@cf/mistralai/mistral-small-3.1-24b-instruct",
    "@cf/llava-hf/llava-1.5-7b-hf",
    "@cf/unum/uform-gen2-qwen-500m",
]


def list_cloudflare_models() -> list[str]:
    """Return the list of known Cloudflare Workers AI vision models."""
    return list(CLOUDFLARE_VISION_MODELS)


# ---------------------------------------------------------------------------
# Dispatch
# ---------------------------------------------------------------------------

BACKENDS = {
    "ocr": describe_ocr,
    "gemini": describe_gemini,
    "cloudflare": describe_cloudflare,
}


def describe_image(img: Image.Image, prompt: str) -> str:
    """Describe an image using the configured backend."""
    cfg = load_config()
    method = cfg.get("method", "")
    backend = BACKENDS.get(method)
    if backend is None:
        return f"Unknown description method '{method}'. Please check settings."
    try:
        return backend(img, prompt)
    except Exception as e:
        return f"Error describing image: {e}"
