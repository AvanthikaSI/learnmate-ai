"""
app.py - Main Streamlit Application for LearnMate AI.
"""

import os
import streamlit as st
from dotenv import load_dotenv
from google import genai
from google.genai import types
from google.genai.errors import APIError

import prompts
import database
import exporter

# ---------------------------------------------------------
# Environment & Streamlit Setup
# ---------------------------------------------------------
load_dotenv()

st.set_page_config(
    page_title="LearnMate AI",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize database tables on app startup
database.init_db()

# Initialize session state variables
if "current_session_id" not in st.session_state:
    st.session_state.current_session_id = None
if "editing_session_id" not in st.session_state:
    st.session_state.editing_session_id = None
if "confirm_delete_id" not in st.session_state:
    st.session_state.confirm_delete_id = None

# Default model configuration
DEFAULT_MODEL = "gemini-2.5-flash"


# ---------------------------------------------------------
# Helper Functions: Secrets & Gemini API
# ---------------------------------------------------------
def get_configured_api_key() -> str:
    """
    Retrieves the Gemini API key from environment variables or Streamlit secrets.
    """
    # 1. Check local environment / .env
    env_key = os.getenv("GEMINI_API_KEY", "").strip()
    
    # 2. Check Streamlit cloud secrets (if deployed)
    cloud_key = ""
    try:
        cloud_key = st.secrets.get("GEMINI_API_KEY", "").strip()
    except Exception:
        cloud_key = ""

    candidate_key = env_key or cloud_key
    
    # Check if candidate is a placeholder
    is_placeholder = any(
        marker in candidate_key.lower()
        for marker in ["your_", "placeholder", "key_here", "your_actual_api_key"]
    )
    
    return "" if is_placeholder else candidate_key


def generate_ai_response(
    api_key: str,
    prompt_text: str,
    system_prompt: str,
    history_interactions: list = None,
    model_name: str = DEFAULT_MODEL
) -> str:
    """
    Calls Google GenAI SDK with multi-turn conversation history.
    Specifies api_version='v1beta' to enable system / developer instructions.
    """
    client = genai.Client(
        api_key=api_key,
        http_options=types.HttpOptions(api_version="v1beta")
    )
    contents = []

    # Inject recent conversation history for multi-turn learning context
    if history_interactions:
        recent = history_interactions[-6:]
        for item in recent:
            u_text = item.get("user_prompt", "").strip()
            a_text = item.get("ai_response", "").strip()
            if u_text and a_text:
                contents.append(types.Content(role="user", parts=[types.Part.from_text(text=u_text)]))
                contents.append(types.Content(role="model", parts=[types.Part.from_text(text=a_text)]))

    # Append the new prompt
    contents.append(types.Content(role="user", parts=[types.Part.from_text(text=prompt_text)]))

    try:
        response = client.models.generate_content(
            model=model_name,
            contents=contents,
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                temperature=0.7,
            )
        )
        return response.text
    except APIError as e:
        # Fallback if an endpoint ever restricts system instructions
        if "Developer instruction is not enabled" in str(e):
            fallback_contents = []
            if system_prompt:
                fallback_contents.append(
                    types.Content(role="user", parts=[types.Part.from_text(text=f"[System Instruction]: {system_prompt}")])
                )
                fallback_contents.append(
                    types.Content(role="model", parts=[types.Part.from_text(text="Understood. I will act as LearnMate AI according to these instructions.")])
                )
            fallback_contents.extend(contents)
            response = client.models.generate_content(
                model=model_name,
                contents=fallback_contents,
                config=types.GenerateContentConfig(temperature=0.7)
            )
            return response.text
        raise


# ---------------------------------------------------------
# Sidebar: Navigation & Session History
# ---------------------------------------------------------
active_api_key = get_configured_api_key()

