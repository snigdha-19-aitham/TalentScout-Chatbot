import streamlit as st
from prompts import *
from model_interface import ask_llm
import random
from textblob import TextBlob

# Constants
MAX_QUESTIONS = 5
MIN_QUESTIONS = 3
TECH_STACK_HELP = """List your primary technologies in order of proficiency (e.g., Python, Django, PostgreSQL, AWS).
Separate with commas and specify frameworks/libraries where relevant."""

# 🎨 Page setup and custom styling
st.set_page_config(page_title="TalentScout AI Interviewer", page_icon="🤖")
st.markdown("""
    <style>
        .stTextInput, .stTextArea, .stSelectbox, .stButton > button {
            border-radius: 8px;
            padding: 10px;
            font-size: 16px;
        }
        .title {
            color: #003566;
            font-size: 36px;
            font-weight: bold;
            text-align: center;
            margin-bottom: 20px;
        }
        .question-card {
            background-color: #f8f9fa;
            padding: 15px;
            border-radius: 10px;
            margin: 15px 0;
            border-left: 4px solid #003566;
        }
        .progress-bar {
            margin: 20px 0;
            height: 8px;
            background-color: #e9ecef;
            border-radius: 4px;
        }
        .progress {
            height: 100%;
            background-color: #003566;
            border-radius: 4px;
            transition: width 0.5s;
        }
    </style>
""", unsafe_allow_html=True)

