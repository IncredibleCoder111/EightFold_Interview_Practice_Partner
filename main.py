import streamlit as st
# CHANGED: Using Google Gemini now
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from dotenv import load_dotenv
import os

# 1. Load Environment Variables
load_dotenv()

# 2. Page Config
st.set_page_config(page_title="Eightfold AI Interview Partner", page_icon="🎤")

# 3. Initialize the "Brain" (Google Gemini)
# We use 'gemini-1.5-flash' because it is fast and free
try:
    chat = ChatGoogleGenerativeAI(model="gemini-pro", temperature=0.7)
except Exception as e:
    st.error("Error initializing Google Gemini. Check your GOOGLE_API_KEY in the .env file.")
    st.stop()

# 4. Define the System Persona
system_prompt = """
You are an expert Technical Interviewer at Eightfold AI. 
Your goal is to conduct a mock interview for a 'Software Engineer' role.

Guidelines:
1. Start by asking the user to introduce themselves.
2. Ask one question at a time.
3. Dig deeper! If the user gives a vague answer, ask a follow-up clarifying question.
4. Be professional but encouraging.
5. If the user says "END INTERVIEW", stop asking questions and provide detailed feedback (Strengths, Weaknesses, Rating /10).
"""

# 5. Manage Session State (Memory)
if "messages" not in st.session_state:
    st.session_state.messages = [SystemMessage(content=system_prompt)]

# 6. Sidebar
with st.sidebar:
    st.header("Interview Settings")
    role = st.selectbox("Choose Role", ["Software Engineer", "Product Manager", "Data Scientist"])
    if st.button("Clear/Restart"):
        st.session_state.messages = [SystemMessage(content=system_prompt)]
        st.rerun()

# 7. Display Chat History
st.title(f"Mock Interview: {role}")
st.markdown("---")

# Filter out system message for display
messages_to_display = [m for m in st.session_state.messages if not isinstance(m, SystemMessage)]

for msg in messages_to_display:
    if isinstance(msg, HumanMessage):
        with st.chat_message("user"):
            st.write(msg.content)
    elif isinstance(msg, AIMessage):
        with st.chat_message("assistant"):
            st.write(msg.content)

# 8. Handle User Input
user_input = st.chat_input("Type your answer here...")

if user_input:
    # Add user message to state
    st.session_state.messages.append(HumanMessage(content=user_input))
    
    # Display user message immediately
    with st.chat_message("user"):
        st.write(user_input)

    # Generate response
    with st.spinner("Interviewer is thinking..."):
        try:
            response = chat.invoke(st.session_state.messages)
            # Add AI response to state
            st.session_state.messages.append(response)
            # Display AI response
            with st.chat_message("assistant"):
                st.write(response.content)
        except Exception as e:
            st.error(f"An error occurred: {e}")