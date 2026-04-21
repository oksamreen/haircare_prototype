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
import json      # for parsing structured LLM output
import re        # for extracting JSON from free-text LLM responses
import time      # reserved for future streaming / typing-delay effects
import os        # for feedback log path resolution
import requests  # for Spoonacular recipe API calls
from datetime import datetime, timezone  # for timestamping feedback entries

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
Do not end messages with a sentence explaining why you are asking the question (e.g. "This will help me tailor your plan", "This helps me match remedies to your needs"). You can still be warm — just let the question speak for itself.

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
  },
  "youtube_queries": ["specific YouTube search query for habit 1", "specific YouTube search query for habit 2", "specific YouTube search query for habit 3"]
}

Rules for remedy content:
- Each item should be specific and actionable (e.g. "Rosemary water scalp spray 3x/week" not just "rosemary")
- Match all recommendations to the user's specific texture, concern and goal
- Topical: product types or DIY treatments applied to hair/scalp
- Nutrition: specific foods or drinks that support hair health
- Vitamins: specific supplements with dosage hints
- Daily care: routines, habits, tools, lifestyle tips
- Evidence: after each recommendation, append a brief evidence note in square brackets, e.g.
  "Rosemary oil scalp massage 3×/week [Panahi et al., 2015 — comparable to minoxidil 2% for hair count]"
  or "Biotin 2500–5000 mcg daily [supports keratin infrastructure; deficiency linked to hair loss — Patel et al., 2017]"
  Keep citations concise (author, year, one-line finding). If no specific paper exists, cite a well-known mechanism instead, e.g. "[anti-inflammatory DHT-blocker via 5α-reductase inhibition]".
- YouTube queries: for each daily_care item, write the exact search phrase a user would type on YouTube to find a helpful tutorial — be specific and include hair type/texture context, e.g. "rice water rinse tutorial for 4C natural hair" not just "rice water rinse".
"""

FEEDBACK_LOG_PATH = os.path.join(os.path.dirname(__file__), "feedback_log.json")

def log_feedback(helpful: bool, personalised: bool, comment: str, profile: dict):
    """
    Append a feedback entry to feedback_log.json alongside the user's
    hair profile so responses can be correlated with personalisation quality.

    The file is created on first use; subsequent calls append to the list.
    """
    entry = {
        "timestamp": datetime.now(tz=timezone.utc).isoformat(),
        "helpful": helpful,
        "felt_personalised": personalised,
        "comment": comment.strip(),
        "profile": profile,
    }
    existing = []
    if os.path.exists(FEEDBACK_LOG_PATH):
        try:
            with open(FEEDBACK_LOG_PATH, "r") as f:
                existing = json.load(f)
        except Exception:
            existing = []
    existing.append(entry)
    with open(FEEDBACK_LOG_PATH, "w") as f:
        json.dump(existing, f, indent=2)

def chat_with_groq(messages: list) -> str:
    """
    Send the full conversation history to Qwen3-32B via Groq and
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
        model="qwen/qwen3-32b",
        messages=groq_messages,
        temperature=0.7
    )
    content = response.choices[0].message.content
    # Qwen3 prepends its chain-of-thought inside <think>…</think> tags.
    # Strip that block so only the final reply reaches the user.
    content = re.sub(r"<think>[\s\S]*?</think>", "", content, flags=re.IGNORECASE).strip()
    return content

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

def youtube_url(query: str) -> str:
    """
    Build a YouTube search URL from an LLM-generated query string.

    The query comes directly from the model's youtube_queries field, so
    it is already optimised for relevance — we just need to URL-encode it.
    """
    import urllib.parse
    return f"https://www.youtube.com/results?search_query={urllib.parse.quote_plus(query)}"

def fetch_nutrition_recipes(nutrition_items: list) -> dict:
    """
    For each nutrition item, search Spoonacular for the top matching recipe
    and return a dict mapping item index → (recipe_title, recipe_url).

    The evidence note (text inside [...]) and parenthetical dosage hints are
    stripped from the item text before searching so the query stays clean.
    Falls back to an empty dict if the API key is missing or a call fails,
    so the rest of the app always renders correctly without recipes.
    """
    api_key = st.secrets.get("SPOONACULAR_API_KEY", "")
    if not api_key:
        return {}

    results = {}
    for i, item in enumerate(nutrition_items):
        # Strip evidence note and parentheticals to get a clean search query
        query = re.sub(r'\[.*?\]', '', item)   # remove [citation]
        query = query.split('(')[0].strip()     # remove (dosage hint)
        try:
            resp = requests.get(
                "https://api.spoonacular.com/recipes/complexSearch",
                params={"query": query, "number": 1, "apiKey": api_key},
                timeout=5
            )
            data = resp.json()
            if data.get("results"):
                r = data["results"][0]
                # Build the Spoonacular recipe page URL from title slug + id
                slug = re.sub(r"[^a-z0-9]+", "-", r["title"].lower()).strip("-")
                url = f"https://spoonacular.com/recipes/{slug}-{r['id']}"
                results[i] = (r["title"], url)
        except Exception:
            pass  # silently skip — recipe button simply won't appear for this item
    return results

CARD_META = {
    "topical":    {"icon": "🌿", "label": "Topical Treatments", "category": "Applied to hair & scalp"},
    "nutrition":  {"icon": "🥑", "label": "Nutrition",          "category": "Foods & drinks"},
    "vitamins":   {"icon": "💊", "label": "Vitamins & Supplements", "category": "Ingestibles"},
    "daily_care": {"icon": "✨", "label": "Daily Care",          "category": "Habits & routines"},
}

