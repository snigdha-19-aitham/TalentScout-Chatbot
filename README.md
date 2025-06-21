# 💼 TalentScout: AI Hiring Assistant

TalentScout is an intelligent Streamlit-based chatbot designed to assist in the initial stages of technical hiring. It collects candidate information, generates tech-stack-based technical questions, provides follow-up questions, and performs sentiment analysis — all in a user-friendly interface.

---

## 🧠 Project Overview

TalentScout streamlines the recruitment screening process by:
- Gathering candidate details (name, experience, tech stack, etc.)
- Generating personalized technical questions using an LLM
- Asking contextual follow-up questions
- Performing sentiment analysis to gauge candidate confidence
- Supporting smooth and secure user interaction via an intuitive interface

---

## ⚙️ Installation Instructions

1. **Clone the Repository**
   ```bash
   git clone https://github.com/snigdha-19-aitham/talentscout-chatbot.git
   cd talentscout-chatbot
   ```

2. **Create and Activate a Virtual Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # For Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set API Key (if using OpenRouter or OpenAI)**
   - Add your API key in a `.env` file or modify the `ask_llm()` function to include:
     ```python
     headers = {
         "Authorization": "Bearer YOUR_API_KEY",
         ...
     }
     ```

5. **Run the Application**
   ```bash
   streamlit run app.py
   ```

---

## 🧪 Usage Guide

1. Click “🚀 Start Interview” on the homepage.
2. Fill in all the required candidate information (name, email, experience, tech stack, etc.).
3. The chatbot will generate questions tailored to the provided tech stack.
4. Answer the questions. The bot may ask intelligent follow-up questions.
5. On completion, the system analyzes responses and provides feedback.

---

## 🛠️ Technical Details

- **Framework:** Streamlit
- **Language:** Python 3.10+
- **LLM Backend:** Configurable via `ask_llm()` (OpenAI, OpenRouter, etc.)
- **Libraries Used:**
  - `streamlit` – UI and state management
  - `textblob` – Sentiment analysis
  - `requests` – API interaction
  - `hashlib` – Anonymizing user data
  - `random` – Controlling follow-up probabilities

---

## ✨ Prompt Design

Prompts are stored in a separate `prompts.py` file. Two types of prompts are designed:

- **Information Collection Prompt:** Ensures a natural introduction and sets the context for technical questioning.
- **Technical Question Prompt:** Uses the candidate’s `tech_stack` to generate 3–5 domain-specific questions.
- **Follow-up Question Prompt:** Crafted to sound human and professional, it is triggered when a candidate’s answer is brief or vague.

The prompts are fine-tuned to prevent deviation and maintain interview relevance.

---

## ⚠️ Challenges & Solutions

| Challenge | Solution |
|----------|----------|
| Ensuring follow-up questions were natural | Prompt tuning and checking response length |
| Preventing prompt hallucinations (irrelevant follow-ups) | Added filters for short/irrelevant answers |
| Handling vague or skipped candidate inputs | Introduced a fallback message asking them to elaborate |
| UI limitations in Streamlit | Applied custom CSS for minimal styling and structure |
| Sentiment scoring inconsistency | Used `TextBlob` polarity scoring and averaged results |

---

## 🚀 Future Improvements

- Multilingual support using `langdetect` and translation APIs
- Role-based question generation (frontend, backend, data)
- Admin dashboard to view candidate responses and sentiment trends
- Real-time feedback system
