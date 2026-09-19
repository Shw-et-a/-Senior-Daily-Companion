"""
Senior Daily Companion — Main Streamlit Application
=====================================================
A Gen AI-powered, senior-first daily companion website.
Features:
  • Time-aware proactive greeting + daily tip + scam alert
  • 8 large task category tiles (Travel, Health, Tech, Finance, Shopping, Govt, Emergency, Wellness)
  • Multi-turn AI conversation with step-by-step micro-guidance
  • Full EN ↔ HI UI language switch
  • Font size controls (Normal / Large / Extra Large)
  • High Contrast mode
  • Voice TTS (Read Aloud) + STT (Speak to type)
  • Scam detection with prominent warnings
  • Emergency panel with Indian helpline numbers
  • "Explain More Simply" and "Next Step" quick actions
"""

import streamlit as st
import streamlit.components.v1 as components
from datetime import datetime
import pytz

from modules.ai_engine import get_greeting_and_tip, get_task_response
from modules.tasks import TASKS, TASK_ORDER
from modules.voice import render_read_aloud, render_voice_input
from translations import TRANSLATIONS

# ══════════════════════════════════════════════════════════════════════════════
# PAGE CONFIG
# ══════════════════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="Senior Daily Companion",
    page_icon="☀️",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# ══════════════════════════════════════════════════════════════════════════════
