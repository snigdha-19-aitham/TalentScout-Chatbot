import streamlit as st
from prompts import *
from model_interface import ask_llm
import random
from textblob import TextBlob

# Constants
MAX_QUESTIONS = 5

# 🎨 Page setup and custom styling
st.set_page_config(page_title="TalentScout Chatbot", page_icon="🤖")
st.markdown("""
    <style>
        .stTextInput, .stTextArea, .stSelectbox, .stButton > button {
            background-color: #f0f4f8;
            padding: 10px;
            border-radius: 8px;
            font-size: 16px;
        }
        .title {
            color: #003566;
            font-size: 36px;
            font-weight: bold;
            text-align: center;
        }
        .stForm {
            background-color: #ffffff;
            padding: 20px;
            border-radius: 12px;
            box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
        }
        .stMarkdown h2, .stMarkdown h3 {
            color: #001d3d;
        }
    </style>
""", unsafe_allow_html=True)

def init_session():
    defaults = {
        'step': 'start',
        'user_data': {},
        'questions': [],
        'answers': [],
        'q_index': 0,
        'sentiments': []
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

def reset_session():
    for key in ['questions', 'answers', 'q_index', 'user_data', 'step', 'sentiments']:
        st.session_state.pop(key, None)

def generate_followup(original_question: str, answer: str, tech_stack: str) -> str:
    if not answer.strip() or len(answer.split()) < 3:
        return "Would you mind elaborating a little more on your answer?"

    followup_prompt = f"""
You are a friendly and professional AI hiring assistant helping assess candidates in a conversational way.

Tech Stack: {tech_stack}

Candidate's Answer to the Question:
"{original_question}"
{answer}

Please respond with ONLY a follow-up question that would:
- Clarify or deepen the candidate’s response
- Stay on topic but sound human and natural

If the response is already strong and needs no follow-up, reply with an EMPTY string.
"""
    try:
        response = ask_llm(followup_prompt)
        followup = response.strip()
        return followup if len(followup) > 10 else None
    except Exception:
        return None

# 🚦 Initialize session
init_session()

# 🏩 App Header
st.markdown("<h1 class='title'>💼 TalentScout: AI Hiring Assistant</h1>", unsafe_allow_html=True)
st.markdown("<hr>", unsafe_allow_html=True)

# 🟢 Step 1: Start Screen
if st.session_state.step == 'start':
    st.info("👋 Welcome to TalentScout! I’m your virtual AI assistant. Let’s begin with a few quick questions to tailor your interview experience.")
    if st.button("🚀 Start Interview"):
        st.session_state.step = 'collect_info'
        st.rerun()

# 🟢 Step 2: Collect Candidate Info
elif st.session_state.step == 'collect_info':
    st.subheader("👤 Candidate Information")
    with st.form("candidate_form"):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("🧑‍💼 Full Name *")
            email = st.text_input("📧 Email *")
            phone = st.text_input("📱 Phone *")
        with col2:
            location = st.text_input("📍 Location *")
            exp = st.selectbox("💼 Experience *", ["0-1", "2-3", "4-6", "7+"])
            position = st.text_input("🎯 Desired Position *")

        stack = st.text_area("🛠️ Tech Stack * (e.g., Python, SQL, React)")
        submitted = st.form_submit_button("✅ Submit")

        if submitted:
            if not all([name.strip(), email.strip(), phone.strip(), location.strip(), exp.strip(), position.strip(), stack.strip()]):
                st.error("⚠️ Please fill out all fields marked with an asterisk (*).")
            else:
                st.session_state.user_data = {
                    "name": name,
                    "email": email,
                    "phone": phone,
                    "experience": exp,
                    "position": position,
                    "location": location,
                    "tech_stack": stack
                }
                st.session_state.step = 'generate_questions'
                st.rerun()

# 🟢 Step 3: Generate and Ask Questions
elif st.session_state.step == 'generate_questions':
    st.subheader("🧠 Technical Questions")

    if not st.session_state.questions:
        with st.spinner("Analyzing your tech stack and preparing tailored questions..."):
            try:
                prompt = question_generation_prompt(st.session_state.user_data['tech_stack'])
                response = ask_llm(prompt)

                # Extract only actual questions (exclude headings or intros)
                lines = response.split('\n')
                questions = []

                for line in lines:
                    line = line.strip()
                    if not line or "question" in line.lower():
                        continue
                    if "?" in line:
                        clean = line.lstrip("-•0123456789. ").strip()
                        questions.append(clean)

                if not questions:
                    questions = ["Tell me about a recent project you've worked on."]

                st.session_state.questions = questions
                st.session_state.answers = []
                st.session_state.q_index = 0

            except Exception:
                st.error("⚠️ We encountered an issue preparing your questions. Please try again.")
                if st.button("🔁 Retry"):
                    st.rerun()

    if st.session_state.q_index < len(st.session_state.questions) and len(st.session_state.answers) < MAX_QUESTIONS:
        q = st.session_state.questions[st.session_state.q_index]
        st.markdown(f"**Question {len(st.session_state.answers) + 1}:** {q}")
        answer = st.text_area("Your Answer", key=f"ans_{st.session_state.q_index}")

        if st.button("Next"):
            sentiment_score = TextBlob(answer).sentiment.polarity
            st.session_state.sentiments.append(sentiment_score)
            st.session_state.answers.append(answer)

            followup = generate_followup(q, answer, st.session_state.user_data['tech_stack'])
            should_add_followup = followup and random.random() < 0.6 and len(st.session_state.answers) < MAX_QUESTIONS

            if should_add_followup:
                st.session_state.questions.insert(st.session_state.q_index + 1, followup)

            st.session_state.q_index += 1
            st.rerun()
    else:
        st.session_state.step = 'end'
        st.rerun()

# 🟢 Step 4: Completion Screen
elif st.session_state.step == 'end':
    st.balloons()
    name = st.session_state.user_data.get('name', 'Candidate')
    email = st.session_state.user_data.get('email', 'your email')

    st.markdown("## 🎉 Interview Complete!")
    st.success(f"Thank you for your time, {name}! 🙌")

    avg_sentiment = sum(st.session_state.sentiments) / len(st.session_state.sentiments) if st.session_state.sentiments else 0
    if avg_sentiment > 0.3:
        st.info("You seemed confident and positive! Great job! 🚀")
    elif avg_sentiment < -0.3:
        st.warning("We sensed a bit of hesitation or uncertainty. Remember to highlight your strengths next time! 😊")
    else:
        st.caption("Your tone was quite neutral throughout. Thank you for being thoughtful in your responses.")

    st.markdown(f"""
### 📒 What's Next:
Our recruitment team will carefully review your responses and match your profile with relevant opportunities.  
You’ll hear from us via email at **{email}** within a few days.

In the meantime, keep up the great work and stay curious! 🚀  
""")

    st.markdown("---")
    if st.button("🔁 Start New Interview"):
        reset_session()
        st.rerun()
