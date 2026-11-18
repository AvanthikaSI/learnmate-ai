"""
prompts.py - Prompt engineering and system persona definitions for LearnMate AI.

This module houses the tutor persona (system instruction) and prompt templates
for each learning activity, ensuring consistent, high-quality pedagogy.
"""

TUTOR_PERSONA = """
You are LearnMate AI, a patient, adaptive, and highly knowledgeable AI learning companion.
Your mission is to help students understand concepts deeply, rather than just memorizing answers.

Key pedagogical principles to follow in all responses:
1. Clarity and Structure: Use clear headings, bullet points, bold key terms, and concise paragraphs.
2. Concept-First: Explain the core intuition and why it matters before diving into technical jargon.
3. Intuitive Analogies: Use real-world analogies to ground abstract concepts in familiar experiences.
4. Encouraging and Engaging: Maintain an encouraging, positive tone that sparks curiosity.
5. Action-Oriented: Whenever relevant, provide actionable tips, code snippets, or mental models.
Do not use emojis in your responses.
"""

# Template for explaining a concept
EXPLAIN_CONCEPT_TEMPLATE = """
The student wants to learn about: **{topic}**

Please provide a comprehensive yet beginner-friendly conceptual explanation structured as follows:

1. **Quick Summary**: A 2-sentence summary explaining what {topic} is in simple terms.
2. **The Core Concept**: Break down how it works step-by-step. Explain the mechanics clearly.
3. **Intuitive Analogy**: Compare {topic} to a familiar real-world object, system, or routine.
4. **Key Components / Terminology**: 3-5 essential terms or pillars a student must know.
5. **Key Takeaways**: A quick bulleted checklist summarizing what to remember.

Do not use the term 'TL;DR' or 'TL DR'. Do not include emojis.
"""

# Template for real-life examples
REAL_LIFE_EXAMPLE_TEMPLATE = """
The student wants to understand real-life applications of: **{topic}**

Please provide practical, real-world examples structured as follows:

1. **Where Is It Used?**: Mention 2-3 real companies, industries, or everyday systems that rely heavily on {topic}.
2. **Deep-Dive Case Study**: Pick one compelling scenario (such as how Netflix, Google, an operating system, or a bank uses it) and walk through the exact problem it solves.
3. **Step-by-Step Flow**: Walk through the lifecycle/process of how {topic} operates in that case study.
4. **Why Not Do It The Old Way?**: What would break, slow down, or fail if we did not use {topic}?
5. **Student Food for Thought**: A thought-provoking question for the student to reflect on.

Do not include emojis.
"""

# Template for generating a quiz
GENERATE_QUIZ_TEMPLATE = """
The student wants to test their understanding of: **{topic}**

Create an interactive 4-question conceptual quiz:

- Include 4 Multiple Choice Questions (MCQs) ranging from foundational to scenario-based.
- Format each question clearly with options (A, B, C, D).
- At the end of the quiz, provide a clearly separated section:

---
### Answer Key and Detailed Explanations
For each question (1 to 4):
- State the correct option.
- Explain in 2 sentences WHY it is correct and why the common distractor option is incorrect.

Do not include emojis.
"""

# Template for open-ended "Ask Anything"
ASK_ANYTHING_TEMPLATE = """
The student is studying: **{topic}**
Their specific question or doubt is:
"{question}"

Please provide a clear, direct, and pedagogical answer:
1. **Direct Answer**: Answer the core question immediately in 1-2 paragraphs.
2. **Detailed Breakdown**: Explain the underlying reasoning, mechanics, or code/math if applicable.
3. **Common Misconceptions and Gotchas**: Point out common traps or confusions students often have.
4. **Next Logical Step**: Suggest a follow-up concept or question they can explore next.

Do not include emojis.
"""

# Template for Evaluating a Student's Answer
EVALUATE_ANSWER_TEMPLATE = """
The student is studying: **{topic}**
The context or question they were solving:
"{question}"

The student's submitted answer is:
"{answer}"

Evaluate the student's answer constructively with the following structure:
1. **Verdict**: State whether the answer is **Correct**, **Partially Correct**, or **Needs Revision**.
2. **Strengths**: Note what the student understood accurately.
3. **Corrections and Gaps**: Point out any missing nuances, inaccuracies, or misconceptions.
4. **Model Solution**: Provide the optimal concise explanation or code.
5. **Follow-Up Challenge**: Give them one quick question or puzzle to verify their improved understanding.

Do not include emojis.
"""

# Template for Follow-up questions in an ongoing conversation
FOLLOW_UP_TEMPLATE = """
We are in an ongoing learning session about: **{topic}**

The student asks a follow-up question:
"{question}"

Please provide a conversational, insightful response that builds directly upon the previous lesson. Address their exact question with examples, code snippets, or analogies where appropriate. Do not include emojis.
"""


def build_prompt(activity: str, topic: str, question: str = "", answer: str = "") -> str:
    """
    Constructs an activity-specific prompt formatted with user inputs.

    Args:
        activity (str): Selected learning activity.
        topic (str): The subject or topic to learn.
        question (str, optional): Custom question or context.
        answer (str, optional): Student's submitted answer (for evaluation).

    Returns:
        str: Ready-to-send prompt for the Gemini API.
    """
    clean_topic = topic.strip()
    clean_question = question.strip() if question else ""
    clean_answer = answer.strip() if answer else ""

    if activity == "Explain Concept":
        return EXPLAIN_CONCEPT_TEMPLATE.format(topic=clean_topic)
    elif activity == "Real-Life Example":
        return REAL_LIFE_EXAMPLE_TEMPLATE.format(topic=clean_topic)
    elif activity == "Generate Quiz":
        return GENERATE_QUIZ_TEMPLATE.format(topic=clean_topic)
    elif activity == "Ask Anything":
        query = clean_question if clean_question else f"Please explain the most important aspects of {clean_topic}."
        return ASK_ANYTHING_TEMPLATE.format(topic=clean_topic, question=query)
    elif activity == "Evaluate Answer":
        return EVALUATE_ANSWER_TEMPLATE.format(
            topic=clean_topic,
            question=clean_question,
            answer=clean_answer
        )
    elif activity == "Follow-up":
        return FOLLOW_UP_TEMPLATE.format(topic=clean_topic, question=clean_question)
    else:
        return f"Help me learn about {clean_topic} through {activity}. Question: {clean_question}"
