"""
Remedy Me — Personalised Hair Care Consultant
Assignment 2 · PPDAI · ESADE

A conversational AI app that collects a user's hair profile through a
3-step chat, then generates a structured remedy plan across four
categories (topical, nutrition, vitamins, daily care) using Llama 3.3
70B via the Groq API.
"""

import streamlit as st
from groq import Groq
import json   # for parsing structured LLM output
import re     # for extracting JSON from free-text LLM responses
import time   # reserved for future streaming / typing-delay effects

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(page_title="Remedy Me", page_icon="🌿", layout="wide")

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,300;0,400;0,600;1,300;1,400&family=DM+Sans:wght@300;400;500&display=swap');

:root {
    --cream: #F4E9CD;
    --warm-white: #F9F2E3;
    --blush: #9DBEBB;
    --terracotta: #468189;
    --deep: #031926;
    --mid: #77ACA2;
    --sage: #9DBEBB;
    --gold: #77ACA2;
    --chat-bg: #F4E9CD;
    --user-bubble: #468189;
    --ai-bubble: #E4F0EF;
}

* { font-family: 'DM Sans', sans-serif; color: var(--deep); }

/* Force light mode across everything */
html, body, [data-testid="stAppViewContainer"], [data-testid="stApp"],
.stApp, .main, section.main { 
    background-color: var(--cream) !important;
    color: var(--deep) !important;
}

.stApp {
    background-color: var(--cream) !important;
    background-image: 
        radial-gradient(ellipse at 20% 50%, rgba(70,129,137,0.06) 0%, transparent 60%),
        radial-gradient(ellipse at 80% 20%, rgba(119,172,162,0.06) 0%, transparent 60%);
}

/* Force all streamlit text elements to dark */
.stApp p, .stApp span, .stApp label, .stApp div,
.stApp h1, .stApp h2, .stApp h3, .stApp h4,
.stMarkdown, .stMarkdown p, .stMarkdown span,
[data-testid="stMarkdownContainer"] p,
[data-testid="stMarkdownContainer"] span {
    color: var(--deep) !important;
}

/* Override: chat header text must be white */
.chat-header div, .chat-header span, .chat-header p,
.chat-title-text, .chat-status {
    color: white !important;
}

/* Hide default streamlit chrome */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 2rem 3rem; max-width: 1200px; }

/* ── Hero ── */
.hero {
    text-align: center;
    padding: 3rem 0 2rem;
    position: relative;
}
.hero-eyebrow {
    font-family: 'DM Sans', sans-serif;
    font-size: 0.75rem;
    font-weight: 500;
    letter-spacing: 0.25em;
    color: var(--terracotta);
    text-transform: uppercase;
    margin-bottom: 1rem;
}
.hero-title {
    font-family: 'Cormorant Garamond', serif;
    font-size: 4.5rem;
    font-weight: 300;
    color: var(--deep);
    line-height: 1.05;
    margin: 0;
    letter-spacing: -0.02em;
}
.hero-title em {
    font-style: italic;
    color: var(--terracotta);
}
.hero-sub {
    font-size: 1rem;
    color: var(--mid);
    margin-top: 1rem;
    font-weight: 300;
    opacity: 0.8;
}
.divider {
    width: 60px;
    height: 1px;
    background: linear-gradient(90deg, transparent, var(--gold), transparent);
    margin: 1.5rem auto;
}

/* ── Chat container ── */
.chat-wrap {
    background: var(--warm-white);
    border-radius: 24px;
    border: 1px solid var(--blush);
    overflow: hidden;
    box-shadow: 0 8px 40px rgba(44,24,16,0.08);
    max-width: 760px;
    margin: 0 auto;
}
.chat-header {
    background: linear-gradient(135deg, var(--deep) 0%, var(--mid) 100%);
    padding: 1.2rem 1.8rem;
    display: flex;
    align-items: center;
    gap: 0.8rem;
}
.chat-avatar {
    width: 38px;
    height: 38px;
    background: var(--terracotta);
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.1rem;
}
.chat-title-text {
    color: white !important;
    font-family: 'Cormorant Garamond', serif;
    font-size: 1.2rem;
    font-weight: 400;
}
.chat-status {
    color: rgba(255,255,255,0.85) !important;
    font-size: 0.7rem;
    letter-spacing: 0.05em;
}
.chat-header * {
    color: white !important;
}