# SESSION STATE
# ══════════════════════════════════════════════════════════════════════════════
def _init_state():
    defaults = {
        "lang": "en",
        "font_size": "large",       # "normal" | "large" | "xlarge"
        "high_contrast": False,
        "chat_history": [],          # [{role, content}]
        "selected_category": None,
        "greeting_data": None,
        "greeting_lang": None,
        "show_emergency": False,
        "last_ai_response": None,
        "pending_voice": "",
        "user_input": "",
        "ask_simplify": False,
        "ask_next": False,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

_init_state()


# ══════════════════════════════════════════════════════════════════════════════
# TRANSLATION HELPER
# ══════════════════════════════════════════════════════════════════════════════
def t(key: str) -> str:
    """Return translated string for the current language."""
    lang = st.session_state.lang
    return TRANSLATIONS.get(lang, TRANSLATIONS["en"]).get(key, key)


# ══════════════════════════════════════════════════════════════════════════════
# TIME HELPERS
# ══════════════════════════════════════════════════════════════════════════════
def _get_time_of_day() -> str:
    IST = pytz.timezone("Asia/Kolkata")
    hour = datetime.now(IST).hour
    if 5 <= hour < 12:
        return "morning"
    elif 12 <= hour < 17:
        return "afternoon"
    elif 17 <= hour < 21:
        return "evening"
    return "night"

def _greeting_key_for_time(time_of_day: str) -> str:
    return {
        "morning":   "greeting_morning",
        "afternoon": "greeting_afternoon",
        "evening":   "greeting_evening",
        "night":     "greeting_night",
    }.get(time_of_day, "greeting_morning")

def _formatted_date(lang: str) -> str:
    IST = pytz.timezone("Asia/Kolkata")
    now = datetime.now(IST)
    if lang == "hi":
        months_hi = ["जनवरी","फ़रवरी","मार्च","अप्रैल","मई","जून",
                     "जुलाई","अगस्त","सितंबर","अक्टूबर","नवंबर","दिसंबर"]
        days_hi = ["सोमवार","मंगलवार","बुधवार","गुरुवार","शुक्रवार","शनिवार","रविवार"]
        return f"{days_hi[now.weekday()]}, {now.day} {months_hi[now.month-1]} {now.year}"
    return now.strftime("%A, %d %B %Y")


# ══════════════════════════════════════════════════════════════════════════════
# DYNAMIC CSS
# ══════════════════════════════════════════════════════════════════════════════
def _inject_css():
    sizes = {
        "normal": {"body": "18px", "sub": "22px", "h3": "26px", "h2": "32px", "h1": "42px", "tile": "20px", "tile_icon": "44px"},
        "large":  {"body": "22px", "sub": "26px", "h3": "30px", "h2": "38px", "h1": "50px", "tile": "23px", "tile_icon": "52px"},
        "xlarge": {"body": "27px", "sub": "32px", "h3": "36px", "h2": "46px", "h1": "58px", "tile": "28px", "tile_icon": "60px"},
    }
    s = sizes.get(st.session_state.font_size, sizes["large"])

    if st.session_state.high_contrast:
        c = {
            "bg": "#0a0a0a", "text": "#f0f0f0", "card": "#1a1a1a",
            "primary": "#FFD700", "primary_text": "#000000",
            "accent": "#00BFFF", "border": "#888888",
            "user_bubble": "#001a33", "ai_bubble": "#001a00",
            "tip_bg": "#001a00", "tip_border": "#00FF00",
            "scam_bg": "#1a0000", "scam_border": "#FF4444",
            "input_bg": "#111111", "muted": "#aaaaaa",
            "tile_bg": "#1a1a1a", "tile_border": "#FFD700",
            "section_bg": "#111111",
        }
    else:
        c = {
            "bg": "#EEF2F7", "text": "#1B2631", "card": "#FFFFFF",
            "primary": "#1A5276", "primary_text": "#FFFFFF",
            "accent": "#2E86AB", "border": "#D5D8DC",
            "user_bubble": "#D6EAF8", "ai_bubble": "#EAFAF1",
            "tip_bg": "#EAFAF1", "tip_border": "#27AE60",
            "scam_bg": "#FDEDEC", "scam_border": "#E74C3C",
            "input_bg": "#FFFFFF", "muted": "#7F8C8D",
            "tile_bg": "#FFFFFF", "tile_border": "#2E86AB",
            "section_bg": "#F8F9FA",
        }

    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800;900&display=swap');

    *, *::before, *::after {{ box-sizing: border-box; margin: 0; }}

    html, body {{
        font-family: 'Nunito', Arial, sans-serif !important;
        font-size: {s["body"]} !important;
        background-color: {c["bg"]} !important;
        color: {c["text"]} !important;
        line-height: 1.75 !important;
    }}
    .stApp {{ background-color: {c["bg"]} !important; }}

    /* ── Typography ── */
    h1, .stMarkdown h1 {{
        font-size: {s["h1"]} !important; font-weight: 900 !important;
        color: {c["primary"]} !important; line-height: 1.2 !important;
    }}
    h2, .stMarkdown h2 {{
        font-size: {s["h2"]} !important; font-weight: 800 !important;
        color: {c["text"]} !important;
    }}
    h3, .stMarkdown h3 {{
        font-size: {s["h3"]} !important; font-weight: 700 !important;
        color: {c["primary"]} !important;
    }}
    p, span, div, label, li,
    .stMarkdown, .stText, .stCaption {{
        font-size: {s["body"]} !important;
        color: {c["text"]} !important;
        font-family: 'Nunito', Arial, sans-serif !important;
    }}

    /* ── Streamlit-specific overrides ── */
    .stApp > header {{ display: none !important; }}
    #MainMenu, footer, .stDeployButton {{ visibility: hidden !important; }}
    .block-container {{ padding: 1.5rem 2rem 3rem 2rem !important; max-width: 1200px !important; }}

    /* ── Inputs ── */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {{
        font-family: 'Nunito', Arial, sans-serif !important;
        font-size: {s["sub"]} !important;
        padding: 16px 20px !important;
        border-radius: 14px !important;
        border: 3px solid {c["accent"]} !important;
        background-color: {c["input_bg"]} !important;
        color: {c["text"]} !important;
        min-height: 62px !important;
        line-height: 1.5 !important;
    }}
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {{
        border-color: {c["primary"]} !important;
        box-shadow: 0 0 0 3px rgba(46,134,171,0.25) !important;
        outline: none !important;
    }}

    /* ── Buttons ── */
    .stButton > button {{
        font-family: 'Nunito', Arial, sans-serif !important;
        font-size: {s["sub"]} !important;
        font-weight: 800 !important;
        padding: 16px 24px !important;
        min-height: 66px !important;
        border-radius: 14px !important;
        background-color: {c["primary"]} !important;
        color: {c["primary_text"]} !important;
        border: none !important;
        width: 100% !important;
        cursor: pointer !important;
        transition: all 0.18s ease !important;
        letter-spacing: 0.3px !important;
        line-height: 1.3 !important;
        white-space: pre-line !important;
    }}
    .stButton > button:hover {{
        transform: translateY(-3px) !important;
        box-shadow: 0 8px 24px rgba(0,0,0,0.22) !important;
        filter: brightness(1.08) !important;
    }}
    .stButton > button:active {{ transform: translateY(0) !important; }}

    /* ── Selectbox / Radio ── */
    .stSelectbox > div > div,
    .stRadio > div,
    .stRadio label, .stCheckbox label {{
        font-family: 'Nunito', Arial, sans-serif !important;
        font-size: {s["body"]} !important;
        color: {c["text"]} !important;
    }}
    .stSelectbox select {{ min-height: 52px !important; font-size: {s["body"]} !important; }}

    /* ── Divider ── */
    hr {{ border: 2px solid {c["border"]}; margin: 28px 0; border-radius: 2px; }}

    /* ── Alert boxes ── */
    .stAlert {{
        font-family: 'Nunito', Arial, sans-serif !important;
        font-size: {s["body"]} !important;
        border-radius: 14px !important;
        padding: 18px 22px !important;
    }}
    .stInfo {{ background-color: {c["tip_bg"]} !important; border-left: 6px solid {c["tip_border"]} !important; }}
    .stError {{ background-color: {c["scam_bg"]} !important; border-left: 6px solid {c["scam_border"]} !important; font-weight: 700 !important; }}
    .stSuccess {{ background-color: {c["tip_bg"]} !important; }}

    /* ── Spinner ── */
    .stSpinner > div > div {{ font-size: {s["sub"]} !important; color: {c["primary"]} !important; }}

    /* ════════════════════════════════
       CUSTOM COMPONENTS
    ════════════════════════════════ */

    /* Accessibility top bar */
    .access-bar {{
        background: linear-gradient(90deg, {c["primary"]}, {c["accent"]});
        border-radius: 16px;
        padding: 14px 22px;
        margin-bottom: 22px;
        display: flex; align-items: center;
        box-shadow: 0 4px 16px rgba(0,0,0,0.15);
    }}

    /* App title in bar */
    .bar-title {{
        font-size: {s["h3"]} !important;
        font-weight: 900 !important;
        color: white !important;
        margin: 0 !important;
        white-space: nowrap;
    }}
    .bar-tagline {{
        font-size: {s["body"]} !important;
        color: rgba(255,255,255,0.88) !important;
        margin: 0 !important;
    }}

    /* SOS button */
    .stButton.sos-btn > button {{
        background-color: #E74C3C !important;
        font-size: {s["sub"]} !important;
        min-height: 56px !important;
        font-weight: 900 !important;
        letter-spacing: 0.5px !important;
        animation: pulse 2s infinite;
    }}
    @keyframes pulse {{
        0%, 100% {{ box-shadow: 0 0 0 0 rgba(231,76,60,0.4); }}
        50% {{ box-shadow: 0 0 0 10px rgba(231,76,60,0); }}
    }}

    /* Greeting card */
    .greeting-card {{
        background: linear-gradient(135deg, {c["primary"]} 0%, {c["accent"]} 100%);
        border-radius: 22px;
        padding: 32px 36px;
        margin-bottom: 22px;
        box-shadow: 0 6px 24px rgba(26,82,118,0.2);
    }}
    .greeting-time {{
        font-size: {s["h2"]} !important;
        font-weight: 900 !important;
        color: white !important;
        margin-bottom: 6px !important;
    }}
    .greeting-subtitle {{
        font-size: {s["sub"]} !important;
        color: rgba(255,255,255,0.92) !important;
        margin-bottom: 4px !important;
    }}
    .greeting-date {{
        font-size: {s["body"]} !important;
        color: rgba(255,255,255,0.78) !important;
    }}
    .greeting-ai-text {{
        font-size: {s["sub"]} !important;
        color: white !important;
        background: rgba(255,255,255,0.15);
        border-radius: 12px;
        padding: 14px 18px;
        margin-top: 14px !important;
        font-style: italic;
    }}

    /* Tip card */
    .tip-card {{
        background-color: {c["tip_bg"]};
        border: 2.5px solid {c["tip_border"]};
        border-radius: 18px;
        padding: 22px 26px;
        height: 100%;
        box-shadow: 0 2px 10px rgba(39,174,96,0.1);
    }}
    .tip-card-title {{
        font-size: {s["h3"]} !important;
        font-weight: 800 !important;
        color: #1D8348 !important;
        margin-bottom: 10px !important;
    }}
    .tip-card-body {{
        font-size: {s["body"]} !important;
        color: {c["text"]} !important;
        line-height: 1.8 !important;
    }}

    /* Scam card */
    .scam-card {{
        background-color: {c["scam_bg"]};
        border: 2.5px solid {c["scam_border"]};
        border-radius: 18px;
        padding: 22px 26px;
        height: 100%;
        box-shadow: 0 2px 10px rgba(231,76,60,0.1);
    }}
    .scam-card-title {{
        font-size: {s["h3"]} !important;
        font-weight: 800 !important;
        color: #C0392B !important;
        margin-bottom: 10px !important;
    }}
    .scam-card-body {{
        font-size: {s["body"]} !important;
        color: {c["text"]} !important;
        line-height: 1.8 !important;
    }}

    /* Section titles */
    .section-title {{
        font-size: {s["h2"]} !important;
        font-weight: 900 !important;
        color: {c["primary"]} !important;
        margin: 28px 0 6px !important;
        padding-bottom: 10px !important;
        border-bottom: 3px solid {c["accent"]};
    }}
    .section-sub {{
        font-size: {s["body"]} !important;
        color: {c["muted"]} !important;
        margin-bottom: 18px !important;
    }}

    /* Task tiles */
    .tile-active-badge {{
        background-color: {c["primary"]};
        color: {c["primary_text"]};
        border-radius: 8px;
        padding: 3px 10px;
        font-size: 13px !important;
        font-weight: 700 !important;
        display: inline-block;
        margin-bottom: 6px;
    }}

    /* Chat bubbles */
    .chat-container {{
        background-color: {c["card"]};
        border: 2px solid {c["border"]};
        border-radius: 20px;
        padding: 24px 28px;
        margin: 18px 0;
        max-height: 480px;
        overflow-y: auto;
        box-shadow: 0 2px 12px rgba(0,0,0,0.06);
    }}
    .user-bubble {{
        background-color: {c["user_bubble"]};
        border-radius: 18px 18px 5px 18px;
        padding: 16px 20px;
        margin: 12px 0 12px auto;
        max-width: 82%;
        font-size: {s["body"]} !important;
        box-shadow: 0 1px 4px rgba(0,0,0,0.08);
    }}
    .user-label {{
        font-size: 13px !important;
        font-weight: 800 !important;
        color: {c["primary"]} !important;
        text-align: right;
        margin-bottom: 4px;
    }}
    .ai-bubble {{
        background-color: {c["ai_bubble"]};
        border: 2px solid {c["border"]};
        border-radius: 18px 18px 18px 5px;
        padding: 20px 24px;
        margin: 12px auto 12px 0;
        max-width: 90%;
        font-size: {s["body"]} !important;
        box-shadow: 0 1px 4px rgba(0,0,0,0.06);
    }}
    .ai-label {{
        font-size: 13px !important;
        font-weight: 800 !important;
        color: #1D8348 !important;
        margin-bottom: 4px;
    }}

    /* AI Response cards */
    .response-card {{
        background-color: {c["card"]};
        border: 2.5px solid {c["accent"]};
        border-radius: 20px;
        padding: 26px 30px;
        margin: 16px 0;
        box-shadow: 0 3px 16px rgba(26,82,118,0.1);
    }}
    .response-title {{
        font-size: {s["h3"]} !important;
        font-weight: 900 !important;
        color: {c["primary"]} !important;
        margin-bottom: 6px !important;
    }}
    .response-summary {{
        font-size: {s["body"]} !important;
        color: {c["muted"]} !important;
        margin-bottom: 18px !important;
        font-style: italic;
    }}

    /* Step item */
    .step-item {{
        background-color: {c["section_bg"]};
        border-left: 5px solid {c["primary"]};
        border-radius: 0 12px 12px 0;
        padding: 14px 18px;
        margin: 10px 0;
        font-size: {s["body"]} !important;
    }}
    .step-num {{
        font-size: {s["sub"]} !important;
        font-weight: 900 !important;
        color: {c["primary"]} !important;
    }}
    .step-instruction {{
        font-size: {s["body"]} !important;
        color: {c["text"]} !important;
        line-height: 1.8 !important;
        margin: 4px 0 0 !important;
    }}
    .visual-cue {{
        background-color: {c["tip_bg"]};
        border: 1.5px solid {c["tip_border"]};
        border-radius: 8px;
        padding: 8px 14px;
        margin-top: 8px;
        font-size: {s["body"]} !important;
        color: #1D8348 !important;
    }}
    .encouragement {{
        font-size: {s["sub"]} !important;
        font-weight: 700 !important;
        color: {c["primary"]} !important;
        margin: 16px 0 8px !important;
        text-align: center;
    }}

    /* Scam warning banner */
    .scam-banner {{
        background: linear-gradient(135deg, #922B21, #E74C3C);
        color: white !important;
        border-radius: 16px;
        padding: 22px 26px;
        margin: 14px 0;
        box-shadow: 0 4px 16px rgba(231,76,60,0.35);
    }}
    .scam-banner * {{ color: white !important; }}
    .scam-banner-title {{
        font-size: {s["h3"]} !important;
        font-weight: 900 !important;
        margin-bottom: 10px !important;
    }}
    .scam-banner-body {{
        font-size: {s["body"]} !important;
        line-height: 1.8 !important;
    }}
    .scam-banner-helpline {{
        font-size: {s["sub"]} !important;
        font-weight: 800 !important;
        background: rgba(255,255,255,0.18);
        border-radius: 10px;
        padding: 10px 16px;
        margin-top: 12px;
        display: inline-block;
    }}

    /* Suggestions chips */
    .suggestions-label {{
        font-size: {s["body"]} !important;
        font-weight: 700 !important;
        color: {c["muted"]} !important;
        margin: 16px 0 8px !important;
    }}

    /* Emergency panel */
    .emergency-panel {{
        background: linear-gradient(135deg, #922B21, #C0392B);
        border-radius: 22px;
        padding: 30px 34px;
        color: white !important;
        box-shadow: 0 6px 28px rgba(192,57,43,0.4);
    }}
    .emergency-panel * {{ color: white !important; }}
    .emergency-title {{
        font-size: {s["h2"]} !important;
        font-weight: 900 !important;
        margin-bottom: 6px !important;
    }}
    .emergency-subtitle {{
        font-size: {s["body"]} !important;
        opacity: 0.9;
        margin-bottom: 20px !important;
    }}
    .emergency-number {{
        background: rgba(255,255,255,0.18);
        border-radius: 14px;
        padding: 16px 20px;
        margin: 10px 0;
        font-size: {s["sub"]} !important;
        font-weight: 800 !important;
        border: 2px solid rgba(255,255,255,0.3);
    }}
    .emergency-note {{
        font-size: {s["body"]} !important;
        margin-top: 18px !important;
        background: rgba(0,0,0,0.2);
        border-radius: 10px;
        padding: 12px 16px;
        font-weight: 700 !important;
    }}

    /* Category selected label */
    .cat-selected {{
        background-color: {c["primary"]};
        color: {c["primary_text"]} !important;
        border-radius: 10px;
        padding: 6px 14px;
        font-size: {s["body"]} !important;
        font-weight: 700 !important;
        display: inline-block;
        margin-bottom: 12px;
    }}

    /* Input area container */
    .input-area {{
        background-color: {c["card"]};
        border: 2.5px solid {c["border"]};
        border-radius: 18px;
        padding: 22px 26px;
        margin-top: 16px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
    }}

    /* Footer */
    .app-footer {{
        text-align: center;
        padding: 20px 0 10px;
        font-size: {s["body"]} !important;
        color: {c["muted"]} !important;
        border-top: 2px solid {c["border"]};
        margin-top: 40px;
    }}
    </style>
    """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# GREETING LOADER
# ══════════════════════════════════════════════════════════════════════════════
def _load_greeting():
    """Load greeting once per session (or when language changes)."""
    lang = st.session_state.lang
    if (
        st.session_state.greeting_data is None
        or st.session_state.greeting_lang != lang
    ):
        with st.spinner(t("thinking")):
            tod = _get_time_of_day()
            st.session_state.greeting_data = get_greeting_and_tip(lang, tod)
            st.session_state.greeting_lang = lang


# ══════════════════════════════════════════════════════════════════════════════
# COMPONENT RENDERERS
# ══════════════════════════════════════════════════════════════════════════════

def _render_access_bar():
    """Top accessibility bar: branding, language toggle, font size, contrast, SOS."""
    st.markdown(
        f"""
        <div class="access-bar">
            <div>
                <p class="bar-title">☀️ {t("app_title")}</p>
                <p class="bar-tagline">{t("app_tagline")}</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col_lang, col_font, col_contrast, col_sos = st.columns([2, 3, 2, 1.5])

    with col_lang:
        lang_choice = st.radio(
            t("language_label"),
            options=["🇬🇧 English", "🇮🇳 हिंदी"],
            index=0 if st.session_state.lang == "en" else 1,
            horizontal=True,
            key="_lang_radio",
            label_visibility="collapsed",
        )
        new_lang = "en" if "English" in lang_choice else "hi"
        if new_lang != st.session_state.lang:
            st.session_state.lang = new_lang
            st.session_state.greeting_data = None  # Force greeting reload
            st.rerun()

    with col_font:
        font_labels = [t("font_normal"), t("font_large"), t("font_xlarge")]
        size_map = {t("font_normal"): "normal", t("font_large"): "large", t("font_xlarge"): "xlarge"}
        cur_label = {v: k for k, v in size_map.items()}.get(st.session_state.font_size, font_labels[1])
        font_choice = st.radio(
            t("font_label"),
            options=font_labels,
            index=font_labels.index(cur_label),
            horizontal=True,
            key="_font_radio",
        )
        new_size = size_map[font_choice]
        if new_size != st.session_state.font_size:
            st.session_state.font_size = new_size
            st.rerun()

    with col_contrast:
        new_contrast = st.checkbox(
            t("contrast_label"),
            value=st.session_state.high_contrast,
            key="_contrast_chk",
        )
        if new_contrast != st.session_state.high_contrast:
            st.session_state.high_contrast = new_contrast
            st.rerun()

    with col_sos:
        if st.button(t("sos_button"), key="sos_btn", use_container_width=True):
            st.session_state.show_emergency = not st.session_state.show_emergency
            st.rerun()


def _render_greeting():
    """Time-aware greeting card + daily tip + scam alert cards."""
    tod = _get_time_of_day()
    greeting_key = _greeting_key_for_time(tod)
    greeting_time = t(greeting_key)
    date_str = _formatted_date(st.session_state.lang)

    data = st.session_state.greeting_data or {}
    ai_greeting = data.get("greeting", "")
    daily_tip = data.get("daily_tip", "")
    scam_alert = data.get("scam_alert", "")
    encouragement = data.get("encouragement", "")

    st.markdown(
        f"""
        <div class="greeting-card">
            <p class="greeting-time">{greeting_time}</p>
            <p class="greeting-subtitle">{t("greeting_subtitle")}</p>
            <p class="greeting-date">📅 {t("todays_date")}: {date_str}</p>
            {'<p class="greeting-ai-text">' + ai_greeting + '</p>' if ai_greeting else ''}
            {'<p class="greeting-ai-text">💪 ' + encouragement + '</p>' if encouragement else ''}
        </div>
        """,
        unsafe_allow_html=True,
    )

    if daily_tip or scam_alert:
        tip_col, scam_col = st.columns(2)
        with tip_col:
            st.markdown(
                f"""
                <div class="tip-card">
                    <p class="tip-card-title">{t("daily_tip_title")}</p>
                    <p class="tip-card-body">{daily_tip}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with scam_col:
            st.markdown(
                f"""
                <div class="scam-card">
                    <p class="scam-card-title">{t("scam_alert_title")}</p>
                    <p class="scam-card-body">{scam_alert}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )


def _render_task_tiles():
    """8 task category tiles in a 4×2 grid."""
    st.markdown(f'<p class="section-title">{t("quick_help_title")}</p>', unsafe_allow_html=True)
    st.markdown(f'<p class="section-sub">{t("quick_help_subtitle")}</p>', unsafe_allow_html=True)

    cols = st.columns(4)
    for i, task_id in enumerate(TASK_ORDER):
        task = TASKS[task_id]
        tile_label = t(task["tile_key"])
        is_selected = st.session_state.selected_category == task_id
        col = cols[i % 4]
        with col:
            if is_selected:
                st.markdown('<p class="tile-active-badge">✓ Selected</p>', unsafe_allow_html=True)
            btn_label = ("✅ " if is_selected else "") + tile_label
            if st.button(btn_label, key=f"tile_{task_id}", use_container_width=True):
                st.session_state.selected_category = task_id
                # Add a helpful prompt to get started
                cat_name = t(task["cat_key"])
                lang = st.session_state.lang
                examples = task["examples_hi"] if lang == "hi" else task["examples_en"]
                welcome_msg = (
                    f"{'मैं आपकी' if lang == 'hi' else 'I can help you with'} **{cat_name}** {'में मदद करूँगा' if lang == 'hi' else ''}. "
                    f"\n\n{'उदाहरण के लिए आप पूछ सकते हैं:' if lang == 'hi' else 'For example, you can ask:'}"
                    + "".join(f"\n• {ex}" for ex in examples[:3])
                )
                st.session_state.chat_history = [
                    {"role": "assistant", "content": welcome_msg}
                ]
                st.session_state.last_ai_response = None
                st.rerun()


def _render_chat():
    """Main AI conversation panel."""
    st.markdown(f'<p class="section-title">{t("chat_title")}</p>', unsafe_allow_html=True)

    # Show selected category badge
    if st.session_state.selected_category:
        cat_name = t(TASKS[st.session_state.selected_category]["cat_key"])
        st.markdown(
            f'<span class="cat-selected">{TASKS[st.session_state.selected_category]["icon"]} {cat_name}</span>',
            unsafe_allow_html=True,
        )

    # ── Chat history ──
    history = st.session_state.chat_history
    if not history:
        welcome = t("chat_welcome")
        st.markdown(
            f"""
            <div class="chat-container">
                <div class="ai-bubble">
                    <p class="ai-label">☀️ {t("assistant_label")}</p>
                    <p style="white-space: pre-line;">{welcome}</p>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        bubbles_html = '<div class="chat-container">'
        for msg in history:
            role = msg.get("role", "user")
            content = msg.get("content", "").replace("\n", "<br>")
            if role == "user":
                bubbles_html += f"""
                    <div style="text-align:right;">
                        <p class="user-label">🧑 {t("you_label")}</p>
                        <div class="user-bubble">{content}</div>
                    </div>
                """
            else:
                bubbles_html += f"""
                    <div style="text-align:left;">
                        <p class="ai-label">☀️ {t("assistant_label")}</p>
                        <div class="ai-bubble">{content}</div>
                    </div>
                """
        bubbles_html += "</div>"
        st.markdown(bubbles_html, unsafe_allow_html=True)

    # ── Last AI structured response ──
    if st.session_state.last_ai_response:
        _render_ai_response(st.session_state.last_ai_response)

    # ── Input area ──
    st.markdown('<div class="input-area">', unsafe_allow_html=True)

    # Check for voice input from URL
    voice_text = ""
    try:
        raw_voice = st.query_params.get("voice_input", "")
        if raw_voice:
            from urllib.parse import unquote
            voice_text = unquote(raw_voice)
            # Clear it after reading
            st.query_params.clear()
    except Exception:
        pass

    prefill = voice_text or st.session_state.get("pending_voice", "")

    input_col, voice_col = st.columns([4, 1])
    with input_col:
        user_text = st.text_input(
            label=t("chat_placeholder"),
            value=prefill,
            placeholder=t("chat_placeholder"),
            key="main_input",
            label_visibility="collapsed",
        )
    with voice_col:
        render_voice_input(st.session_state.lang)

    # Quick action buttons
    ask_col, simplify_col, next_col = st.columns([2, 2, 2])
    with ask_col:
        ask_clicked = st.button(t("ask_button"), key="ask_btn", use_container_width=True)
    with simplify_col:
        simplify_clicked = st.button(t("explain_simpler"), key="simplify_btn", use_container_width=True)
    with next_col:
        next_clicked = st.button(t("next_step"), key="next_btn", use_container_width=True)

    st.markdown("</div>", unsafe_allow_html=True)

    # ── Follow-up suggestion chips ──
    if st.session_state.last_ai_response:
        suggestions = st.session_state.last_ai_response.get("follow_up_suggestions", [])
        if suggestions:
            st.markdown(f'<p class="suggestions-label">{t("suggestions_title")}</p>', unsafe_allow_html=True)
            sug_cols = st.columns(min(len(suggestions), 3))
            for i, sug in enumerate(suggestions[:3]):
                with sug_cols[i]:
                    if st.button(f"💬 {sug}", key=f"sug_{i}", use_container_width=True):
                        _handle_query(sug)

    # ── Handle query submission ──
    query_to_send = None
    if ask_clicked and user_text.strip():
        query_to_send = user_text.strip()
    elif simplify_clicked:
        lang = st.session_state.lang
        query_to_send = "कृपया और आसान भाषा में समझाएं।" if lang == "hi" else "Please explain that more simply, like I've never done this before."
    elif next_clicked:
        lang = st.session_state.lang
        query_to_send = "अगला कदम क्या है?" if lang == "hi" else "What is the next step I should do?"

    if query_to_send:
        _handle_query(query_to_send)


def _handle_query(query: str):
    """Run AI query, update history, store structured response."""
    lang = st.session_state.lang
    category = st.session_state.selected_category or "general"
    category_context = TASKS.get(category, {}).get("system_context", "")

    # Add user message to history
    st.session_state.chat_history.append({"role": "user", "content": query})

    # Build history for AI (exclude structured-response messages)
    ai_history = [
        msg for msg in st.session_state.chat_history[:-1]
        if msg.get("role") in ("user", "assistant", "model")
    ]

    with st.spinner(t("thinking")):
        response = get_task_response(
            query=query,
            category=category,
            language=lang,
            history=ai_history,
            category_context=category_context,
        )

    st.session_state.last_ai_response = response

    # Add assistant reply to history (simple text for bubble display)
    summary = response.get("simple_summary", "")
    st.session_state.chat_history.append({
        "role": "assistant",
        "content": summary,
    })

    st.rerun()


def _render_ai_response(resp: dict):
    """Render a structured AI response card with steps, TTS, and actions."""
    lang = st.session_state.lang
    is_scam = resp.get("is_scam_warning", False)

    # Scam warning banner
    if is_scam:
        scam_detail = resp.get("scam_detail", "")
        st.markdown(
            f"""
            <div class="scam-banner">
                <p class="scam-banner-title">{t("scam_banner")}</p>
                <p class="scam-banner-body">{t("scam_detail")}</p>
                {'<p class="scam-banner-body">' + scam_detail + '</p>' if scam_detail else ''}
                <span class="scam-banner-helpline">{t("scam_helpline")}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # Main response card
    step_title = resp.get("step_title", "")
    simple_summary = resp.get("simple_summary", "")
    steps = resp.get("steps", [])
    encouragement = resp.get("encouragement", "")

    st.markdown(
        f"""
        <div class="response-card">
            <p class="response-title">{'⚠️ ' if is_scam else '✅ '}{step_title}</p>
            <p class="response-summary">{simple_summary}</p>
        """,
        unsafe_allow_html=True,
    )

    # Step items
    step_prefix = t("step_prefix")
    visual_label = t("visual_cue_label")
    for step in steps:
        num = step.get("number", "")
        instruction = step.get("instruction", "")
        visual_cue = step.get("visual_cue", "")
        st.markdown(
            f"""
            <div class="step-item">
                <p class="step-num">📌 {step_prefix} {num}</p>
                <p class="step-instruction">{instruction}</p>
                {'<div class="visual-cue">' + visual_label + ' ' + visual_cue + '</div>' if visual_cue else ''}
            </div>
            """,
            unsafe_allow_html=True,
        )

    if encouragement:
        st.markdown(
            f'<p class="encouragement">{t("encouragement_label")} {encouragement}</p>',
            unsafe_allow_html=True,
        )

    st.markdown("</div>", unsafe_allow_html=True)

    # Read Aloud — compile full text
    tts_text = f"{step_title}. {simple_summary}. "
    for step in steps:
        tts_text += f"{t('step_prefix')} {step.get('number','')}: {step.get('instruction','')}. "
    if encouragement:
        tts_text += encouragement

    render_read_aloud(tts_text, lang, t("read_aloud"))


def _render_emergency():
    """Emergency contacts overlay."""
    st.markdown(
        f"""
        <div class="emergency-panel">
            <p class="emergency-title">{t("emergency_title")}</p>
            <p class="emergency-subtitle">{t("emergency_subtitle")}</p>
            <div class="emergency-number">🚑 {t("emergency_ambulance")}</div>
            <div class="emergency-number">🚔 {t("emergency_police")}</div>
            <div class="emergency-number">🚒 {t("emergency_fire")}</div>
            <div class="emergency-number">📞 {t("emergency_helpline")}</div>
            <div class="emergency-number">🛡️ {t("emergency_cyber")}</div>
            <p class="emergency-note">⚡ {t("emergency_note")}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if st.button(t("emergency_close"), key="close_emergency", use_container_width=True):
        st.session_state.show_emergency = False
        st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# MAIN APP
# ══════════════════════════════════════════════════════════════════════════════
def main():
    # 1. Inject CSS
    _inject_css()

    # 2. Accessibility bar (language, font, contrast, SOS)
    _render_access_bar()

    st.divider()

    # 3. Emergency panel (shown full-width if triggered)
    if st.session_state.show_emergency:
        _render_emergency()
        st.divider()

    # 4. Load and show greeting
    _load_greeting()
    _render_greeting()

    st.divider()

    # 5. Task tiles
    _render_task_tiles()

    st.divider()

    # 6. Chat panel
    _render_chat()

    # 7. Footer
    st.markdown(
        f'<p class="app-footer">{t("footer")}</p>',
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
