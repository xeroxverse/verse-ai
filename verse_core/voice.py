"""
VERSE AI — Realistic 24kHz Neural Voice Engine & "Hello VERSE" Wake-Word System (`verse_core/voice.py`).
Strictly branded VERSE AI.
Voice Personas:
  1. "makoto_tensei_female": Makoto / Tensei (Great Sage / Raphael style) — Calm, crystal-clear, intelligent, realistic female neural voice.
  2. "kenjiro_tsuda_male": Kenjiro Tsuda (Kento Nanami / Seto Kaiba style) — Deep, resonant, composed baritone male neural voice.
  3. "verse_natural": Ultra-Natural Multilingual Conversational Neural Voice.

Key Fixes in v12.0:
  - 12.0s timeout on `edge-tts` (fixes premature 3.2s timeout that caused fallback to robotic offline voice).
  - Background pre-warming of Makoto Tensei & Kenjiro Tsuda voice greetings into `_mp3_cache` on server boot.
  - Mandatory greeting prefix in `WAKE_PHRASES_REGEX` ("Hello VERSE" / "Hey VERSE") so the mic never false-triggers on speaker echoes.
"""

from __future__ import annotations
import asyncio
import base64
import platform
import re
import subprocess
import threading
from typing import Any, Dict


VOICE_PERSONAS: Dict[str, Dict[str, Any]] = {
    "makoto_tensei_female": {
        "label": "VERSE AI — Makoto Tensei (Great Sage / Raphael Female)",
        "gender": "Female",
        "style": "Calm, crystal-clear, composed, hyper-intelligent anime AI (Makoto / Raphael style)",
        "pitch": 1.00,
        "rate": 1.02,
        "edge_voices": {
            "en-IN": "en-US-AvaMultilingualNeural",
            "en-US": "en-US-AvaMultilingualNeural",
            "hi-IN": "hi-IN-SwaraNeural",
            "ja-JP": "ja-JP-NanamiNeural",
        },
        "edge_rate": "+3%",
        "edge_pitch": "-2Hz",
    },
    "kenjiro_tsuda_male": {
        "label": "VERSE AI — Kenjiro Tsuda (Deep Baritone Male)",
        "gender": "Male",
        "style": "Deep, gravelly-warm, calm, authoritative baritone (Kenjiro Tsuda / Nanami style)",
        "pitch": 0.82,
        "rate": 0.93,
        "edge_voices": {
            "en-IN": "en-US-AndrewMultilingualNeural",
            "en-US": "en-US-AndrewMultilingualNeural",
            "hi-IN": "hi-IN-MadhurNeural",
            "ja-JP": "ja-JP-KeitaNeural",
        },
        "edge_rate": "-6%",
        "edge_pitch": "-15Hz",
    },
    "verse_natural": {
        "label": "VERSE AI — Natural Studio Neural (Female)",
        "gender": "Female",
        "style": "Warm, natural conversational studio voice",
        "pitch": 1.00,
        "rate": 1.00,
        "edge_voices": {
            "en-IN": "en-IN-NeerjaExpressiveNeural",
            "en-US": "en-US-EmmaMultilingualNeural",
            "hi-IN": "hi-IN-SwaraNeural",
            "ja-JP": "ja-JP-NanamiNeural",
        },
        "edge_rate": "+1%",
        "edge_pitch": "+0Hz",
    },
}

PERSONA_ALIASES = {
    "verse_anime_female": "makoto_tensei_female",
    "verse_anime_male": "kenjiro_tsuda_male",
    "anime_female": "makoto_tensei_female",
    "anime_male": "kenjiro_tsuda_male",
}

# Greeting prefix is mandatory so random sentences containing "VERSE" never self-trigger wake mode
WAKE_PHRASES_REGEX = re.compile(
    r"^\s*(?:hello|hey|hi|ok|okay|wake\s+up|halo|namaste|listen)\s+(?:verse|varsh|vars|virs|bars|jarvis)(?:\s+ai)?[\s,.:;!-]*(.*)$",
    re.IGNORECASE,
)