def init_session():
    defaults = {
        'step': 'start',
        'user_data': {},
        'base_questions': [],
        'followup_questions': [],
        'answers': [],
        'current_tech_focus': None,
        'q_index': 0,
        'sentiments': [],
        'completed': False
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

def reset_session():
    for key in ['base_questions', 'followup_questions', 'answers', 
                'current_tech_focus', 'q_index', 'user_data', 
                'step', 'sentiments', 'completed']:
        st.session_state.pop(key, None)

def analyze_answer(answer: str) -> dict:
    """Analyze answer quality and content"""
    blob = TextBlob(answer)
    word_count = len(answer.split())
    tech_mentions = sum(1 for tech in st.session_state.user_data['tech_stack'].split(',') 
                       if tech.lower() in answer.lower())
    
    return {
        'sentiment': blob.sentiment.polarity,
        'word_count': word_count,
        'tech_mentions': tech_mentions,
        'needs_followup': word_count < 30 or tech_mentions == 0
    }

def generate_tech_questions(tech_stack: str, role: str, experience: str) -> list:
    """Generate adaptive technical questions based on role and experience level"""
    prompt = f"""
Generate technical screening questions for a {experience}-level {role} candidate with these skills: {tech_stack}

Requirements:
1. Generate 3-5 questions total
2. Include at least one question per major technology
3. Vary question types:
   - Practical implementation
   - Problem-solving scenarios
   - Technology comparisons
4. Adjust difficulty based on experience level:
   - Junior: Focus on fundamentals
   - Mid-level: Include optimization questions
   - Senior: Include architectural decisions
5. Format as a bulleted list without numbering

Example Questions:
- How would you implement [feature] using [technology]?
- Describe your approach to [common challenge] in [technology]
- Compare [technology A] and [technology B] for [use case]

Generated Questions:
"""
    try:
        response = ask_llm(prompt)
        questions = [q.strip() for q in response.split('\n') if q.strip() and '?' in q]
        return questions[:MAX_QUESTIONS]
    except Exception:
        # Fallback questions
        primary_tech = tech_stack.split(',')[0].strip()
        return [
            f"Describe your experience with {primary_tech} in {role} projects",
            "Explain a challenging technical problem you've solved",
            f"How would you approach a {role}-specific problem using {primary_tech}?"
        ]

def generate_followup(question: str, answer: str, tech_stack: str) -> str:
    """Generate context-aware follow-up question"""
    prompt = f"""
Original Question: {question}
Candidate Answer: {answer}
Tech Stack: {tech_stack}

Generate ONE follow-up question that:
1. Probes deeper into a technical aspect mentioned
2. Requests specific examples if answer was vague
3. Explores related technologies in their stack
4. Is concise and directly relevant

Return ONLY the question or EMPTY if no good follow-up exists.
"""
    try:
        response = ask_llm(prompt).strip()
        return response if response and len(response) > 15 and '?' in response else ""
    except Exception:
        return ""

def get_current_question():
    """Get the next question with tech context"""
    if st.session_state.q_index < len(st.session_state.base_questions):
        return st.session_state.base_questions[st.session_state.q_index]
    return st.session_state.followup_questions[
        st.session_state.q_index - len(st.session_state.base_questions)
    ]

# 🚦 Initialize session
init_session()

# 🏩 App Header
st.markdown("<h1 class='title'>💼 TalentScout AI Interviewer</h1>", unsafe_allow_html=True)

# Calculate progress safely
if st.session_state.step == 'generate_questions':
    total_questions = len(st.session_state.base_questions) + len(st.session_state.followup_questions)
    progress = min(100, st.session_state.q_index * 100 // total_questions) if total_questions > 0 else 0
else:
    progress = 0

st.markdown(f"""
<div class='progress-bar'>
    <div class='progress' style='width: {progress}%'></div>
</div>
""", unsafe_allow_html=True)

# 🟢 Step 1: Start Screen
if st.session_state.step == 'start':
    st.info("👋 Welcome to your technical screening! This will take 10-15 minutes with 3-5 questions about your tech stack.")
    if st.button("🚀 Begin Interview"):
        st.session_state.step = 'collect_info'
        st.rerun()

# 🟢 Step 2: Collect Candidate Info
elif st.session_state.step == 'collect_info':
    st.subheader("👤 Candidate Profile")
    with st.form("candidate_form"):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("🧑‍💼 Full Name *")
            email = st.text_input("📧 Email *")
            phone = st.text_input("📱 Phone *")
        with col2:
            location = st.text_input("📍 Location (City, Country) *")
            exp = st.selectbox("💼 Years of Experience *", 
                            ["Select", "0-2", "3-5", "6-8", "9+"])
            position = st.text_input("🎯 Desired Position *")

        stack = st.text_area("🛠️ Tech Stack *", 
                          placeholder="Python, React, PostgreSQL, AWS...",
                          help=TECH_STACK_HELP)
        
        submitted = st.form_submit_button("✅ Continue to Technical Questions")

        if submitted:
            if not all([name.strip(), email.strip(), phone.strip(), location.strip(),
                       exp != "Select", position.strip(), stack.strip()]):
                st.error("⚠️ Please complete all required fields")
            else:
                st.session_state.user_data = {
                    "name": name,
                    "email": email,
                    "phone": phone,
                    "location": location,
                    "experience": exp,
                    "position": position,
                    "tech_stack": stack
                }
                st.session_state.step = 'generate_questions'
                st.rerun()

# 🟢 Step 3: Technical Screening
elif st.session_state.step == 'generate_questions':
    # Generate base questions if none exist
    if not st.session_state.base_questions:
        with st.spinner("🔍 Analyzing your tech stack and preparing questions..."):
            st.session_state.base_questions = generate_tech_questions(
                tech_stack=st.session_state.user_data['tech_stack'],
                role=st.session_state.user_data['position'],
                experience=st.session_state.user_data['experience']
            )
            st.session_state.current_tech_focus = (
                st.session_state.user_data['tech_stack'].split(',')[0].strip()
            )
    
    # Conduct interview
    if not st.session_state.completed:
        total_questions = len(st.session_state.base_questions) + len(st.session_state.followup_questions)
        
        # Update progress
        progress = min(100, st.session_state.q_index * 100 // total_questions) if total_questions > 0 else 0
        st.markdown(f"""
        <div class='progress-bar'>
            <div class='progress' style='width: {progress}%'></div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.session_state.q_index < total_questions:
            question = get_current_question()
            
            with st.container():
                st.markdown(f"""
                <div class="question-card">
                    <strong>Question {st.session_state.q_index + 1}:</strong> {question}
                    {f"<br><small>Focus: {st.session_state.current_tech_focus}</small>" if st.session_state.current_tech_focus else ""}
                </div>
                """, unsafe_allow_html=True)
                
                answer = st.text_area("Your Answer:", key=f"ans_{st.session_state.q_index}",
                                   height=150, placeholder="Be specific about your experience...")
                
                if st.button("Submit Answer"):
                    if not answer.strip():
                        st.warning("Please provide an answer before continuing")
                    else:
                        # Analyze and store response
                        analysis = analyze_answer(answer)
                        st.session_state.answers.append(answer)
                        st.session_state.sentiments.append(analysis['sentiment'])
                        
                        # Generate follow-up if needed
                        if (analysis['needs_followup'] and 
                            len(st.session_state.answers) < MAX_QUESTIONS - 1):
                            followup = generate_followup(
                                question, answer,
                                st.session_state.user_data['tech_stack']
                            )
                            if followup:
                                st.session_state.followup_questions.append(followup)
                        
                        # Move to next question or complete
                        st.session_state.q_index += 1
                        if (len(st.session_state.answers) >= MIN_QUESTIONS and 
                            not analysis['needs_followup']) or len(st.session_state.answers) >= MAX_QUESTIONS:
                            st.session_state.completed = True
                        st.rerun()
        else:
            st.session_state.completed = True
            st.rerun()
    else:
        st.session_state.step = 'end'
        st.rerun()

# 🟢 Step 4: Completion
elif st.session_state.step == 'end':
    st.balloons()
    name = st.session_state.user_data.get('name', 'Candidate')
    
    st.markdown(f"""
    ## 🎉 Screening Complete, {name}!
    Thank you for completing the technical assessment.
    """)
    
    # Calculate performance metrics
    if st.session_state.sentiments:
        avg_sentiment = sum(st.session_state.sentiments)/len(st.session_state.sentiments)
        tech_mention_avg = sum(
            analyze_answer(ans)['tech_mentions'] 
            for ans in st.session_state.answers
        ) / len(st.session_state.answers)
        
        feedback = []
        if avg_sentiment > 0.3:
            feedback.append("Your responses showed strong confidence and positivity.")
        if tech_mention_avg > 1:
            feedback.append("You effectively referenced your technical skills.")
        if len(st.session_state.answers) >= MIN_QUESTIONS:
            feedback.append(f"You provided comprehensive answers to all {len(st.session_state.answers)} questions.")
        
        if feedback:
            st.info("💡 " + " ".join(feedback))
    
    st.markdown(f"""
    ### 📨 Next Steps:
    - We'll review your technical responses
    - Our team will contact you at **{st.session_state.user_data.get('email', 'your email')}**
    - Expect feedback within 3-5 business days
    """)
    
    if st.button("🔄 Start New Interview"):
        reset_session()
        st.rerun()