with st.sidebar:
    st.title("LearnMate AI")
    st.caption("AI-Powered Study Companion")

    # Button to start a fresh learning session
    if st.button("New Learning Session", use_container_width=True, type="primary"):
        st.session_state.current_session_id = None
        st.session_state.editing_session_id = None
        st.session_state.confirm_delete_id = None
        st.rerun()

    st.divider()

    # Saved Learning Sessions List
    st.subheader("Saved Sessions")
    all_sessions = database.get_all_sessions()

    if not all_sessions:
        st.caption("No saved sessions yet.")
    else:
        for s in all_sessions:
            s_id = s["id"]
            is_active = (st.session_state.current_session_id == s_id)
            btn_label = f"[Active] {s['title'][:22]}" if is_active else s['title'][:26]
            
            col_open, col_del = st.columns([4, 1])
            with col_open:
                if st.button(btn_label, key=f"session_btn_{s_id}", use_container_width=True):
                    st.session_state.current_session_id = s_id
                    st.session_state.confirm_delete_id = None
                    st.rerun()
            with col_del:
                if st.button("X", key=f"del_btn_{s_id}", help=f"Delete: {s['title']}"):
                    st.session_state.confirm_delete_id = s_id
                    st.rerun()

            # Handle deletion confirmation
            if st.session_state.confirm_delete_id == s_id:
                st.warning(f"Delete '{s['title'][:20]}'?")
                c_yes, c_no = st.columns(2)
                with c_yes:
                    if st.button("Delete", key=f"conf_yes_{s_id}", type="primary"):
                        database.delete_session(s_id)
                        if st.session_state.current_session_id == s_id:
                            st.session_state.current_session_id = None
                        st.session_state.confirm_delete_id = None
                        st.rerun()
                with c_no:
                    if st.button("Cancel", key=f"conf_no_{s_id}"):
                        st.session_state.confirm_delete_id = None
                        st.rerun()


# ---------------------------------------------------------
# Main Panel: Mode A (Active Session) vs Mode B (New Session)
# ---------------------------------------------------------
current_id = st.session_state.current_session_id
current_session = database.get_session(current_id) if current_id else None

# If the session was deleted or does not exist, reset to new session
if current_id and not current_session:
    st.session_state.current_session_id = None
    st.rerun()


