import os
import streamlit as st
from groq import Groq
from characters import CHARACTERS
from voice_engine import text_to_speech

st.set_page_config(
    page_title="AI Character Voice Chat",
    page_icon="🎭",
    layout="wide",
)

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Rajdhani:wght@400;500;600;700&display=swap');

  /* ── Base ── */
  html, body, [data-testid="stAppViewContainer"] {
    background: #06060f !important;
    color: #e0e8ff !important;
  }

  [data-testid="stAppViewContainer"] {
    background:
      radial-gradient(ellipse 70% 35% at 50% 0%, rgba(120,40,255,0.16) 0%, transparent 65%),
      radial-gradient(ellipse 50% 25% at 90% 90%, rgba(0,210,180,0.09) 0%, transparent 55%),
      #06060f !important;
  }

  body, p, li, span, div, label, input {
    font-family: 'Rajdhani', sans-serif !important;
    letter-spacing: 0.02em;
  }

  h1, h2, h3 {
    font-family: 'Orbitron', monospace !important;
  }

  /* ── HERO ── */
  .hero {
    text-align: center;
    padding: 2.2rem 1rem 1.8rem;
    background: linear-gradient(135deg, rgba(10,8,32,0.95), rgba(20,10,50,0.90));
    border: 1px solid rgba(120,50,255,0.35);
    border-radius: 16px;
    color: white;
    margin-bottom: 1.8rem;
    position: relative;
    overflow: hidden;
  }

  .hero::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, transparent, #7b2fff, #00e6b4, transparent);
  }

  .hero h1 {
    font-family: 'Orbitron', monospace !important;
    font-size: 2.2rem;
    font-weight: 900;
    margin-bottom: 0.4rem;
    background: linear-gradient(90deg, #00e6b4, #7b2fff, #ff4fa3);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    filter: drop-shadow(0 0 20px rgba(123,47,255,0.5));
  }

  .hero p {
    font-family: 'Rajdhani', sans-serif !important;
    opacity: 0.7;
    margin: 0;
    font-size: 0.95rem;
    letter-spacing: 0.08em;
    text-transform: uppercase;
  }

  /* ── CHAT BUBBLES ── */
  .chat-bubble-user {
    background: linear-gradient(135deg, #7b2fff, #5b1fcc);
    color: white;
    padding: 0.7rem 1.1rem;
    border-radius: 18px 18px 4px 18px;
    max-width: 78%;
    margin: 0.4rem 0 0.4rem auto;
    font-size: 0.95rem;
    line-height: 1.55;
    word-wrap: break-word;
    box-shadow: 0 0 14px rgba(123,47,255,0.35);
  }

  .chat-bubble-ai {
    background: rgba(14,12,38,0.92);
    color: #dde6ff;
    padding: 0.7rem 1.1rem;
    border-radius: 18px 18px 18px 4px;
    max-width: 80%;
    margin: 0.4rem 0;
    font-size: 0.95rem;
    line-height: 1.6;
    word-wrap: break-word;
    border: 1px solid rgba(123,47,255,0.3);
    box-shadow: 0 0 12px rgba(0,0,0,0.3);
  }

  .chat-label-user {
    text-align: right;
    font-size: 0.7rem;
    color: #7b8cc8;
    padding-right: 4px;
    margin-bottom: 2px;
    letter-spacing: 0.06em;
    text-transform: uppercase;
  }

  .chat-label-ai {
    font-size: 0.7rem;
    color: #7b8cc8;
    padding-left: 4px;
    margin-bottom: 2px;
    letter-spacing: 0.06em;
    text-transform: uppercase;
  }

  /* ── CHAT CONTAINER ── */
  .chat-container {
    background: rgba(8,6,22,0.85);
    border: 1px solid rgba(123,47,255,0.2);
    border-radius: 14px;
    padding: 1.2rem;
    min-height: 380px;
    max-height: 480px;
    overflow-y: auto;
    margin-bottom: 1rem;
  }

  .chat-container::-webkit-scrollbar { width: 4px; }
  .chat-container::-webkit-scrollbar-track { background: transparent; }
  .chat-container::-webkit-scrollbar-thumb { background: rgba(123,47,255,0.4); border-radius: 4px; }

  /* ── ACTIVE BANNER ── */
  .active-banner {
    display: flex;
    align-items: center;
    gap: 12px;
    background: rgba(14,12,38,0.90);
    border: 1px solid rgba(123,47,255,0.3);
    border-radius: 12px;
    padding: 0.7rem 1rem;
    margin-bottom: 1rem;
  }

  /* ── SIDEBAR CHARACTER BUTTONS ── */
  div[data-testid="stButton"] > button {
    border-radius: 10px !important;
    font-family: 'Rajdhani', sans-serif !important;
    font-weight: 600 !important;
    letter-spacing: 0.04em !important;
    transition: all 0.18s ease !important;
    border: 1px solid rgba(123,47,255,0.4) !important;
    background: rgba(10,8,30,0.8) !important;
    color: #b0bcff !important;
  }

  div[data-testid="stButton"] > button:hover {
    background: rgba(123,47,255,0.15) !important;
    border-color: #7b2fff !important;
    color: #fff !important;
    box-shadow: 0 0 16px rgba(123,47,255,0.3) !important;
  }

  div[data-testid="stButton"] > button[kind="primary"] {
    background: linear-gradient(135deg, #7b2fff, #5b1fcc) !important;
    border-color: #9b5fff !important;
    color: #fff !important;
    box-shadow: 0 0 14px rgba(123,47,255,0.4) !important;
  }

  div[data-testid="stButton"] > button[kind="primary"]:hover {
    background: linear-gradient(135deg, #9b5fff, #7b2fff) !important;
    box-shadow: 0 0 24px rgba(123,47,255,0.55) !important;
  }

  /* ── TEXT INPUT ── */
  div[data-testid="stTextInput"] input {
    border-radius: 10px !important;
    background: rgba(10,8,30,0.85) !important;
    border: 1px solid rgba(123,47,255,0.4) !important;
    color: #dde6ff !important;
    font-family: 'Rajdhani', sans-serif !important;
    font-size: 1rem !important;
  }

  div[data-testid="stTextInput"] input:focus {
    border-color: #7b2fff !important;
    box-shadow: 0 0 10px rgba(123,47,255,0.25) !important;
  }

  /* ── TOGGLE ── */
  [data-testid="stToggle"] label {
    font-family: 'Rajdhani', sans-serif !important;
    font-size: 0.9rem !important;
    color: #8892c8 !important;
    letter-spacing: 0.05em !important;
  }

  /* ── DIVIDER ── */
  hr {
    border: none !important;
    border-top: 1px solid rgba(123,47,255,0.2) !important;
    margin: 1rem 0 !important;
  }

  /* ── SECTION HEADERS ── */
  h3 {
    font-family: 'Orbitron', monospace !important;
    font-size: 0.85rem !important;
    color: #7b2fff !important;
    letter-spacing: 0.12em !important;
    text-transform: uppercase !important;
  }

  /* ── ALERTS / SPINNER ── */
  [data-testid="stAlert"] {
    font-family: 'Rajdhani', sans-serif !important;
    border-radius: 8px !important;
  }

  /* ── SIDEBAR ── */
  [data-testid="stSidebar"] { display: none !important; }
  [data-testid="collapsedControl"] { display: none !important; }

  /* ── EMPTY STATE ── */
  .empty-state { text-align: center; padding: 3rem 1rem; color: #555; }
  .empty-state p { font-family: 'Rajdhani', sans-serif; font-size: 1rem; letter-spacing: 0.04em; }
</style>
""", unsafe_allow_html=True)


# ── Helper ────────────────────────────────────────────────────────────────────
def clean_text(text):
    if not isinstance(text, str):
        return str(text)
    return text.encode("utf-8", "ignore").decode("utf-8")


# ── Groq client ───────────────────────────────────────────────────────────────
@st.cache_resource
def get_client():
    api_key = os.environ.get("GROQ_API_KEY") or st.secrets.get("GROQ_API_KEY", "")
    if not api_key:
        st.error("GROQ_API_KEY missing from Streamlit Secrets.")
        st.stop()
    return Groq(api_key=api_key)


# ── Session state ─────────────────────────────────────────────────────────────
for k, v in [
    ("selected_char",  None),
    ("chat_histories", {}),
    ("voice_on",       True),
]:
    if k not in st.session_state:
        st.session_state[k] = v


# ── Hero ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div class='hero'>
  <h1>🎭 AI Character Voice Chat</h1>
  <p>Chat with your favourite characters — they talk back! &nbsp;|&nbsp; Powered by Groq + Llama 3.3</p>
</div>
""", unsafe_allow_html=True)


# ── Layout ────────────────────────────────────────────────────────────────────
sidebar, chat_col = st.columns([1, 2.6], gap="large")


# ── SIDEBAR ───────────────────────────────────────────────────────────────────
with sidebar:
    st.markdown("### 🎬 Pick a Character")

    for char_name, char_data in CHARACTERS.items():
        is_active = st.session_state.selected_char == char_name
        history   = st.session_state.chat_histories.get(char_name, [])
        msg_count = len([m for m in history if m["role"] == "user"])
        label     = f"{clean_text(char_data['emoji'])} {clean_text(char_name)}"
        if msg_count > 0:
            label += f"  · {msg_count}"

        clean_key = f"btn_{char_name}".encode("utf-8", "ignore").decode("utf-8")

        if st.button(label, key=clean_key, use_container_width=True,
                     type="primary" if is_active else "secondary"):
            st.session_state.selected_char = char_name
            st.rerun()

    st.markdown("---")

    st.session_state.voice_on = st.toggle(
        "🔊 Voice replies", value=st.session_state.voice_on
    )

    st.markdown("---")

    if st.session_state.selected_char:
        if st.button("🗑️ Clear this chat", use_container_width=True):
            st.session_state.chat_histories[st.session_state.selected_char] = []
            st.rerun()

    if st.button("🗑️ Clear ALL chats", use_container_width=True):
        st.session_state.chat_histories = {}
        st.rerun()


# ── CHAT AREA ─────────────────────────────────────────────────────────────────
with chat_col:
    if not st.session_state.selected_char:
        st.markdown("""
        <div class='empty-state'>
          <div style='font-size:3rem'>👈</div>
          <p>Select a character from the left to start chatting!</p>
        </div>
        """, unsafe_allow_html=True)

    else:
        char    = st.session_state.selected_char
        cdata   = CHARACTERS[char]
        history = st.session_state.chat_histories.get(char, [])

        # ── Voice badge ───────────────────────────────────────────────────────
        if st.session_state.voice_on:
            voice_badge  = "🔊 Voice ON"
            badge_color  = "rgba(0,230,150,0.15)"
            badge_text   = "#00e696"
            badge_border = "#00e696"
        else:
            voice_badge  = "🔇 Voice OFF"
            badge_color  = "rgba(255,60,100,0.1)"
            badge_text   = "#ff6b8a"
            badge_border = "#ff3c64"

        # ── Active banner ─────────────────────────────────────────────────────
        safe_emoji = clean_text(cdata.get("emoji", ""))
        safe_char  = clean_text(char)
        safe_title = clean_text(cdata.get("title", ""))
        safe_desc  = clean_text(cdata.get("description", ""))
        safe_badge = clean_text(voice_badge)

        st.markdown(f"""
        <div class='active-banner'>
          <div style='font-size:2rem'>{safe_emoji}</div>
          <div>
            <div style='font-weight:700; font-size:1rem; color:#dde6ff; font-family:Rajdhani,sans-serif;'>{safe_char}</div>
            <div style='font-size:0.78rem; color:#7b8cc8; letter-spacing:0.04em;'>{safe_title} · {safe_desc}</div>
          </div>
          <div style='margin-left:auto; background:{badge_color}; color:{badge_text};
                      border:1px solid {badge_border}; font-size:0.73rem; font-weight:700;
                      padding:3px 10px; border-radius:20px; font-family:Rajdhani,sans-serif;
                      letter-spacing:0.06em;'>
            {safe_badge}
          </div>
        </div>
        """, unsafe_allow_html=True)

        # ── Chat bubbles ──────────────────────────────────────────────────────
        chat_html = "<div class='chat-container'>"
        if not history:
            chat_html += f"""
            <div style='text-align:center; padding:3rem 1rem; color:#555;'>
              <div style='font-size:2.5rem'>{clean_text(cdata['emoji'])}</div>
              <p style='font-family:Rajdhani,sans-serif; letter-spacing:0.04em;'>Say something to <b style='color:#b0bcff'>{clean_text(char)}</b>!</p>
            </div>"""
        else:
            for msg in history:
                if msg["role"] == "user":
                    chat_html += f"<div class='chat-label-user'>You</div>"
                    chat_html += f"<div class='chat-bubble-user'>{clean_text(msg['content'])}</div>"
                else:
                    chat_html += f"<div class='chat-label-ai'>{clean_text(cdata['emoji'])} {clean_text(char)}</div>"
                    chat_html += f"<div class='chat-bubble-ai' style='border-color:{cdata['color']}66'>{clean_text(msg['content'])}</div>"
        chat_html += "</div>"
        st.markdown(chat_html, unsafe_allow_html=True)

        # ── Play last voice reply ─────────────────────────────────────────────
        if st.session_state.voice_on and history and history[-1]["role"] == "assistant":
            last_reply = history[-1]["content"]
            audio_key  = f"audio_{char}_{len(history)}"
            if audio_key not in st.session_state:
                with st.spinner("🔊 Generating voice..."):
                    try:
                        audio_bytes = text_to_speech(last_reply, char)
                        st.session_state[audio_key] = audio_bytes
                    except Exception as e:
                        st.warning(f"Voice generation failed: {e}")
            if audio_key in st.session_state:
                st.audio(st.session_state[audio_key], format="audio/mp3", autoplay=True)

        # ── Suggested starters ────────────────────────────────────────────────
        starters = {
            "Tony Stark":       ["Are you really a genius?",         "Tell me about your best suit",      "What do you think of Captain America?"],
            "Spider-Man":       ["How did you get your powers?",      "Is being a superhero fun?",         "What does Aunt May think of Spider-Man?"],
            "Narendra Modi":    ["Mitron, what is your vision?",      "Tell me about Digital India",       "What makes India special?"],
            "Shah Rukh Khan":   ["What is love according to you?",    "Tell me your favourite film",       "How do you stay so charming?"],
            "Roman Reigns":     ["Should I acknowledge you?",         "Who is the Head of the Table?",     "Tell me about the Bloodline"],
            "MS Dhoni":         ["How do you stay so calm?",          "Tell me about the 2011 World Cup",  "What is your helicopter shot secret?"],
            "Itachi Uchiha":    ["Why did you do it, Itachi?",        "Do you love Sasuke?",               "What is reality to you?"],
            "Madara Uchiha":    ["Are you the strongest ever?",       "Tell me about Hashirama",           "What is Infinite Tsukuyomi?"],
            "Gojo Satoru":      ["Are you really the strongest?",     "Tell me about Unlimited Void",      "What do you think of your students?"],
            "Zenitsu Agatsuma": ["Are you scared right now?",         "Tell me about Nezuko",              "Can you actually fight?"],
        }

        if not history:
            st.markdown("<p style='font-family:Rajdhani,sans-serif; font-size:0.85rem; color:#7b8cc8; letter-spacing:0.06em; text-transform:uppercase;'>💡 Try asking:</p>", unsafe_allow_html=True)
            cols = st.columns(3)
            for i, q in enumerate(starters.get(char, [])):
                if cols[i].button(q, key=f"s_{char}_{i}", use_container_width=True):
                    st.session_state[f"pending_{char}"] = q
                    st.rerun()

        # ── Text input ────────────────────────────────────────────────────────
        col_input, col_send = st.columns([5, 1])
        with col_input:
            user_input = st.text_input(
                "msg",
                placeholder=f"Message {clean_text(char)}...",
                label_visibility="collapsed",
                key=f"input_{char}",
            )
        with col_send:
            send = st.button("Send ➤", type="primary", use_container_width=True)

        # ── Handle pending starter ────────────────────────────────────────────
        if f"pending_{char}" in st.session_state:
            user_input = st.session_state.pop(f"pending_{char}")
            send = True

        # ── Send & get reply ──────────────────────────────────────────────────
        if send and user_input.strip():
            client = get_client()

            if char not in st.session_state.chat_histories:
                st.session_state.chat_histories[char] = []

            st.session_state.chat_histories[char].append({
                "role": "user", "content": user_input.strip()
            })

            with st.spinner(f"{clean_text(cdata['emoji'])} {clean_text(char)} is typing..."):
                api_messages  = [{"role": "system", "content": cdata["system_prompt"]}]
                api_messages += st.session_state.chat_histories[char][-10:]

                response = get_client().chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=api_messages,
                    max_tokens=500,
                    temperature=0.92,
                )
                reply = response.choices[0].message.content

            st.session_state.chat_histories[char].append({
                "role": "assistant", "content": reply
            })
            st.rerun()
