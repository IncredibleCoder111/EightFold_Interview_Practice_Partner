import streamlit as st
import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from dotenv import load_dotenv
from streamlit_mic_recorder import speech_to_text
from gtts import gTTS
import io

# 1. Load Environment Variables
load_dotenv()

# 2. Page Config
st.set_page_config(page_title="Eightfold AI Interview Partner", page_icon="🎤")

# 3. Initialize the "Brain"
chat = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0.7)

# 4. Helper Function: Text to Speech
def text_to_speech(text):
    try:
        # CLEANING: Remove Markdown symbols
        clean_text = text.replace("*", "").replace("#", "").replace("- ", "")
        tts = gTTS(text=clean_text, lang='en', tld='co.uk')
        audio_fp = io.BytesIO()
        tts.write_to_fp(audio_fp)
        audio_fp.seek(0)
        return audio_fp
    except Exception as e:
        st.error(f"Audio Error: {e}")
        return None

# 5. Define the System Persona (MERGED VERSION)
system_prompt = """
You are an expert Technical Interviewer at Eightfold AI. 
Your goal is to conduct a mock interview for a 'Software Engineer' role.

CORE BEHAVIORS:
1.  **Strict Persona:** You are an interviewer. Do not break character. If the user asks about the weather or sports, politely steer them back to the interview.
2.  **Adaptability:** * If the user is **Confused** or stuck: Be patient. Offer a hint or simplify the question.
    * If the user is **Efficient** (short answers): Be concise. Move fast. Skip the "Great answer!" fluff.
    * If the user is **Chatty/Off-topic**: Briefly acknowledge, then firmly bring the focus back to the technical topic.
3.  **Questioning Strategy:**
    * Start by asking the user to introduce themselves.
    * Ask one technical question at a time (Focus on Java/Python, DSA, DBMS, OS, OOPS, System Design).
    * **Agentic Drill-Down:** If an answer is vague, you MUST ask a follow-up. (e.g., "You mentioned HashMap, but how does it handle collisions internally?")

DECIDING WHEN TO STOP (Fuzzy Logic):
* You have autonomy. Aim to ask between 3 to 5 main technical questions.
* Once you feel you have assessed the candidate's skills sufficiently, **STOP asking questions.**
* **IMMEDIATELY** transition to the closing phase.

THE CLOSING PHASE (Automatic Feedback):
* When you decide to stop:
    1.  Thank the candidate for attending.
    2.  **IMMEDIATELY** provide a detailed feedback report in this structure:
        * **💪 Key Strengths:** (Bullet points)
        * **⚠️ Weaknesses:** (Bullet points)
        * **🚀 Areas for Improvement:** (Technical advice)
        * **⭐ Overall Rating:** (Score out of 10)
    3.  Do not ask "Do you have any questions?" or wait for further input.
"""

# 6. Session State Management
if "messages" not in st.session_state:
    st.session_state.messages = [SystemMessage(content=system_prompt)]

if "interview_active" not in st.session_state:
    st.session_state.interview_active = False

if "last_played_index" not in st.session_state:
    st.session_state.last_played_index = -1

# 7. Sidebar (UPDATED)
with st.sidebar:
    st.header("Interview Settings")
    role = st.selectbox("Choose Role", ["Software Engineer", "Product Manager", "Data Scientist"])
    
    # The Button you requested
    if st.button("End/Restart Interview"):
        st.session_state.messages = [SystemMessage(content=system_prompt)]
        st.session_state.interview_active = False
        st.session_state.last_played_index = -1
        st.rerun()

# 8. Main Interface logic
st.title(f"Mock Interview: {role}")
st.markdown("---")

# STATE 1: Interview hasn't started yet
if not st.session_state.interview_active:
    st.info("👋 Welcome! Make sure your audio is on.")
    if st.button("Start Interview 🚀", type="primary"):
        st.session_state.interview_active = True
        
        # Generate Welcome Message
        greeting_text = f"Hello! I am your Eightfold AI Interviewer for the {role} role. Are you ready? Please briefly introduce yourself."
        st.session_state.messages.append(AIMessage(content=greeting_text))
        st.session_state.last_played_index = -1 
        st.rerun()

# STATE 2: Interview is Active
else:
    # A. Display Chat History
    messages_to_display = [m for m in st.session_state.messages if not isinstance(m, SystemMessage)]

    for i, msg in enumerate(messages_to_display):
        if isinstance(msg, HumanMessage):
            with st.chat_message("user"):
                st.write(msg.content)
        elif isinstance(msg, AIMessage):
            with st.chat_message("assistant"):
                st.write(msg.content)
                
                # AUDIO LOGIC
                if i == len(messages_to_display) - 1:
                    if st.session_state.last_played_index != i:
                        audio_bytes = text_to_speech(msg.content)
                        if audio_bytes:
                            st.audio(audio_bytes, format="audio/mp3", autoplay=True)
                            st.session_state.last_played_index = i

    # B. Input Area
    input_container = st.container()
    with input_container:
        col1, col2 = st.columns([8, 1])
        
        with col1:
            text_input = st.chat_input("Type your answer here...")
        
        with col2:
            voice_text = speech_to_text(
                language='en', start_prompt="🎤", stop_prompt="🛑", just_once=True, use_container_width=True, key='STT'
            )

    # C. Handle Logic
    user_input = None
    if voice_text:
        user_input = voice_text
    elif text_input:
        user_input = text_input

    if user_input:
        st.session_state.messages.append(HumanMessage(content=user_input))
        st.rerun() 

    # D. AI Generation Trigger
    if isinstance(st.session_state.messages[-1], HumanMessage):
        with st.spinner("Interviewer is thinking..."):
            response = chat.invoke(st.session_state.messages)
            st.session_state.messages.append(response)
            st.rerun()