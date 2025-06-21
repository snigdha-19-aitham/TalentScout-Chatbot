def greeting_prompt():
    return (
        "Hi 👋 I'm TalentScout, your virtual hiring assistant. "
        "I'll guide you through a short screening. Let's begin!"
    )

def question_generation_prompt(tech_stack):
    return f"""
You are an AI interviewer tasked with generating tailored technical screening questions.

Candidate's Tech Stack: {tech_stack}

Guidelines:
- Generate 3 to 5 relevant technical questions based on the stack.
- Vary difficulty levels: include at least one conceptual, one practical, and one deeper or applied question.
- Avoid overused academic definitions unless the stack is very beginner-level.
- Make questions natural, short, and free of jargon.
- Output only the list of questions. No explanations, no numbering.

Begin:
"""