/* ── Messages ── */
.msg-row {
    display: flex;
    gap: 0.75rem;
    margin-bottom: 1rem;
    align-items: flex-end;
}
.msg-row.user { flex-direction: row-reverse; }
.msg-avatar {
    width: 30px;
    height: 30px;
    border-radius: 50%;
    flex-shrink: 0;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 0.85rem;
}
.msg-avatar.ai { background: var(--terracotta); color: white; }
.msg-avatar.user { background: var(--deep); color: white; }
.bubble {
    max-width: 75%;
    padding: 0.75rem 1.1rem;
    border-radius: 18px;
    font-size: 0.92rem;
    line-height: 1.55;
    color: var(--deep);
}
.bubble.ai {
    background: var(--ai-bubble);
    border-bottom-left-radius: 4px;
}
.bubble.user {
    background: var(--user-bubble);
    color: white;
    border-bottom-right-radius: 4px;
}

/* ── Remedy cards ── */
.remedy-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1rem;
    margin: 1.5rem 0;
}
.remedy-card {
    background: white;
    border-radius: 16px;
    padding: 1.2rem 1.4rem;
    border: 1px solid var(--blush);
    box-shadow: 0 2px 12px rgba(44,24,16,0.06);
}
.card-icon { font-size: 1.4rem; margin-bottom: 0.5rem; }
.card-category {
    font-family: 'DM Sans', sans-serif;
    font-size: 0.65rem;
    font-weight: 500;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    color: var(--terracotta);
    margin-bottom: 0.4rem;
}
.card-title {
    font-family: 'Cormorant Garamond', serif;
    font-size: 1.15rem;
    font-weight: 600;
    color: var(--deep);
    margin-bottom: 0.5rem;
}
.card-item {
    font-size: 0.83rem;
    color: var(--mid);
    padding: 0.3rem 0;
    border-bottom: 1px solid rgba(196,113,74,0.1);
    display: flex;
    align-items: flex-start;
    gap: 0.4rem;
}
.card-item:last-child { border-bottom: none; }
.card-item::before { content: "—"; color: var(--gold); flex-shrink: 0; }
.amazon-btn {
    display: inline-block;
    margin-top: 0.7rem;
    padding: 0.35rem 0.9rem;
    background: #FF9900;
    color: white !important;
    border-radius: 20px;
    font-size: 0.72rem;
    font-weight: 500;
    text-decoration: none;
    letter-spacing: 0.03em;
}
.amazon-btn:hover { background: #e68900; }

/* ── Input area ── */
.stTextInput > div > div > input {
    background: var(--warm-white) !important;
    border: 1.5px solid var(--blush) !important;
    border-radius: 50px !important;
    padding: 0.7rem 1.2rem !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.9rem !important;
    color: var(--deep) !important;
    transition: border-color 0.2s;
}
.stTextInput > div > div > input:focus {
    border-color: var(--terracotta) !important;
    box-shadow: 0 0 0 3px rgba(196,113,74,0.1) !important;
}
.stButton > button {
    background: linear-gradient(135deg, var(--terracotta), var(--mid)) !important;
    color: white !important;
    border: none !important;
    border-radius: 50px !important;
    padding: 0.6rem 1.6rem !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 500 !important;
    font-size: 0.85rem !important;
    letter-spacing: 0.03em !important;
    transition: opacity 0.2s !important;
}
.stButton > button:hover { opacity: 0.88 !important; }

/* Form submit button (Send →) */
.stFormSubmitButton > button {
    background: linear-gradient(135deg, var(--terracotta), var(--mid)) !important;
    color: white !important;
    border: none !important;
    border-radius: 50px !important;
    padding: 0.6rem 1.6rem !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 500 !important;
    font-size: 0.85rem !important;
    letter-spacing: 0.03em !important;
    transition: opacity 0.2s !important;
}
.stFormSubmitButton > button:hover { opacity: 0.88 !important; }

/* ── Category selector ── */
.stMultiSelect > div { 
    border-radius: 12px !important;
    border-color: var(--blush) !important;
}
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, var(--warm-white) 0%, #C8E0DE 100%) !important;
    border-right: 1px solid var(--blush);
}
[data-testid="stSidebar"] * { color: #031926 !important; }
[data-testid="stSidebar"] .stMarkdown h2 {
    font-family: 'Cormorant Garamond', serif;
    color: var(--deep) !important;
    font-size: 1.5rem;
    font-weight: 400;
}
[data-baseweb="tag"] { background-color: var(--terracotta) !important; }
[data-baseweb="tag"] span, [data-baseweb="tag"] * { color: white !important; }
[data-baseweb="select"] > div { background-color: var(--warm-white) !important; color: var(--deep) !important; }

.typing-indicator {
    display: flex;
    gap: 4px;
    padding: 0.75rem 1.1rem;
    background: var(--ai-bubble);
    border-radius: 18px;
    border-bottom-left-radius: 4px;
    width: fit-content;
}
.typing-dot {
    width: 7px; height: 7px;
    background: var(--terracotta);
    border-radius: 50%;
    opacity: 0.4;
}
</style>
""", unsafe_allow_html=True)

# ── Helpers ──────────────────────────────────────────────────────────────────

def get_groq_client():
    """
    Initialise and return a Groq client using the API key stored in
    Streamlit secrets. Halts the app with a user-friendly error if the
    key is missing, preventing silent failures in production.
    """
    api_key = st.secrets.get("GROQ_API_KEY", "")
    if not api_key:
        st.error("⚠️ Add your GROQ_API_KEY to .streamlit/secrets.toml")
        st.stop()
    return Groq(api_key=api_key)

SYSTEM_PROMPT = """You are Remedy, a warm, knowledgeable hair care consultant.
Your role is to have a SHORT, friendly conversation (3–4 exchanges max) to learn about the user's hair.

Ask about ONE thing at a time:
1. Their main hair/scalp concern (e.g. thinning, breakage, oiliness, dryness)
2. Their hair texture/type (fine, medium, thick/coarse; straight, wavy, curly, coily)
3. Their primary goal (e.g. growth, hydration, volume, scalp health)

Keep messages concise and warm. Use gentle, elegant language. No bullet points in your questions.

IMPORTANT: If the user's response does not actually answer your question (e.g. they repeat a previous message, go off topic, or give an unclear answer), do NOT move on. Politely acknowledge what they said and ask the same question again in a slightly different way. Only proceed to the next question once you have a clear, relevant answer to the current one. Never assume or infer an answer the user has not explicitly given.

When you have collected all three pieces of information, output ONLY a valid JSON block (no other text) in this exact format:
{
  "profile_complete": true,
  "texture": "...",
  "concern": "...",
  "goal": "...",
  "categories_requested": ["topical", "nutrition", "vitamins", "daily_care"],
  "remedy": {
    "topical": ["remedy 1", "remedy 2", "remedy 3"],
    "nutrition": ["food/drink 1", "food/drink 2", "food/drink 3"],
    "vitamins": ["supplement 1", "supplement 2", "supplement 3"],
    "daily_care": ["habit 1", "habit 2", "habit 3"]
  }
}

Rules for remedy content:
- Each item should be specific and actionable (e.g. "Rosemary water scalp spray 3x/week" not just "rosemary")
- Match all recommendations to the user's specific texture, concern and goal
- Topical: product types or DIY treatments applied to hair/scalp
- Nutrition: specific foods or drinks that support hair health
- Vitamins: specific supplements with dosage hints
- Daily care: routines, habits, tools, lifestyle tips
"""

def chat_with_groq(messages: list) -> str:
    """
    Send the full conversation history to Llama 3.3 70B via Groq and
    return the model's plain-text reply.

    The system prompt is prepended on every call because the Groq API
    is stateless — no conversation context is retained between requests.
    Temperature is set to 0.7 to balance creativity with consistency
    in the remedy recommendations.
    """
    client = get_groq_client()
    groq_messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    for m in messages:
        role = "user" if m["role"] == "user" else "assistant"
        groq_messages.append({"role": role, "content": m["content"]})
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=groq_messages,
        temperature=0.7
    )
    return response.choices[0].message.content

def parse_remedy(text: str):
    """
    Extract and parse the JSON remedy block from the LLM's response.

    The model is instructed to output pure JSON once the profile is
    complete, but may occasionally include surrounding text. A regex
    search isolates the outermost {...} block before parsing, making
    the extraction robust to minor prompt-following failures.

    Returns a dict if valid JSON is found, otherwise None.
    """
    # Greedy match captures the largest {...} block in the response
    match = re.search(r'\{[\s\S]*\}', text)
    if match:
        try:
            return json.loads(match.group())
        except:
            return None  # malformed JSON — treat as a conversational reply
    return None

def amazon_url(query: str) -> str:
    """
    Build an Amazon search URL for a given remedy item.

    Parenthetical details (e.g. dosage hints like "Biotin (5000mcg)")
    are stripped before encoding so the search stays broad enough to
    return relevant product results.
    """
    q = query.split("(")[0].strip().replace(" ", "+")
    return f"https://www.amazon.com/s?k={q}&tag=remedyme-20"

CARD_META = {
    "topical":    {"icon": "🌿", "label": "Topical Treatments", "category": "Applied to hair & scalp"},
    "nutrition":  {"icon": "🥑", "label": "Nutrition",          "category": "Foods & drinks"},
    "vitamins":   {"icon": "💊", "label": "Vitamins & Supplements", "category": "Ingestibles"},
    "daily_care": {"icon": "✨", "label": "Daily Care",          "category": "Habits & routines"},
}

def render_remedy_cards(remedy_data: dict, categories: list):
    """
    Render the remedy plan as a 2-column HTML card grid.

    The number of recommendations per card scales down from 3 to 2 when
    more than 2 categories are selected, keeping the layout balanced and
    avoiding information overload. Amazon links are added only for
    categories where products are purchasable (topical and vitamins).
    """
    n_cats = len(categories)
    # Show fewer items per card when more categories are visible
    n_solutions = 3 if n_cats <= 2 else 2

    cards_html = '<div class="remedy-grid">'
    for cat in categories:
        if cat not in remedy_data or cat not in CARD_META:
            continue
        meta = CARD_META[cat]
        items = remedy_data[cat][:n_solutions]
        items_html = ""
        for item in items:
            amazon = amazon_url(item)
            items_html += f'<div class="card-item">{item}'
            if cat in ("topical", "vitamins"):
                items_html += f' <a href="{amazon}" target="_blank" class="amazon-btn">🛒 Find on Amazon</a>'
            items_html += '</div>'
        cards_html += f"""
        <div class="remedy-card">
            <div class="card-icon">{meta["icon"]}</div>
            <div class="card-category">{meta["category"]}</div>
            <div class="card-title">{meta["label"]}</div>
            {items_html}
        </div>"""
    cards_html += '</div>'
    return cards_html

# ── Session state ─────────────────────────────────────────────────────────────
# Streamlit reruns the entire script on each interaction, so all mutable
# state must live in st.session_state to persist across reruns.
if "messages" not in st.session_state:
    st.session_state.messages = []
if "remedy" not in st.session_state:
    st.session_state.remedy = None
if "selected_cats" not in st.session_state:
    st.session_state.selected_cats = ["topical", "nutrition", "vitamins", "daily_care"]
if "started" not in st.session_state:
    st.session_state.started = False
if "chat_input" not in st.session_state:
    st.session_state.chat_input = ""

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## Remedy Me")
    st.markdown("*Your personal hair care consultant*")
    st.divider()
    st.markdown("**Customise your remedy**")
    st.caption("Choose which categories you'd like in your plan:")
    
    cat_options = {
        "🌿 Topical Treatments": "topical",
        "🥑 Nutrition": "nutrition",
        "💊 Vitamins": "vitamins",
        "✨ Daily Care": "daily_care"
    }
    selected_labels = st.multiselect(
        "Categories",
        options=list(cat_options.keys()),
        default=list(cat_options.keys()),
        label_visibility="collapsed"
    )
    st.session_state.selected_cats = [cat_options[l] for l in selected_labels]
    
    st.divider()
    st.caption("Remedy Me uses AI to generate personalised suggestions. Always consult a trichologist for medical concerns.")

# ── Main page ─────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <div class="hero-eyebrow">Personalised Hair Care</div>
    <h1 class="hero-title">Remedy <em>Me</em></h1>
    <div class="divider"></div>
    <p class="hero-sub">Your AI consultant for a complete, tailored hair care plan</p>
</div>
""", unsafe_allow_html=True)

