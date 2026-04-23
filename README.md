# haircare_prototype
Third stage prototype for a personalized hair care consultant.

# 🌿 Remedy Me

**Remedy Me** is a personalised hair care consultant powered by AI. Instead of selecting from dropdowns, you have a natural conversation with an AI consultant called Remedy — it asks about your hair concern, texture, and goal, then builds a fully tailored, evidence-grounded remedy plan just for you.

Live demo: [https://remedyup.streamlit.app/]

---

## What It Does

- Guides you through a short 3-step conversation to understand your hair profile
- Retrieves relevant evidence from a curated knowledge base of 40 hair science paper summaries before generating recommendations
- Generates a personalised, citation-backed remedy plan across four categories: topical treatments, nutrition, vitamins, and daily care
- Links topical and vitamin recommendations directly to Amazon search results
- Links daily care items to hair-type-aware YouTube tutorial searches
- Links nutrition items to real recipes via the Spoonacular API
- Lets you customise which categories you want to see using the sidebar
- Adapts the number of recommendations based on how many categories you select
- Exports your full remedy plan as a downloadable PDF
- Logs your feedback (helpful / personalised / comment) to validate the personalisation hypothesis

---

## What's New in Assignment 3

### 1. RAG System (Retrieval-Augmented Generation)
Rather than relying on the LLM's parametric memory, the app retrieves relevant evidence from a curated knowledge base of 40 hair science paper summaries before generating any recommendations. Each entry is tagged by concern, texture, and goal; the top 6 most relevant chunks are scored and injected into the prompt. This grounds every recommendation in real literature (Panahi et al. 2015, Rushton 2002, Koyama 2016, Patel 2017, etc.).

### 2. Two-Phase Architecture
Phase 1 (Llama 3.3 70B) collects the hair profile cleanly. Phase 2 (Llama 3.3 70B with retrieved context) generates the evidence-grounded remedy plan. Separate prompts make citations traceable and the system more auditable.

### 3. YouTube Tutorial Links
The LLM generates hair-type-aware YouTube search queries per daily care item. These render as Tutorial buttons directly under each daily care recommendation.

### 4. Recipe Links via Spoonacular API
Each nutrition recommendation is paired with a real recipe fetched from the Spoonacular API.

### 5. PDF Export
Users can download their full remedy plan as a formatted PDF including their hair profile, all four remedy categories with citations, and a medical disclaimer.

### 6. Personalisation Feedback Loop
After the remedy is shown, users are asked "Was this helpful?" and "Did it feel personalised?" with an optional comment. Responses are timestamped and logged to `feedback_log.json` alongside the user's hair profile.

### 7. Sample Q&A on Landing Screen
A collapsible expander shows a complete example consultation end-to-end, reducing first-time user confusion.

### 8. Step-by-Step Progress Indicator
An `st.status` component shows live progress during remedy generation (profile analysis → paper retrieval → remedy generation → recipe fetch).

---

## Tech Stack

- **Frontend:** Streamlit
- **LLM:** Llama 3.3 70B via Groq API
- **RAG:** Custom scoring retrieval over `hair_knowledge.json`
- **Recipes:** Spoonacular API
- **PDF:** fpdf2
- **Fonts:** Cormorant Garamond, DM Sans (Google Fonts)

---

## Project Structure

haircare_prototype/
├── haircare_upgrade.py     # Main Streamlit app
├── hair_knowledge.json     # 40-entry hair science knowledge base
├── feedback_log.json       # Logged user feedback (auto-created)
├── requirements.txt
└── README.md

## Key Prompt Engineering Decisions

- One-question-at-a-time prevents the model from front-loading all questions
- Explicit guardrail against filler phrases ("this will help me tailor your plan")
- Phase 2 prompt instructs the model to cite only from retrieved evidence; omit brackets entirely when no paper is available
- Temperature 0.6 for structured JSON generation in Phase 2 (vs 0.7 for conversation)

---

*Remedy Me uses AI to generate personalised suggestions. Always consult a trichologist for medical concerns.*