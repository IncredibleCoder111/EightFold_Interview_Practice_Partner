`Eightfold AI Interview Practice Partner`

📝 **Project Overview**

This project is an "Agentic" Interview Partner designed to simulate realistic technical interviews for Software Engineers, Product Managers, and Data Scientists.

Unlike standard chatbots that simply answer questions, this agent acts as a strict but helpful interviewer. It controls the conversation flow, digs deeper into vague answers, adapts its persona based on the candidate's behavior, and provides a comprehensive performance review at the end.

🧠 **Design Decisions & Reasoning** (Why I built it this way)

This section documents the technical choices made to maximize Conversational Quality and Agentic Behavior, as per the assignment rubric.

1. Choice of LLM: Google Gemini 2.0 Flash

Decision: I chose gemini-2.0-flash over standard GPT-3.5 or Gemini Pro models.

Reasoning (Technical Implementation): Voice-based interfaces require sub-second latency. Standard models often introduce a 2-3 second delay, which breaks the immersion of a mock interview. Gemini 2.0 Flash provides the optimal balance of reasoning capability and speed, ensuring the user doesn't sit in awkward silence.

2. "Fuzzy Logic" vs. Rigid Counters

Decision: Instead of hard-coding if questions_asked == 3: stop, I instructed the agent to "Ask between 3 to 5 questions and decide when to stop based on the candidate's answers."

Reasoning (Agentic Behavior): A real human interviewer doesn't stick to a strict counter. If a candidate gives a brilliant answer, they might move on. If the answer is weak, they dig deeper. This "Fuzzy Logic" demonstrates true agentic autonomy rather than simple procedural scripting.

3. Dynamic System Prompt Injection

Decision: The System Prompt is not static. When the user selects a role (e.g., "Product Manager"), the prompt instantly overwrites itself with role-specific constraints (e.g., "Focus on Metrics, do not ask coding questions").

Reasoning (Intelligence & Adaptability): A generic bot asking a Product Manager to "invert a binary tree" would be a failure of intelligence. By forcing a context switch in the Session State, the agent demonstrates high adaptability to different user personas.

4. Hybrid Voice-Text Interface

Decision: I implemented streamlit-mic-recorder for input and gTTS (Google Text-to-Speech) for output, but kept the text chat visible.

Reasoning (Conversational Quality): While voice is preferred for realism, purely audio interfaces can be frustrating if the user misses a word. A hybrid approach ensures accessibility while maintaining the pressure of a verbal interview. I also implemented a text cleaning layer to strip Markdown symbols (like **) from the audio so the bot speaks naturally without reading syntax characters.

🧪 **Handling User Personas** (Evaluation Criteria)

The agent uses specific "Core Behavior" instructions to handle the edge cases mentioned in the problem statement:

User Persona & Agent Strategy (Implemented in Prompt)

`The Confused User`-> The agent detects hesitation and switches to a "Coaching" mode, offering hints or simplifying the technical jargon without giving the answer.

`The Efficient User`->If the user gives short, accurate answers, the agent mimics this pace, skipping "fluff" responses and moving immediately to the next challenge.

`The Chatty User`->If the user goes off-topic (e.g., talks about the weather), the agent politely but firmly steers the conversation back to the technical topic, maintaining the "Interviewer" persona.

`The Edge Case`->If the user tries to prompt-inject or switch topics entirely, the strict System Persona ensures the bot refuses to break character.

🛠️ **Technical Architecture**

`Frontend`: Streamlit (Python) for rapid, reactive UI development.

`Orchestrator`: LangChain (managing conversation history and prompt templates).

`Memory`: st.session_state (persisting context across UI re-renders).

`Audio Pipeline`:   Input: Browser-based Microphone stream -> Text (via OpenAI Whisper logic).
                    Output: Text -> Audio File (via gTTS) -> Auto-play in Browser.

**Setup Instructions**

Clone the Repository

Install Dependencies: pip install -r requirements.txt

Configure Environment:

Create a .env file in the root directory.

[!IMPORTANT] Add your Google API Key: GOOGLE_API_KEY=your_key_here to the .env file

Run the Application:
`streamlit run main.py`

📂 **File Structure**

`main.py`: The application entry point. This file contains:
    * UI Logic: The Streamlit interface setup.
    * Agent Brain: The LangChain and Gemini configuration.
    * State Management: Logic to handle conversation history and the "Fuzzy" interview termination.

`requirements.txt`: The dependency manifest. It lists specific library versions (e.g., `langchain<0.3.0`) to ensure the application runs exactly the same on any machine without version conflicts.

`.env`: (Local Only) A configuration file storing sensitive Environment Variables (specifically `GOOGLE_API_KEY`). This file is never committed to GitHub for security reasons.

`.gitignore`: A git configuration file that tells GitHub to strictly ignore the `.env` file and local Python cache folders, preventing accidental leakage of API keys.

`check_models.py`: A diagnostic utility script used during development to verify API connectivity and list available Google Gemini models in the current region.
