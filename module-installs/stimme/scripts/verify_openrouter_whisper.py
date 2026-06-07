"""Standalone-Verifikation, dass die OpenRouter-Whisper-Transkription funktioniert.

So nutzt du das:
    1. Stell sicher, dass OPENROUTER_API_KEY in der .env steht
    2. python3 scripts/verify_openrouter_whisper.py
    3. Skript erzeugt eine kurze Test-Audio-Datei, schickt sie an OpenRouter,
       und prueft, dass eine Transkription zurueckkommt.

Exit-Code 0 = alles gut, 1 = Fehler (Details werden ausgegeben).

Das hier ist die Pflicht-Pruefung VOR dem ersten Bot-Start, damit du sicher
weisst, dass die Sprachnachrichten-Pipeline lebt.
"""

from __future__ import annotations

import base64
import io
import json
import os
import struct
import sys
import urllib.error
import urllib.request
import wave
from pathlib import Path


ENDPOINT = "https://openrouter.ai/api/v1/audio/transcriptions"
MODEL = "openai/whisper-large-v3-turbo"


def find_env_file() -> Path | None:
    """Suche eine .env-Datei: zuerst neben dem Skript, dann hochlaufend bis zum Root."""
    here = Path(__file__).resolve()
    candidates = [
        here.parent / ".env",                # gleiche Ebene wie das Skript
        here.parent.parent / ".env",          # eins drueber (post-install: workspace root)
    ]
    # ausserdem hochlaufen vom CWD
    cwd = Path.cwd().resolve()
    for parent in [cwd, *cwd.parents]:
        candidates.append(parent / ".env")
    for p in candidates:
        if p.exists():
            return p
    return None


ENV_PATH = find_env_file()


def load_api_key() -> str:
    """Read OPENROUTER_API_KEY from .env (or environment)."""
    if ENV_PATH and ENV_PATH.exists():
        try:
            from dotenv import load_dotenv
            load_dotenv(ENV_PATH)
        except ImportError:
            # Fallback: parse .env manually so the script works even without python-dotenv
            for line in ENV_PATH.read_text().splitlines():
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, _, value = line.partition("=")
                os.environ.setdefault(key.strip(), value.strip())

    key = os.environ.get("OPENROUTER_API_KEY", "").strip()
    if not key:
        print("FEHLER: OPENROUTER_API_KEY ist nicht in der .env gesetzt.", file=sys.stderr)
        print(f"        Erwartete Datei: {ENV_PATH or '(keine .env gefunden)'}", file=sys.stderr)
        sys.exit(1)
    if not key.startswith("sk-or-"):
        print(
            "WARNUNG: OPENROUTER_API_KEY beginnt nicht mit 'sk-or-'. "
            "Echte OpenRouter-Keys haben dieses Praefix.",
            file=sys.stderr,
        )
    return key


def make_test_wav() -> bytes:
    """Erzeugt eine Mini-Wav-Datei (1s 440Hz Sinus) als bytes."""
    import math

    sample_rate = 16000
    duration_s = 1
    frequency = 440.0
    amplitude = 16000

    frames = []
    for i in range(sample_rate * duration_s):
        sample = int(amplitude * math.sin(2.0 * math.pi * frequency * i / sample_rate))
        frames.append(struct.pack("<h", sample))

    buf = io.BytesIO()
    with wave.open(buf, "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(sample_rate)
        wav.writeframes(b"".join(frames))
    return buf.getvalue()


def call_openrouter(api_key: str, audio_b64: str, audio_format: str) -> dict:
    """Ruft die OpenRouter-Transcription-API auf, gibt das JSON-Response-Dict zurueck."""
    payload = json.dumps({
        "model": MODEL,
        "input_audio": {
            "data": audio_b64,
            "format": audio_format,
        },
    }).encode("utf-8")

    req = urllib.request.Request(
        url=ENDPOINT,
        data=payload,
        method="POST",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
    )

    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            body = resp.read().decode("utf-8")
            return {"status": resp.status, "body": json.loads(body)}
    except urllib.error.HTTPError as e:
        err_body = e.read().decode("utf-8", errors="replace")
        return {"status": e.code, "body": err_body, "error": True}
    except urllib.error.URLError as e:
        return {"status": 0, "body": str(e.reason), "error": True}


def main() -> int:
    print("=== OpenRouter Whisper Verification ===")
    print(f"Endpoint:  {ENDPOINT}")
    print(f"Modell:    {MODEL}")
    print(f".env:      {ENV_PATH}")
    print()

    api_key = load_api_key()
    print(f"API-Key:   gefunden ({api_key[:10]}...) [{len(api_key)} Zeichen]")

    print("Erzeuge 1s Sinus-Test-Audio (WAV)...")
    audio_bytes = make_test_wav()
    audio_b64 = base64.b64encode(audio_bytes).decode("ascii")
    print(f"Audio:     {len(audio_bytes)} bytes, base64 = {len(audio_b64)} chars")

    print("Sende an OpenRouter...")
    result = call_openrouter(api_key, audio_b64, "wav")

    print(f"\nHTTP-Status: {result['status']}")
    if result.get("error") or result["status"] != 200:
        print("\nFEHLER: Anfrage ist fehlgeschlagen.")
        print("Response Body:")
        print(result["body"])
        print()
        print("Mögliche Ursachen:")
        print("  - Key ist falsch oder hat keine Credits")
        print("  - Lade Credits auf: https://openrouter.ai/credits")
        print("  - Pruefe den Key unter: https://openrouter.ai/keys")
        return 1

    body = result["body"]
    print("\nResponse JSON (full):")
    print(json.dumps(body, indent=2, ensure_ascii=False))
    print()

    # Pruefe, ob das "text"-Feld existiert (das ist, was bot.py liest)
    text = body.get("text")
    if text is None:
        print("FEHLER: Response enthaelt kein 'text'-Feld.")
        print("Vorhandene Felder:", list(body.keys()) if isinstance(body, dict) else "N/A")
        print()
        print("Loesung: Schau in der Response oben nach dem Feld mit der Transkription")
        print("und passe in bot.py Zeile mit `data.get(\"text\")` an.")
        return 1

    print(f"OK: 'text'-Feld gefunden: \"{text.strip()}\"")
    print()
    print("Verifikation erfolgreich. Sprachnachrichten-Transkription ist bereit.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
