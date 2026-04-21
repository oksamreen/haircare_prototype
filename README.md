# haircare_prototype
Second stage prototype for a personalized hair care consultant.

# 🌿 Remedy Me

**Remedy Me** is a personalised hair care consultant powered by AI. Instead of selecting from dropdowns, you have a natural conversation with an AI consultant called Remedy — it asks about your hair concern, texture, and goal, then builds a fully tailored remedy plan just for you.

Live demo: [remedizeme.streamlit.app](https://remedizeme.streamlit.app)

---

## What It Does

- Guides you through a short 3-step conversation to understand your hair profile
- Generates a personalised remedy plan across four categories: topical treatments, nutrition, vitamins, and daily care
- Lets you customise which categories you want to see using the sidebar
- Links topical and vitamin recommendations directly to Amazon search results
- Adapts the number of recommendations based on how many categories you select

---

## Tech Stack

- **Frontend:** Streamlit
- **LLM:** Qwen3-32B via Groq (`groq`)
- **Language:** Python

---

## How to Run Locally

**1. Clone the repo**
```bash
git clone https://github.com/oksamreen/haircare_prototype.git
cd haircare_prototype
```

**2. Install dependencies**
```bash
pip install streamlit groq
```

**3. Add your Groq API key**

Create a `.streamlit/secrets.toml` file:
```bash
mkdir .streamlit
echo 'GROQ_API_KEY = "your-key-here"' > .streamlit/secrets.toml
```

Get a free API key at [console.groq.com](https://console.groq.com)

**4. Run the app**
```bash
streamlit run haircare_upgrade.py
```

---

## Project Structure

```
haircare_prototype/
├── haircare_upgrade.py      # Main app
├── feedback_log.json        # Auto-created; stores user feedback entries
├── requirements.txt         # Dependencies
├── .streamlit/
│   └── secrets.toml         # API key (not committed)
└── .gitignore
```

---

## Prompt Engineering Decisions

### System prompt design

The system prompt gives the LLM a persona (`Remedy`) with an explicit role, a bounded conversation structure (3 questions, one at a time), and strict output rules. This three-part structure was a deliberate choice:

1. **One question at a time** — prevents the model from front-loading all questions into a single message, which would feel clinical rather than consultative. Users tested early prototypes and responded better to the conversational pacing.

2. **Guardrails against drift** — the prompt explicitly instructs the model: *"If the user's response does not actually answer your question… do NOT move on. Politely acknowledge and ask the same question again."* This prevents the common failure mode where the LLM infers an answer the user never gave, leading to mismatched recommendations.

3. **Structured JSON output** — once the profile is complete, the model switches modes and outputs a single JSON block. Separating the conversational phase from the output phase (rather than mixing them) makes parsing deterministic. A `regex` fallback extracts the JSON even if the model wraps it in prose.

4. **Evidence-based citations** — each remedy item is required to include a bracketed evidence note (e.g. `[Panahi et al., 2015 — comparable to minoxidil 2%]`). This grounds recommendations in hair science literature rather than generic wellness advice, directly addressing the professor's "narrow domain limits originality" note.

### Why multi-turn over one-shot?

A one-shot approach (e.g. a form where the user fills in all fields) would produce equally structured output, but user testing showed it feels impersonal. The multi-turn design builds rapport and allows the model to ask clarifying follow-ups if an answer is ambiguous — something a static form cannot do.

### Temperature

Set to `0.7` — high enough to produce varied, creative remedy items across sessions, low enough to keep the JSON output structurally consistent. Lower values (e.g. `0.3`) produced repetitive recommendations; higher values (e.g. `1.0`) occasionally broke the JSON schema.

---

## Feedback & Personalisation Validation

After the remedy plan is shown, users are asked:
- *Was the remedy plan helpful?*
- *Did it feel personalised to you?*
- *(Optional)* Any other thoughts?

Responses are timestamped and logged to `feedback_log.json` alongside the user's hair profile (texture, concern, goal). This dataset lets us quantitatively test the hypothesis that personalised recommendations score higher than generic advice — the core claim of the product.

---

## Notes

- Never commit your API key — `secrets.toml` is listed in `.gitignore`
- `feedback_log.json` is auto-created on first feedback submission; it is excluded from the repo via `.gitignore`
- This app was built as part of the PPDAI course at ESADE

Author: Samreen
