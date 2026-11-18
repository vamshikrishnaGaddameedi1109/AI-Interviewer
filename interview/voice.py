"""Voice synthesis and Web Speech API utilities for AI Interviewer."""

import os
import io
import re
from typing import Optional, Dict, Any
import streamlit as st
import streamlit.components.v1 as components

# Declare bidirectional Streamlit Web Speech API component
_VOICE_COMP_DIR = os.path.join(os.path.dirname(__file__), "voice_component")
_voice_input_func = components.declare_component(
    "voice_input_component",
    path=_VOICE_COMP_DIR
)


def voice_input_widget(key: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """
    Renders the browser's Web Speech API speech-to-text hook component.
    Enables candidates to transcribe spoken answers directly in the browser using their microphone.
    
    Returns:
        None if idle, or a dictionary containing:
        {
            "action": "submit",
            "text": "spoken transcript...",
            "timestamp": 123456789
        }
    """
    return _voice_input_func(key=key, default=None)


@st.cache_data(show_spinner=False, max_entries=50)
def generate_speech_audio_bytes(text: str) -> Optional[bytes]:
    """
    Generate an MP3 audio byte stream from question text using Google TTS (gTTS).
    Strips code fences, emojis, or markdown characters for a clean, natural spoken delivery.
    """
    if not text or not text.strip():
        return None

    # Clean markdown, URLs, bullet formatting, and symbols for natural spoken cadence
    clean_text = re.sub(r"```[\s\S]*?```", " Code snippet provided. ", text)
    clean_text = re.sub(r"`([^`]+)`", r"\1", clean_text)
    clean_text = re.sub(r"[*_~#>|]", "", clean_text)
    clean_text = re.sub(r"\bhttps?://\S+", "", clean_text)
    clean_text = re.sub(r"\s+", " ", clean_text).strip()

    if not clean_text:
        return None

    try:
        from gtts import gTTS
        fp = io.BytesIO()
        # English conversational voice
        tts = gTTS(text=clean_text, lang="en", tld="com", slow=False)
        tts.write_to_fp(fp)
        fp.seek(0)
        return fp.getvalue()
    except Exception as e:
        print(f"Warning: TTS generation failed: {e}")
        return None


def render_voice_player_widget(text: str, autoplay: bool = False, msg_idx: int = 0) -> None:
    """
    Renders an audio player for an interviewer question.
    Generates high quality audio via gTTS, and renders standard HTML5 audio with autoplay.
    Also provides a browser Web Speech API button as a zero-latency fallback.
    """
    audio_bytes = generate_speech_audio_bytes(text)
    if audio_bytes:
        st.audio(audio_bytes, format="audio/mp3", autoplay=autoplay)
    else:
        # Fallback to browser Web Speech API if gTTS is unreachable
        render_browser_voice_player(text, auto_play=autoplay, element_id=f"voice_msg_{msg_idx}")


def render_browser_voice_player(text: str, auto_play: bool = False, element_id: str = "tts_player") -> None:
    """
    Renders a Web Speech API audio controller with Speak, Pause, and Resume buttons.
    Provides instant browser-native speech synthesis without relying on network audio.
    """
    safe_text = (
        text.replace("\\", "\\\\")
        .replace("`", "\\`")
        .replace("$", "\\$")
        .replace("\n", " ")
        .replace('"', '\\"')
        .replace("'", "\\'")
    )

    html_code = f"""
    <div style="display: flex; align-items: center; gap: 8px; margin: 4px 0 8px 0; font-family: system-ui, sans-serif;">
        <button id="btn_speak_{element_id}" onclick="speakQuestion_{element_id}()" 
            style="background: #2563eb; color: #ffffff; border: none; border-radius: 6px; padding: 6px 12px; font-size: 13px; font-weight: 500; cursor: pointer; display: inline-flex; align-items: center; gap: 6px; box-shadow: 0 1px 2px rgba(0,0,0,0.1);">
            🔊 Read Aloud
        </button>
        <button id="btn_stop_{element_id}" onclick="stopSpeech_{element_id}()" 
            style="background: #f1f5f9; color: #334155; border: 1px solid #cbd5e1; border-radius: 6px; padding: 6px 10px; font-size: 13px; font-weight: 500; cursor: pointer;">
            ⏹️ Stop
        </button>
        <span id="status_{element_id}" style="font-size: 12px; color: #64748b;"></span>
    </div>

    <script>
        const textToSpeak_{element_id} = "{safe_text}";

        function updateStatus_{element_id}(msg) {{
            const el = document.getElementById("status_{element_id}");
            if (el) el.innerText = msg;
        }}

        function stopSpeech_{element_id}() {{
            if ('speechSynthesis' in window) {{
                window.speechSynthesis.cancel();
                updateStatus_{element_id}("");
            }}
        }}

        function speakQuestion_{element_id}() {{
            if (!('speechSynthesis' in window)) {{
                updateStatus_{element_id}("Speech synthesis not supported.");
                return;
            }}

            window.speechSynthesis.cancel();
            const utterance = new SpeechSynthesisUtterance(textToSpeak_{element_id});
            utterance.rate = 1.0;
            utterance.pitch = 1.0;
            
            const voices = window.speechSynthesis.getVoices();
            const englishVoice = voices.find(v => v.lang.startsWith('en') && (v.name.includes('Natural') || v.name.includes('Google') || v.name.includes('Samantha') || v.name.includes('Daniel') || v.name.includes('US')));
            if (englishVoice) {{
                utterance.voice = englishVoice;
            }}

            utterance.onstart = () => updateStatus_{element_id}("Speaking...");
            utterance.onend = () => updateStatus_{element_id}("");
            utterance.onerror = (e) => {{
                console.error("Speech error", e);
                updateStatus_{element_id}("");
            }};

            window.speechSynthesis.speak(utterance);
        }}

        {"speakQuestion_" + element_id + "();" if auto_play else ""}
    </script>
    """
    components.html(html_code, height=44)
