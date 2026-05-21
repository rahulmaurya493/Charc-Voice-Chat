import os
import io
import time
import streamlit as st
from groq import Groq
from characters import CHARACTERS
from voice_engine import text_to_speech

st.set_page_config(
    page_title="AI Character Voice Chat",
    page_icon="🎭",
    layout="wide",
)

st.markdown("""
<style>
  .hero {
    text-align:center; padding:2rem 1rem 1.5rem;
    background:linear-gradient(135deg,#0f0c29,#302b63,#24243e);
    border-radius:16px; color:white; margin-bottom:2rem;
  }
  .hero h1 { font-size:2.5rem; margin-bottom:0.3rem; }
  .hero p  { opacity:0.75; margin:0; font-size:1rem; }

  .chat-bubble-user {
    background:linear-gradient(135deg,#667eea,#764ba2);
    color:white; padding:0.75rem 1.1rem;
    border-radius:18px 18px 4px 18px;
    max-width:78%; margin:0.4rem 0 0.4rem auto;
    font-size:0.93rem; line-height:1.5; word-wrap:break-word;
  }
  .chat-bubble-ai {
    background:white; color:#1a1a2e;
    padding:0.75rem 1.1rem;
    border-radius:18px 18px 18px 4px;
    max-width:80%; margin:0.4rem 0;
    font-size:0.93rem; line-height:1.6;
    word-wrap:break-word; border:1.5px solid #e8e8e8;
  }
  .chat-label-user { text-align:right; font-size:0.72rem; color:#999; padding-right:4px; margin-bottom:2px; }
  .chat-label-ai   { font-size:0.72rem; color:#999; padding-left:4px; margin-bottom:2px; }

  .chat-container {
    background:#f7f8fc; border-radius:14px;
    padding:1.2rem; min-height:380px; max-height:480px;
    overflow-y:auto; margin-bottom:1rem; border:1px solid #e8e8e8;
  }
  .active-banner {
    display:flex; align-items:center; gap:12px;
    background:white; border:1.5px solid #e0e0e0;
    border-radius:12px; padding:0.7rem 1rem; margin-bottom:1rem;
  }
  .empty-state { text-align:center; padding:3rem 1rem; color:#bbb; }
  div[data-testid="stButton"] > button { border-radius:10px; font-weight:500; }
  div[data-testid="stTextInput"] input { border-radius:10px; border:1.5px solid #e0e0e0; }
</style>
""", unsafe_allow_html=True)

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
  <p>Chat with your favourite characters — they talk back! Powered by Groq + Llama 3.3</p>
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
        label     = f"{char_data['emoji']} {char_name}"
        if msg_count > 0:
            label += f"  · {msg_count}"

        # Create a cleaned version of the label and key to strip out broken characters
        clean_label = label.encode('utf-8', 'ignore').decode('utf-8')
        clean_key = f"btn_{char_name}".encode('utf-8', 'ignore').decode('utf-8')

        if st.button(clean_label, key=clean_key, use_container_width=True, 
                 type="primary" if is_active else "secondary"):
           st.session_state.selected_char = char_name
           st.rerun()

    st.markdown("---")

    # Voice toggle
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
    
            # Banner
    # 1. Define this helper function at the top of your app if you haven't already
    def clean_text(text):
        if not isinstance(text, str):
            return str(text)
        return text.encode('utf-8', 'ignore').decode('utf-8')
    
    # 2. Prepare the clean variables before the markdown block
    safe_emoji = clean_text(cdata.get('emoji', ''))
    safe_char = clean_text(char)
    safe_title = clean_text(cdata.get('title', ''))
    safe_desc = clean_text(cdata.get('description', ''))
    safe_badge = clean_text(voice_badge)
    
    # 3. Use the safe variables in your markdown
    st.markdown(f"""
    <div class='active-banner'>
      <div style='font-size:2rem'>{safe_emoji}</div>
      <div>
        <div style='font-weight:600;font-size:1rem'>{safe_char}</div>
        <div style='font-size:0.78rem;color:#888'>{safe_title} · {safe_desc}</div>
      </div>
      <div style='margin-left:auto;background:{badge_color};color:{badge_text};
                  font-size:0.75rem;font-weight:600;padding:3px 10px;border-radius:20px'>
        {safe_badge}
      </div>
    </div>
    """, unsafe_allow_html=True)
        # Chat bubbles
        chat_html = "<div class='chat-container'>"
        if not history:
            chat_html += f"""
            <div style='text-align:center;padding:3rem 1rem;color:#bbb'>
              <div style='font-size:2.5rem'>{cdata['emoji']}</div>
              <p>Say something to <b>{char}</b>!</p>
            </div>"""
        else:
            for msg in history:
                if msg["role"] == "user":
                    chat_html += f"<div class='chat-label-user'>You</div>"
                    chat_html += f"<div class='chat-bubble-user'>{msg['content']}</div>"
                else:
                    chat_html += f"<div class='chat-label-ai'>{cdata['emoji']} {char}</div>"
                    chat_html += f"<div class='chat-bubble-ai' style='border-color:{cdata['color']}55'>{msg['content']}</div>"
        chat_html += "</div>"
        st.markdown(chat_html, unsafe_allow_html=True)

        # Play last voice reply
        if st.session_state.voice_on and history and history[-1]["role"] == "assistant":
            last_reply = history[-1]["content"]
            if f"audio_{char}_{len(history)}" not in st.session_state:
                with st.spinner("🔊 Generating voice..."):
                    try:
                        audio_bytes = text_to_speech(last_reply, char)
                        st.session_state[f"audio_{char}_{len(history)}"] = audio_bytes
                    except Exception as e:
                        st.warning(f"Voice generation failed: {e}")
            audio_key = f"audio_{char}_{len(history)}"
            if audio_key in st.session_state:
                st.audio(st.session_state[audio_key], format="audio/mp3", autoplay=True)

        # Suggested starters
        starters = {
            "Tony Stark":       ["Are you really a genius?",          "Tell me about your best suit",       "What do you think of Captain America?"],
            "Spider-Man":       ["How did you get your powers?",       "Is being a superhero fun?",          "What does Aunt May think of Spider-Man?"],
            "Narendra Modi":    ["Mitron, what is your vision?",       "Tell me about Digital India",        "What makes India special?"],
            "Shah Rukh Khan":   ["What is love according to you?",     "Tell me your favourite film",        "How do you stay so charming?"],
            "Roman Reigns":     ["Should I acknowledge you?",          "Who is the Head of the Table?",      "Tell me about the Bloodline"],
            "MS Dhoni":         ["How do you stay so calm?",           "Tell me about the 2011 World Cup",   "What is your helicopter shot secret?"],
            "Itachi Uchiha":    ["Why did you do it, Itachi?",         "Do you love Sasuke?",                "What is reality to you?"],
            "Madara Uchiha":    ["Are you the strongest ever?",        "Tell me about Hashirama",            "What is Infinite Tsukuyomi?"],
            "Gojo Satoru":      ["Are you really the strongest?",      "Tell me about Unlimited Void",       "What do you think of your students?"],
            "Zenitsu Agatsuma": ["Are you scared right now?",          "Tell me about Nezuko",               "Can you actually fight?"],
        }

        if not history:
            st.markdown("**💡 Try asking:**")
            cols = st.columns(3)
            for i, q in enumerate(starters.get(char, [])):
                if cols[i].button(q, key=f"s_{char}_{i}", use_container_width=True):
                    st.session_state[f"pending_{char}"] = q
                    st.rerun()

        # Text input
        col_input, col_send = st.columns([5, 1])
        with col_input:
            user_input = st.text_input(
                "msg", placeholder=f"Message {char}...",
                label_visibility="collapsed", key=f"input_{char}"
            )
        with col_send:
            send = st.button("Send ➤", type="primary", use_container_width=True)

        # Handle pending starter question
        if f"pending_{char}" in st.session_state:
            user_input = st.session_state.pop(f"pending_{char}")
            send = True

        # Send & get reply
        if send and user_input.strip():
            client = get_client()

            if char not in st.session_state.chat_histories:
                st.session_state.chat_histories[char] = []

            st.session_state.chat_histories[char].append({
                "role": "user", "content": user_input.strip()
            })

            with st.spinner(f"{cdata['emoji']} {char} is typing..."):
                api_messages  = [{"role": "system", "content": cdata["system_prompt"]}]
                api_messages += st.session_state.chat_histories[char][-10:]

                response = client.chat.completions.create(
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