class VoiceAssistant:
    """Realistic 24kHz Neural Voice Engine & 'Hello VERSE' Wake-Word Controller for VERSE AI."""

    def __init__(self):
        self.supported_languages = ["en-IN", "hi-IN", "en-US", "ja-JP"]
        self.active_language = "en-IN"
        self.active_persona = "makoto_tensei_female"
        self.voice_gender = "Female"
        self.tts_enabled = True
        self.push_to_talk_ready = True
        self.barge_in_enabled = True
        self.wake_word_phrase = "Hello VERSE"
        self.wake_word_enabled = True
        self._speech_lock = threading.Lock()
        self._active_proc: subprocess.Popen | None = None
        self._mp3_cache: Dict[str, str] = {}
        self.wake_word_status = (
            "ALWAYS_ON_HELLO_VERSE_READY (Say 'Hello VERSE' or toggle Mic / Alt+V)"
        )

    def prewarm_common_phrases_async(self) -> None:
        """Pre-synthesizes common Makoto Tensei & Kenjiro Tsuda greetings in a background daemon thread."""
        def _worker():
            samples = [
                ("makoto_tensei_female", "en-US", "Confirmed. VERSE AI is online and listening, Ankit. What is your command?"),
                ("makoto_tensei_female", "en-US", "Confirmed. I am VERSE AI. All system diagnostics and your eighty percent memory shield are optimal. What is your command, Ankit?"),
                ("kenjiro_tsuda_male", "en-US", "I am online and listening, Ankit. Tell me your command."),
                ("kenjiro_tsuda_male", "en-US", "I am VERSE AI, Ankit. Every subsystem is locked in and under my control. Tell me what task we are executing next."),
            ]
            for persona, lang, txt in samples:
                try:
                    self.synthesize_neural_mp3_base64(txt, persona=persona, language=lang)
                except Exception:
                    pass

        threading.Thread(target=_worker, daemon=True).start()

    def parse_wake_word(self, transcript: str) -> Dict[str, Any]:
        """Detects 'Hello VERSE' / 'Hey VERSE' wake phrase and extracts any trailing command."""
        raw = (transcript or "").strip()
        m = WAKE_PHRASES_REGEX.match(raw)
        if m:
            remainder = m.group(1).strip()
            return {
                "wake_detected": True,
                "wake_phrase": "Hello VERSE",
                "command_after_wake": remainder,
                "wake_only": len(remainder) == 0,
            }
        if raw.lower() in {"hello verse", "hey verse", "wake up verse", "ok verse"}:
            return {
                "wake_detected": True,
                "wake_phrase": "Hello VERSE",
                "command_after_wake": "",
                "wake_only": True,
            }
        return {
            "wake_detected": False,
            "wake_phrase": None,
            "command_after_wake": raw,
            "wake_only": False,
        }

    def resolve_persona(self, persona: str | None) -> str:
        if not persona:
            return self.active_persona
        mapped = PERSONA_ALIASES.get(persona, persona)
        return mapped if mapped in VOICE_PERSONAS else self.active_persona

    def set_persona(self, persona: str) -> Dict[str, Any]:
        resolved = self.resolve_persona(persona)
        self.active_persona = resolved
        self.voice_gender = VOICE_PERSONAS[resolved]["gender"]
        self.stop_speaking()
        return {
            "status": "PERSONA_UPDATED",
            "active_persona": self.active_persona,
            "persona_label": VOICE_PERSONAS[resolved]["label"],
            "voice_gender": self.voice_gender,
        }

    def stop_speaking(self) -> Dict[str, Any]:
        with self._speech_lock:
            if self._active_proc is not None and self._active_proc.poll() is None:
                try:
                    self._active_proc.terminate()
                except Exception:
                    pass
                self._active_proc = None
        return {"status": "STOPPED", "single_voice_lock": True}

    def detect_language(self, text: str) -> str:
        for ch in text or "":
            if "\u0900" <= ch <= "\u097f":
                return "hi-IN"
        hinglish_tokens = {
            "mujhe", "banani", "banao", "karo", "kya", "hai", "mera", "ek",
            "chahiye", "dikhao", "kholo", "chalu", "tum", "kaun", "ho",
            "kaise", "abhi", "batao", "samajh", "apna", "kaam",
        }
        words = {w.strip(".,!?\"'").lower() for w in (text or "").split()}
        if words.intersection(hinglish_tokens):
            return "hi-IN"
        return "en-IN"

    def detect_emotion(self, text: str) -> Dict[str, Any]:
        lower = (text or "").lower()
        if any(k in lower for k in ["error", "fail", "overload", "block", "warning", "alert"]):
            return {"emotion": "TACTICAL_ALERT", "pitch_mod": -0.02, "rate_mod": 0.0}
        if any(k in lower for k in ["completed", "ready", "built", "verified", "confirmed", "pass"]):
            return {"emotion": "COMPOSED_CONFIRMED", "pitch_mod": 0.0, "rate_mod": 0.01}
        if any(k in lower for k in ["plan", "research", "analy", "architecture", "notice"]):
            return {"emotion": "ANALYTICAL_SAGE", "pitch_mod": 0.0, "rate_mod": 0.0}
        return {"emotion": "CALM_REALISTIC", "pitch_mod": 0.0, "rate_mod": 0.0}

    def clean_for_realistic_speech(self, text: str) -> str:
        """Strips markdown/code/symbols so the voice speaks smooth, natural sentences without stuttering."""
        raw = text or ""
        raw = re.sub(r"```[\s\S]*?```", " ", raw)
        raw = re.sub(r"`([^`]+)`", r"\1", raw)
        raw = re.sub(r"https?://\S+", " ", raw)
        raw = re.sub(r"[*_#~>|\\/<>{}\[\]]+", " ", raw)
        raw = re.sub(r"\s*//\s*", ", ", raw)
        raw = re.sub(r"\s+", " ", raw).strip()
        return raw[:280] if raw else "Confirmed. VERSE AI is online and listening."

    def synthesize_neural_mp3_base64(
        self, text: str, persona: str | None = None, language: str | None = None
    ) -> Dict[str, Any]:
        """Synthesizes 24kHz realistic neural MP3 audio via edge-tts with in-memory caching and 12.0s timeout."""
        chosen_key = self.resolve_persona(persona)
        p_cfg = VOICE_PERSONAS[chosen_key]
        clean_text = self.clean_for_realistic_speech(text)
        lang = language or self.detect_language(clean_text)
        voice_name = p_cfg["edge_voices"].get(lang, p_cfg["edge_voices"]["en-IN"])
        cache_key = f"{chosen_key}:{lang}:{clean_text}"

        if cache_key in self._mp3_cache:
            return {
                "status": "NEURAL_MP3_READY",
                "engine": "edge_tts_neural_24khz_cached",
                "voice_name": voice_name,
                "persona": chosen_key,
                "persona_label": p_cfg["label"],
                "voice_gender": p_cfg["gender"],
                "language": lang,
                "spoken_text": clean_text,
                "audio_base64": self._mp3_cache[cache_key],
                "mime_type": "audio/mpeg",
            }

        try:
            import edge_tts  # type: ignore

            async def _gen() -> bytes:
                communicate = edge_tts.Communicate(
                    text=clean_text,
                    voice=voice_name,
                    rate=p_cfg["edge_rate"],
                    pitch=p_cfg["edge_pitch"],
                )
                audio_chunks = bytearray()
                async for chunk in communicate.stream():
                    if chunk.get("type") == "audio" and chunk.get("data"):
                        audio_chunks.extend(chunk["data"])
                return bytes(audio_chunks)

            mp3_bytes = asyncio.run(asyncio.wait_for(_gen(), timeout=12.0))
            if mp3_bytes:
                b64_str = base64.b64encode(mp3_bytes).decode("ascii")
                if len(self._mp3_cache) < 128:
                    self._mp3_cache[cache_key] = b64_str
                return {
                    "status": "NEURAL_MP3_READY",
                    "engine": "edge_tts_neural_24khz",
                    "voice_name": voice_name,
                    "persona": chosen_key,
                    "persona_label": p_cfg["label"],
                    "voice_gender": p_cfg["gender"],
                    "language": lang,
                    "spoken_text": clean_text,
                    "audio_base64": b64_str,
                    "mime_type": "audio/mpeg",
                }
        except Exception:
            pass

        return {
            "status": "WEB_SPEECH_DSP_FALLBACK",
            "engine": "web_audio_dsp_natural",
            "voice_name": voice_name,
            "persona": chosen_key,
            "persona_label": p_cfg["label"],
            "voice_gender": p_cfg["gender"],
            "language": lang,
            "pitch": p_cfg["pitch"],
            "rate": p_cfg["rate"],
            "spoken_text": clean_text,
            "audio_base64": None,
        }

    def speak(
        self,
        text: str,
        language: str | None = None,
        dry_run: bool = True,
        persona: str | None = None,
    ) -> Dict[str, Any]:
        chosen_key = self.resolve_persona(persona)
        p_cfg = VOICE_PERSONAS[chosen_key]
        clean_text = self.clean_for_realistic_speech(text)
        lang = language or self.detect_language(clean_text)
        emo = self.detect_emotion(clean_text)

        final_pitch = round(p_cfg["pitch"] + emo["pitch_mod"], 2)
        final_rate = round(p_cfg["rate"] + emo["rate_mod"], 2)

        if dry_run or platform.system() != "Windows":
            return {
                "status": "SYNTHESIZED_FOR_WEB_AUDIO",
                "engine": "verse_neural_voice_locked",
                "persona": chosen_key,
                "persona_label": p_cfg["label"],
                "style": p_cfg["style"],
                "emotion": emo["emotion"],
                "language": lang,
                "voice_gender": p_cfg["gender"],
                "pitch": final_pitch,
                "rate": final_rate,
                "spoken_text": clean_text,
            }

        with self._speech_lock:
            if self._active_proc is not None and self._active_proc.poll() is None:
                try:
                    self._active_proc.terminate()
                except Exception:
                    pass

            safe_ps_text = clean_text.replace("'", "").replace('"', "")
            ps_rate = -1 if chosen_key == "kenjiro_tsuda_male" else 0
            ps_cmd = (
                "Add-Type -AssemblyName System.Speech; "
                "$s = New-Object System.Speech.Synthesis.SpeechSynthesizer; "
                f"$s.SelectVoiceByHints([System.Speech.Synthesis.VoiceGender]::{p_cfg['gender']}); "
                f"$s.Rate = {ps_rate}; "
                f"$s.Speak('{safe_ps_text}');"
            )
            try:
                self._active_proc = subprocess.Popen(
                    [
                        "powershell",
                        "-NoProfile",
                        "-WindowStyle",
                        "Hidden",
                        "-Command",
                        ps_cmd,
                    ],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
                return {
                    "status": "SPEAKING_NATIVE_WINDOWS_SINGLE_VOICE",
                    "engine": "windows_sapi_verse_locked",
                    "persona": chosen_key,
                    "persona_label": p_cfg["label"],
                    "style": p_cfg["style"],
                    "emotion": emo["emotion"],
                    "language": lang,
                    "voice_gender": p_cfg["gender"],
                    "pitch": final_pitch,
                    "rate": final_rate,
                    "spoken_text": clean_text,
                }
            except Exception as exc:
                return {
                    "status": "FALLBACK_WEB_AUDIO",
                    "engine": "verse_neural_voice_locked",
                    "persona": chosen_key,
                    "persona_label": p_cfg["label"],
                    "emotion": emo["emotion"],
                    "language": lang,
                    "voice_gender": p_cfg["gender"],
                    "pitch": final_pitch,
                    "rate": final_rate,
                    "spoken_text": clean_text,
                    "error": str(exc),
                }

    def status(self) -> Dict[str, Any]:
        edge_installed = False
        try:
            import edge_tts  # type: ignore # noqa: F401
            edge_installed = True
        except Exception:
            pass
        return {
            "agent_name": "VERSE AI",
            "tts_ready": True,
            "edge_tts_24khz_installed": edge_installed,
            "stt_ready_in_dashboard": True,
            "single_voice_lock": True,
            "anime_voice_mode": True,
            "maya_emotional_intelligence": True,
            "barge_in_interruptible": self.barge_in_enabled,
            "wake_word_phrase": self.wake_word_phrase,
            "wake_word_enabled": self.wake_word_enabled,
            "active_persona": self.active_persona,
            "available_personas": VOICE_PERSONAS,
            "voice_gender": self.voice_gender,
            "supported_languages": self.supported_languages,
            "active_language": self.active_language,
            "push_to_talk": "READY (Say 'Hello VERSE', Click Reactor, or Alt+V)",
            "wake_word": self.wake_word_status,
            "native_windows_sapi": platform.system() == "Windows",
        }
