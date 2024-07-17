import streamlit as st
import google.generativeai as genai

# Configure the API key
api_key = "AIzaSyDd3pZF_IF3tTg09MsgmKwa9T6GrMkBL6Y"
genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-pro')

# Initialize session state for chat history
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

st.title("MY Generative AI")

# Function to add chat to history
def add_to_chat_history(user_input, response):
    st.session_state.chat_history.append({
        "user_input": user_input,
        "response": response
    })

# Display chat history
if st.session_state.chat_history:
    st.write("## Chat History")
    for chat in st.session_state.chat_history:
        st.markdown(f"<div style='text-align: left; color: white;'><strong>You:</strong> {chat['user_input']}</div>", unsafe_allow_html=True)
        print("/n")
        st.markdown(f"<div style='text-align: right; color: white;'><strong>AI:</strong> {chat['response']}</div>", unsafe_allow_html=True)

st.write("## New Chat")

# Form to input and submit user question
with st.form(key='input_form', clear_on_submit=True):
    user_input = st.text_input("Enter your question:", key="user_input")
    submit_button = st.form_submit_button(label="Submit")

    if submit_button and user_input:
        # Generate content
        response = model.generate_content(user_input)
        response_text = response.text

        # Add to chat history
        add_to_chat_history(user_input, response_text)

        # Rerun to update the chat history
        st.experimental_rerun()

# Option to start a new chat
if st.button("New Chat"):
    st.session_state.chat_history = []
    st.experimental_rerun()
