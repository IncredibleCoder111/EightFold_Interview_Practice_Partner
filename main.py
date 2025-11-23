import streamlit as st
import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from dotenv import load_dotenv
from streamlit_mic_recorder import speech_to_text
from gtts import gTTS
import io
import re  # Imported for text cleaning

# 1. Load Environment Variables
load_dotenv()

# 2. Page Config
st.set_page_config(page_title="Eightfold AI Interview Partner", page_icon="🎤")

# 3. Initialize the "Brain"
chat = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0.7)

# 4. Helper Function: Text to Speech (Now with Cleaning!)
def text_to_speech(text):
    try:
        # CLEANING STEP: Remove Markdown symbols (*, #, etc) from audio only
        clean_text = text.replace("*", "").replace("#", "").replace("- ", "")
        
        # Use British accent (tld='co.uk') for professional vibe
        tts = gTTS(text=clean_text, lang='en', tld='co.uk')
        audio_fp = io.BytesIO()
        tts.write_to_fp(audio_fp)
        audio_fp.seek(0)
        return audio_fp
    except Exception as e:
        st.error(f"Audio Error: {e}")
        return None

# 5. Define the System Persona
system_prompt = """
You are an expert Technical Interviewer at Eightfold AI. 
Your goal is to conduct a mock interview for a 'Software Engineer' role.

Guidelines:
1. Start by asking the user to introduce themselves.
2. Ask one question at a time.
3. Dig deeper! If the user gives a vague answer, ask a follow-up clarifying question.
4. Be professional but encouraging.
5. If the user says "END INTERVIEW", stop asking questions and provide detailed feedback (Strengths, Weaknesses, Rating /10).
6. Keep your responses concise (under 3 sentences) so the conversation flows naturally.
"""

# 6. Session State Management
if "messages" not in st.session_state:
    st.session_state.messages = [SystemMessage(content=system_prompt)]

if "interview_active" not in st.session_state:
    st.session_state.interview_active = False

if "last_played_index" not in st.session_state:
    st.session_state.last_played_index = -1

# 7. Sidebar
with st.sidebar:
    st.header("Interview Settings")
    role = st.selectbox("Choose Role", ["Software Engineer", "Product Manager", "Data Scientist"])
    
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
        
        # Generate the Welcome Message
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
                st.write(msg.content) # This keeps the bold text on screen
                
                # AUDIO LOGIC
                if i == len(messages_to_display) - 1:
                    if st.session_state.last_played_index != i:
                        # The cleaner is inside text_to_speech function
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
            # Voice Input
            voice_text = speech_to_text(
                language='en',
                start_prompt="🎤",
                stop_prompt="🛑",
                just_once=True,
                use_container_width=True,
                key='STT'
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