# ── Chat UI ───────────────────────────────────────────────────────────────────
chat_container = st.container()

with chat_container:
    st.markdown('<div class="chat-wrap">', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="chat-header">
        <div class="chat-avatar">🌿</div>
        <div>
            <div class="chat-title-text" style="color: white !important;">Remedy</div>
            <div class="chat-status" style="color: rgba(255,255,255,0.85) !important;">AI HAIR CONSULTANT · ONLINE</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    msg_area = st.container()
    with msg_area:
        if not st.session_state.started:
            st.markdown("""
            <div style="padding: 2rem; text-align: center; color: #031926; opacity: 0.7;">
                <div style="font-size: 2rem; margin-bottom: 0.5rem;">🌿</div>
                <div style="font-family: 'Cormorant Garamond', serif; font-size: 1.1rem;">
                    Click below to begin your consultation
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown('<div style="padding: 1.2rem 1.5rem;">', unsafe_allow_html=True)
            for msg in st.session_state.messages:
                role = msg["role"]
                content = msg["content"]
                if role == "assistant" and msg.get("is_remedy"):
                    st.markdown(f"""
                    <div class="msg-row">
                        <div class="msg-avatar ai">🌿</div>
                        <div class="bubble ai">Here is your personalised remedy plan! ✨</div>
                    </div>
                    """, unsafe_allow_html=True)
                    st.markdown(render_remedy_cards(
                        msg["remedy_data"],
                        st.session_state.selected_cats
                    ), unsafe_allow_html=True)
                elif role == "assistant":
                    st.markdown(f"""
                    <div class="msg-row">
                        <div class="msg-avatar ai">🌿</div>
                        <div class="bubble ai">{content}</div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class="msg-row user">
                        <div class="msg-avatar user">you</div>
                        <div class="bubble user">{content}</div>
                    </div>
                    """, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# ── Input area ────────────────────────────────────────────────────────────────
st.markdown("<div style='max-width:760px; margin: 1rem auto 0;'>", unsafe_allow_html=True)

if not st.session_state.started:
    if st.button("✨ Begin my consultation", use_container_width=True):
        st.session_state.started = True
        opening = "Hello! I'm Remedy, your personal hair consultant. I'll ask you just a few quick questions to build your custom plan. 💆\u200d♀️\n\nTo start — what's your biggest hair or scalp concern right now?"
        st.session_state.messages.append({"role": "assistant", "content": opening})
        st.rerun()
elif st.session_state.remedy is None:
    with st.form(key="chat_form", clear_on_submit=True):
        col1, col2 = st.columns([5, 1])
        with col1:
            user_input = st.text_input(
                "Message",
                placeholder="Type your answer here…",
                label_visibility="collapsed"
            )
        with col2:
            submitted = st.form_submit_button("Send →", use_container_width=True)
    if submitted and user_input.strip():
        st.session_state.messages.append({"role": "user", "content": user_input.strip()})
        response = chat_with_groq(st.session_state.messages)
        parsed = parse_remedy(response)
        # If the model returned a complete profile JSON, store the remedy
        # and switch the UI to the results view; otherwise continue the chat
        if parsed and parsed.get("profile_complete"):
            st.session_state.remedy = parsed
            st.session_state.messages.append({
                "role": "assistant",
                "content": "",
                "is_remedy": True,
                "remedy_data": parsed["remedy"]
            })
        else:
            st.session_state.messages.append({"role": "assistant", "content": response})
        st.rerun()
else:
    st.markdown("""
    <div style="text-align:center; padding: 0.5rem; color: #031926; font-size: 0.85rem; font-weight: 500;">
        ✅ Your remedy is ready! Adjust categories in the sidebar to customise your plan.
    </div>
    """, unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)