def render_remedy_cards(remedy_data: dict, categories: list, youtube_queries: list = None, recipe_links: dict = None):
    """
    Render the remedy plan as a 2-column HTML card grid.

    The number of recommendations per card scales down from 3 to 2 when
    more than 2 categories are selected, keeping the layout balanced and
    avoiding information overload. Amazon links are added for topical and
    vitamins; YouTube tutorial links are added for daily_care items using
    LLM-generated search queries for maximum relevance.
    """
    n_cats = len(categories)
    # Show fewer items per card when more categories are visible
    n_solutions = 3 if n_cats <= 2 else 2
    yt_queries = youtube_queries or []
    recipes = recipe_links or {}

    cards_html = '<div class="remedy-grid">'
    for cat in categories:
        if cat not in remedy_data or cat not in CARD_META:
            continue
        meta = CARD_META[cat]
        items = remedy_data[cat][:n_solutions]
        items_html = ""
        for i, item in enumerate(items):
            items_html += f'<div class="card-item">{item}'
            if cat in ("topical", "vitamins"):
                items_html += f' <a href="{amazon_url(item)}" target="_blank" class="amazon-btn">🛒 Find on Amazon</a>'
            elif cat == "daily_care" and i < len(yt_queries):
                yt = youtube_url(yt_queries[i])
                items_html += f' <a href="{yt}" target="_blank" class="amazon-btn" style="background:#FF0000;">▶ Tutorial</a>'
            elif cat == "nutrition" and i in recipes:
                title, url = recipes[i]
                items_html += f' <a href="{url}" target="_blank" class="amazon-btn" style="background:#2E7D32;">🍽 Recipe</a>'
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
if "feedback_submitted" not in st.session_state:
    st.session_state.feedback_submitted = False

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
                        st.session_state.selected_cats,
                        msg.get("youtube_queries", []),
                        msg.get("recipe_links", {})
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
    # ── Sample Q&A expander ──────────────────────────────────────────────────
    with st.expander("💬 See an example consultation", expanded=False):
        st.markdown("""
**What does a session look like?** Remedy asks three short questions and then generates your plan. Here's a real example:

---

🌿 **Remedy:** Hello! I'm Remedy, your personal hair consultant. To start — what's your biggest hair or scalp concern right now?

**You:** My hair has been breaking a lot lately, especially at the ends. It feels really dry and brittle.

🌿 **Remedy:** Thank you for sharing that. Could you tell me a bit about your hair texture and type — for example, is it fine, medium, or thick? And would you say it's straight, wavy, curly, or coily?

**You:** It's medium thickness and quite curly — probably a 3A or 3B curl pattern.

🌿 **Remedy:** Got it! And finally, what's your main goal — are you focused on stopping the breakage, restoring moisture and softness, or something else?

**You:** Restoring moisture and reducing breakage so my curls look healthy again.

🌿 **Remedy:** *(generates your personalised remedy plan across topical treatments, nutrition, vitamins, and daily care — each backed by evidence)*

---
*Your answers will always produce a plan tailored to your specific concern, texture, and goal — not generic advice.*
        """)

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
            recipe_links = fetch_nutrition_recipes(parsed["remedy"].get("nutrition", []))
            st.session_state.messages.append({
                "role": "assistant",
                "content": "",
                "is_remedy": True,
                "remedy_data": parsed["remedy"],
                "youtube_queries": parsed.get("youtube_queries", []),
                "recipe_links": recipe_links,
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

    # ── Feedback / validation loop ────────────────────────────────────────────
    if not st.session_state.feedback_submitted:
        st.markdown("<div style='max-width:760px; margin: 1.5rem auto 0;'>", unsafe_allow_html=True)
        st.markdown("""
        <div style='background:#E4F0EF; border-radius:16px; padding:1.2rem 1.5rem; border:1px solid #9DBEBB;'>
            <div style='font-family:"Cormorant Garamond",serif; font-size:1.15rem; color:#031926; margin-bottom:0.4rem;'>
                How did we do?
            </div>
            <div style='font-size:0.85rem; color:#468189;'>
                Your feedback helps us understand whether personalised plans work better than generic advice.
            </div>
        </div>
        """, unsafe_allow_html=True)

        with st.form(key="feedback_form"):
            col_a, col_b = st.columns(2)
            with col_a:
                helpful = st.radio(
                    "Was the remedy plan helpful?",
                    options=["Yes", "No"],
                    horizontal=True,
                )
            with col_b:
                personalised = st.radio(
                    "Did it feel personalised to you?",
                    options=["Yes", "No"],
                    horizontal=True,
                )
            comment = st.text_input(
                "Any other thoughts? (optional)",
                placeholder="e.g. 'Loved the citations' or 'Wanted more nutrition options'",
            )
            fb_submitted = st.form_submit_button("Submit feedback →", use_container_width=True)

        if fb_submitted:
            profile = {
                "texture": st.session_state.remedy.get("texture", ""),
                "concern": st.session_state.remedy.get("concern", ""),
                "goal": st.session_state.remedy.get("goal", ""),
            }
            log_feedback(
                helpful=(helpful == "Yes"),
                personalised=(personalised == "Yes"),
                comment=comment,
                profile=profile,
            )
            st.session_state.feedback_submitted = True
            st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)

    else:
        st.markdown("""
        <div style='max-width:760px; margin: 1rem auto 0; background:#E4F0EF; border-radius:16px;
                    padding:1rem 1.5rem; border:1px solid #9DBEBB; text-align:center;
                    font-size:0.9rem; color:#031926;'>
            Thank you for your feedback — it helps us improve every plan. 🌿
        </div>
        """, unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)