# =========================================================
# MODE A: ACTIVE SESSION VIEW (Chronological History & Chat)
# =========================================================
if current_session:
    interactions = database.get_interactions_for_session(current_session["id"])
    
    # Header & Meta Row
    col_title, col_edit = st.columns([4, 1])
    with col_title:
        st.title(current_session["title"])
        st.caption(f"Topic: {current_session['topic']} | Created: {current_session['created_at']} | Interactions: {len(interactions)}")

    with col_edit:
        with st.popover("Rename"):
            new_title = st.text_input("Session Title:", value=current_session["title"])
            if st.button("Save Title"):
                if new_title.strip():
                    database.update_session_title(current_session["id"], new_title)
                    st.rerun()

    # Export Section
    with st.expander("Export Study Notes (Markdown, Text, PDF)", expanded=False):
        exp_col1, exp_col2, exp_col3 = st.columns(3)
        
        # Markdown Export
        md_data = exporter.export_to_markdown(current_session, interactions)
        with exp_col1:
            st.download_button(
                label="Download Markdown (.md)",
                data=md_data,
                file_name=f"learnmate_{current_session['topic'].lower().replace(' ', '_')}.md",
                mime="text/markdown",
                use_container_width=True
            )
        
        # Text Export
        txt_data = exporter.export_to_txt(current_session, interactions)
        with exp_col2:
            st.download_button(
                label="Download Plain Text (.txt)",
                data=txt_data,
                file_name=f"learnmate_{current_session['topic'].lower().replace(' ', '_')}.txt",
                mime="text/plain",
                use_container_width=True
            )

        # PDF Export
        pdf_bytes = exporter.export_to_pdf(current_session, interactions)
        with exp_col3:
            st.download_button(
                label="Download PDF (.pdf)",
                data=pdf_bytes,
                file_name=f"learnmate_{current_session['topic'].lower().replace(' ', '_')}.pdf",
                mime="application/pdf",
                use_container_width=True
            )

    st.divider()

    # Render Session Timeline (All Past Interactions)
    if not interactions:
        st.info("No interactions in this session yet. Choose an activity below to get started.")
    else:
        for idx, item in enumerate(interactions, 1):
            act_type = item["activity"]

            with st.container():
                st.markdown(f"#### {idx}. {act_type}")
                st.caption(f"Time: {item['created_at']}")
                
                # Show user query if available
                if item["user_prompt"].strip():
                    st.chat_message("user").markdown(item["user_prompt"])
                
                # Show AI response
                st.chat_message("assistant").markdown(item["ai_response"])
                st.divider()

    # Continue Learning in this Session
    st.subheader("Continue Learning")
    
    tab_activity, tab_followup = st.tabs(["Next Activity", "Follow-up Question"])

    with tab_activity:
        act_col1, act_col2 = st.columns([1, 2])
        with act_col1:
            next_activity = st.selectbox(
                "Choose Next Activity",
                [
                    "Explain Concept",
                    "Real-Life Example",
                    "Generate Quiz",
                    "Ask Anything",
                    "Evaluate Answer"
                ],
                key="next_activity_select"
            )

        act_question = ""
        act_answer = ""
        
        with act_col2:
            if next_activity == "Ask Anything":
                act_question = st.text_input(
                    "Question or doubt:",
                    placeholder="Enter your specific question"
                )
            elif next_activity == "Evaluate Answer":
                act_question = st.text_input(
                    "Question or problem being answered:",
                    placeholder="Enter the question or problem"
                )
                act_answer = st.text_area(
                    "Your Answer to Evaluate:",
                    placeholder="Write your explanation or code here for LearnMate to evaluate",
                    height=100
                )
            else:
                st.write(f"LearnMate will generate a structured {next_activity} for {current_session['topic']}.")

        if st.button("Generate Activity Response", type="primary", key="btn_next_act"):
            if not active_api_key:
                st.error("API Key not found. Please set GEMINI_API_KEY in your .env file.")
            elif next_activity == "Evaluate Answer" and (not act_question.strip() or not act_answer.strip()):
                st.warning("Please provide both the question and your answer for evaluation.")
            else:
                prompt_to_send = prompts.build_prompt(
                    activity=next_activity,
                    topic=current_session["topic"],
                    question=act_question,
                    answer=act_answer
                )
                
                user_record_text = f"Activity: {next_activity}"
                if act_question:
                    user_record_text += f"\nQuestion: {act_question}"
                if act_answer:
                    user_record_text += f"\nMy Answer: {act_answer}"

                with st.spinner("Generating response..."):
                    try:
                        resp = generate_ai_response(
                            api_key=active_api_key,
                            prompt_text=prompt_to_send,
                            system_prompt=prompts.TUTOR_PERSONA,
                            history_interactions=interactions
                        )
                        database.add_interaction(
                            session_id=current_session["id"],
                            activity=next_activity,
                            user_prompt=user_record_text,
                            ai_response=resp
                        )
                        st.success("Activity added.")
                        st.rerun()
                    except APIError as api_err:
                        st.error(f"Gemini API Error: {api_err.message}")
                    except Exception as e:
                        st.error(f"Error: {str(e)}")

    with tab_followup:
        followup_q = st.text_area(
            "Ask a follow-up question or clarification on anything discussed above:",
            placeholder="Enter your follow-up question",
            height=90
        )
        if st.button("Submit Follow-up", type="secondary", key="btn_followup"):
            if not active_api_key:
                st.error("API Key not found. Please set GEMINI_API_KEY in your .env file.")
            elif not followup_q.strip():
                st.warning("Please enter your question first.")
            else:
                prompt_to_send = prompts.build_prompt(
                    activity="Follow-up",
                    topic=current_session["topic"],
                    question=followup_q
                )
                with st.spinner("Generating response..."):
                    try:
                        resp = generate_ai_response(
                            api_key=active_api_key,
                            prompt_text=prompt_to_send,
                            system_prompt=prompts.TUTOR_PERSONA,
                            history_interactions=interactions
                        )
                        database.add_interaction(
                            session_id=current_session["id"],
                            activity="Follow-up",
                            user_prompt=followup_q,
                            ai_response=resp
                        )
                        st.success("Response added to session.")
                        st.rerun()
                    except APIError as api_err:
                        st.error(f"Gemini API Error: {api_err.message}")
                    except Exception as e:
                        st.error(f"Error: {str(e)}")


