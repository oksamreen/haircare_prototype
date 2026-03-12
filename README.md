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
- **LLM:** Llama 3.3 70B via Groq (`groq`)
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
├── requirements.txt         # Dependencies
├── .streamlit/
│   └── secrets.toml         # API key (not committed)
└── .gitignore
```

---

## Notes

- Never commit your API key — `secrets.toml` is listed in `.gitignore`
- This app was built as part of Assignment 2 for the PPDAI course at ESADE

Author
Samreen
