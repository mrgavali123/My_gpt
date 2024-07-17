import streamlit as st
import google.generativeai as genai

# Configure the API key
api_key = "AIzaSyDd3pZF_IF3tTg09MsgmKwa9T6GrMkBL6Y"
genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-pro')

# Initialize session state for chat history
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# Set default theme to dark mode with contrasting text colors
st.markdown(
    """
    <style>
    body {
        background-color: #303030;
        color: #f1f1f1;
    }
    .message-user, .message-ai {
        padding: 10px;
        border-radius: 10px;
        margin-bottom: 10px;
    }
    .message-user {
        background-color: #333333;
        color: #ffffff;
        text-align: right;
    }
    .message-ai {
        background-color: #444444;
        color: #ffffff;
        text-align: left;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("MY Generative AI")

# Function to add chat to history
def add_to_chat_history(user_input, response):
    st.session_state.chat_history.append({
        "user_input": user_input,
        "response": response
    })

# Function to check for rule violations
def check_for_violations(user_input):
    # Example rule: no offensive language (simple example)
    offensive_words = ['offensive_word1', 'offensive_word2']  # Add more as needed
    for word in offensive_words:
        if word in user_input.lower():
            return True
    return False

# Display chat history
if st.session_state.chat_history:
    st.write("## Chat History")
    for chat in st.session_state.chat_history:
        st.markdown(f"<div class='message-user'><strong>You:</strong> {chat['user_input']}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='message-ai'><strong>AI:</strong> {chat['response']}</div>", unsafe_allow_html=True)

st.write("## New Chat")

# Form to input and submit user question
with st.form(key='input_form', clear_on_submit=True):
    user_input = st.text_input("Enter your question:", key="user_input")
    submit_button = st.form_submit_button(label="Submit")

    if submit_button and user_input:
        # Check for rule violations
        if check_for_violations(user_input):
            st.error("Your input violates the rules. Please try again with appropriate content.")
        else:
            # Generate content
            try:
                response = model.generate_content(user_input)
                response_text = response.text
            except Exception as e:
                response_text = "The AI is unable to answer your question. Please ask another question."

            # Add to chat history
            add_to_chat_history(user_input, response_text)

            # Rerun to update the chat history
            st.experimental_rerun()

# Option to start a new chat
if st.button("New Chat"):
    st.session_state.chat_history = []
    st.experimental_rerun()
