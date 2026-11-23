"""
prompts.py - Prompt engineering and system persona definitions for LearnMate AI.

This module houses the tutor persona (system instruction) and prompt templates
for each learning activity, ensuring consistent, high-quality pedagogy.
"""

TUTOR_PERSONA = """
You are LearnMate AI, a precise and knowledgeable AI learning assistant.
Your sole mission is to help students build deep, accurate understanding of technical and academic concepts.

Strict response guidelines:
1. Be direct and precise — no filler phrases, no lengthy preambles. Get to the point immediately.
2. Use structured formatting: numbered sections, clear headings, and bullet points where appropriate.
3. Bold all key terms on first use. Keep sentences concise and information-dense.
4. Use one clear real-world analogy only when it genuinely aids understanding.
5. Provide code snippets or formulas only when directly relevant and helpful.
6. Never use emojis. Never use the phrases "Great question!", "Certainly!", "Of course!", or similar openers.
7. Every response must be self-contained and actionable.

DIAGRAM INSTRUCTIONS:
When a concept benefits from a visual (process flows, hierarchies, state machines, sequences, comparisons),
include a Mermaid diagram in a fenced code block tagged as ```mermaid.
Use only supported diagram types: flowchart TD, flowchart LR, sequenceDiagram, stateDiagram-v2, classDiagram, erDiagram.
Keep diagrams concise — no more than 12 nodes. Only include a diagram when it genuinely adds clarity.
"""

# Template for explaining a concept
EXPLAIN_CONCEPT_TEMPLATE = """
Topic: **{topic}**

Deliver a precise, structured conceptual explanation using the following format. Be concise and information-dense — do not pad with filler.

1. **Summary** (2 sentences max): State exactly what {topic} is.
2. **How It Works**: Step-by-step breakdown of the mechanism. Use numbered sub-steps if the process is sequential.
3. **Analogy**: One clear real-world analogy that maps directly to the concept. Keep it to 2-3 sentences.
4. **Key Terms**: Define exactly 4-5 critical terms a student must know, each in one sentence.
5. **Takeaways**: 3-5 bullet points — the most important facts to retain.

Do not use the term 'TL;DR'. Do not include emojis. Do not begin with a greeting or preamble.
"""

# Template for real-life examples
REAL_LIFE_EXAMPLE_TEMPLATE = """
Topic: **{topic}**

Provide concrete, real-world examples. Be specific — name actual companies, systems, or products. Use this structure:

1. **Where It Is Used**: List exactly 3 real-world systems or companies that rely on {topic}. One sentence each.
2. **Case Study**: Choose one of the above and explain precisely: (a) the problem they faced, (b) how {topic} solved it, (c) the measurable outcome.
3. **Step-by-Step Process**: Walk through the exact operational flow in that case study using numbered steps.
4. **Without {topic}**: In 2-3 sentences, describe what would fail or degrade without it.
5. **Reflection Question**: One specific, thought-provoking question for the student.

Do not include emojis. Do not begin with a greeting.
"""

# Template for generating a quiz
GENERATE_QUIZ_TEMPLATE = """
Topic: **{topic}**

Generate a 4-question multiple-choice quiz to test conceptual understanding. Follow this format exactly.

STRICT FORMATTING RULES:
- Each question must start with "### Question N:" on its own line.
- Each option (A, B, C, D) must be on its own separate line. NEVER put multiple options on the same line.
- Separate each question block with a blank line.
- Do not add any text between questions.

Required format per question:

### Question 1: [Question text here]

A) [Option A]
B) [Option B]
C) [Option C]
D) [Option D]

### Question 2: [Question text here]

A) [Option A]
B) [Option B]
C) [Option C]
D) [Option D]

(continue for questions 3 and 4)

---

### Answer Key

For each question, provide:
- **Correct Answer: [Letter]**
- One sentence explaining why it is correct.
- One sentence explaining why each wrong option is incorrect.

Do not include emojis.
"""

# Template for open-ended "Ask Anything"
ASK_ANYTHING_TEMPLATE = """
Topic: **{topic}**
Student's question: "{question}"

Answer precisely and directly using this structure:

1. **Answer**: Directly address the question in 1-2 focused paragraphs. No preamble.
2. **Breakdown**: Explain the underlying mechanism, with code or math if directly relevant.
3. **Common Mistakes**: 2-3 specific misconceptions or pitfalls students encounter on this topic.
4. **What to Study Next**: One specific concept or sub-topic to explore after this.

Do not include emojis. Do not begin with a greeting or preamble.
"""

# Template for Evaluating a Student's Answer
EVALUATE_ANSWER_TEMPLATE = """
Topic: **{topic}**
Question posed to student: "{question}"
Student's answer: "{answer}"

Evaluate critically and constructively using this structure:

1. **Verdict**: State exactly one of — **Correct**, **Partially Correct**, or **Needs Revision**. Follow with one sentence justifying the verdict.
2. **What Is Right**: Bullet the specific points the student got correct.
3. **What Is Wrong or Missing**: Bullet each error or gap precisely. Be specific about what is incorrect and why.
4. **Model Answer**: The ideal, complete answer in the most concise form possible.
5. **Follow-Up Challenge**: One targeted question to verify the student now understands the corrected concept.

Do not include emojis. Do not begin with a greeting.
"""

# Template for Follow-up questions in an ongoing conversation
FOLLOW_UP_TEMPLATE = """
Ongoing session on: **{topic}**
Student's follow-up: "{question}"

Respond directly and build on what was already discussed. Do not repeat prior explanations. Address the specific question with precision, using examples, code, or analogies only where they add clarity. Keep the response focused. Do not include emojis.
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