# =========================================================
# MODE B: CREATE NEW SESSION
# =========================================================
else:
    st.title("LearnMate AI")
    st.caption("AI-guided learning assistant for any topic.")
    st.divider()

    st.subheader("Start a New Learning Session")

    col_topic, col_act = st.columns([2, 1])

    with col_topic:
        new_topic = st.text_input(
            "What topic do you want to learn?",
            placeholder="e.g., Operating Systems Virtual Memory, Dijkstra Algorithm, React Hooks, Kafka..."
        )

    with col_act:
        initial_activity = st.selectbox(
            "Starting Activity",
            [
                "Explain Concept",
                "Real-Life Example",
                "Generate Quiz",
                "Ask Anything",
                "Evaluate Answer"
            ]
        )

    # Contextual inputs
    init_question = ""
    init_answer = ""
    
    if initial_activity == "Ask Anything":
        init_question = st.text_area(
            "What specific question do you have about this topic?",
            placeholder="Enter your question",
            height=100
        )
    elif initial_activity == "Evaluate Answer":
        init_question = st.text_input(
            "What was the question or problem?",
            placeholder="Enter the question or problem"
        )
        init_answer = st.text_area(
            "Your Answer:",
            placeholder="Write your answer here",
            height=100
        )

    if st.button("Start Learning Session", type="primary"):
        if not new_topic.strip():
            st.warning("Please enter a topic first.")
        elif not active_api_key:
            st.error("API Key not found. Please set GEMINI_API_KEY in your .env file.")
        elif initial_activity == "Ask Anything" and not init_question.strip():
            st.warning("Please enter your question.")
        elif initial_activity == "Evaluate Answer" and (not init_question.strip() or not init_answer.strip()):
            st.warning("Please provide both the question and your answer.")
        else:
            # Create session in SQLite
            new_session_id = database.create_session(
                topic=new_topic,
                title=f"{new_topic.strip()} - {initial_activity}"
            )

            # Build prompt
            prompt_to_send = prompts.build_prompt(
                activity=initial_activity,
                topic=new_topic,
                question=init_question,
                answer=init_answer
            )

            user_record_text = f"Activity: {initial_activity}"
            if init_question:
                user_record_text += f"\nQuestion: {init_question}"
            if init_answer:
                user_record_text += f"\nMy Answer: {init_answer}"

            with st.spinner("Generating response..."):
                try:
                    resp = generate_ai_response(
                        api_key=active_api_key,
                        prompt_text=prompt_to_send,
                        system_prompt=prompts.TUTOR_PERSONA
                    )
                    
                    # Save interaction to SQLite
                    database.add_interaction(
                        session_id=new_session_id,
                        activity=initial_activity,
                        user_prompt=user_record_text,
                        ai_response=resp
                    )

                    # Set active session and reload
                    st.session_state.current_session_id = new_session_id
                    st.success("Session created successfully.")
                    st.rerun()

                except APIError as api_err:
                    database.delete_session(new_session_id)
                    st.error(f"Gemini API Error: {api_err.message}")
                except Exception as e:
                    database.delete_session(new_session_id)
                    st.error(f"Error: {str(e)}")
