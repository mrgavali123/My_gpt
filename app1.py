import streamlit as st
import google.generativeai as genai
import hashlib
import sqlite3
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import uuid
import time

# Configure the API key
api_key = "AIzaSyDd3pZF_IF3tTg09MsgmKwa9T6GrMkBL6Y"
genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-pro')

# Initialize session state for chat history and authentication
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'username' not in st.session_state:
    st.session_state.username = ""

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

# Function to initialize the SQLite database
def init_db():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                 username TEXT PRIMARY KEY,
                 password TEXT,
                 email TEXT UNIQUE,
                 reset_token TEXT,
                 token_expiration INTEGER)''')
    conn.commit()
    conn.close()

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

# Function to generate a response from the model with context
def generate_response_with_context(user_input):
    # Create a context string from the chat history
    context = "\n".join([f"User: {chat['user_input']}\nAI: {chat['response']}" for chat in st.session_state.chat_history])
    if context:
        context += f"\nUser: {user_input}\nAI:"
    else:
        context = f"User: {user_input}\nAI:"

    # Generate response using the model with context
    try:
        response = model.generate_content(context)
        response_text = response.text
    except Exception as e:
        response_text = "The AI is unable to answer your question. Please ask another question."
    
    return response_text

# Display chat history
def display_chat_history():
    if st.session_state.chat_history:
        st.write("## Chat History")
        for chat in st.session_state.chat_history:
            st.markdown(f"<div class='message-user'><strong>You:</strong> {chat['user_input']}</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='message-ai'><strong>AI:</strong> {chat['response']}</div>", unsafe_allow_html=True)

# Function to send email
def send_email(to_email, subject, body):
    from_email = "gavalipratik2@gmail.com"
    from_password = "tjnq sxak avym pmmn"

    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(from_email, from_password)
        text = msg.as_string()
        server.sendmail(from_email, to_email, text)
        server.quit()
        return True
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False

# Function for the login page
def login_page():
    st.title("Login")
    with st.form(key='login_form'):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        login_button = st.form_submit_button(label="Login")

        if login_button:
            hashed_password = hashlib.sha256(password.encode()).hexdigest()
            conn = sqlite3.connect('users.db')
            c = conn.cursor()
            c.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, hashed_password))
            if c.fetchone():
                st.session_state.authenticated = True
                st.session_state.username = username
                st.experimental_rerun()
            else:
                st.error("Invalid username or password")
            conn.close()

    # Forgot Password link
    if st.button("Forgot Password"):
        st.session_state.page = "Forgot Password"
        st.experimental_rerun()

# Function for the registration page
def registration_page():
    st.title("Register")
    with st.form(key='registration_form'):
        email = st.text_input("Enter your Email")
        username = st.text_input("Choose a Username")
        password = st.text_input("Choose a Password", type="password")
        confirm_password = st.text_input("Confirm Password", type="password")
        register_button = st.form_submit_button(label="Register")

        if register_button:
            if password != confirm_password:
                st.error("Passwords do not match")
            else:
                hashed_password = hashlib.sha256(password.encode()).hexdigest()
                conn = sqlite3.connect('users.db')
                c = conn.cursor()
                try:
                    c.execute('INSERT INTO users (email, username, password) VALUES (?, ?, ?)', (email, username, hashed_password))
                    conn.commit()
                    st.success("Registration successful! Please log in.")
                except sqlite3.IntegrityError as e:
                    if "UNIQUE constraint failed: users.email" in str(e):
                        st.error("Email already exists")
                    else:
                        st.error("Username already exists")
                conn.close()

# Function for the forgot password page
def forgot_password_page():
    st.title("Forgot Password")
    with st.form(key='forgot_password_form'):
        email = st.text_input("Enter your registered Email")
        submit_button = st.form_submit_button(label="Submit")

        if submit_button:
            conn = sqlite3.connect('users.db')
            c = conn.cursor()

            # Invalidate any existing token for this email
            c.execute('UPDATE users SET reset_token = NULL, token_expiration = NULL WHERE email = ?', (email,))
            conn.commit()

            # Generate a new unique token and its expiration time
            token = str(uuid.uuid4())
            expiration = int(time.time()) + 3600  # Token expires in 1 hour

            # Save the new token and expiration to the database
            c.execute('UPDATE users SET reset_token = ?, token_expiration = ? WHERE email = ?', (token, expiration, email))
            conn.commit()

            c.execute('SELECT username FROM users WHERE email = ?', (email,))
            result = c.fetchone()
            conn.close()

            if result:
                username = result[0]
                reset_link = f"https://mygenerativeairesetpass.streamlit.app/?token={token}"
                subject = "Password Reset Request"
                body = f"Hi {username},\n\nPlease click the link below to reset your password:\n{reset_link}"
                if send_email(email, subject, body):
                    st.success("Password reset link sent successfully! Check your inbox.")
                else:
                    st.error("Failed to send email. Please try again later.")
            else:
                st.error("Email not found in the database.")

# Function for the chatbot page
def chatbot_page():
    st.title(f"Welcome, {st.session_state.username}")
    st.title("MY Generative AI")

    # Display chat history
    display_chat_history()

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
                # Generate content with context
                response_text = generate_response_with_context(user_input)

                # Add to chat history
                add_to_chat_history(user_input, response_text)

                # Rerun to update the chat history
                st.experimental_rerun()

    # Option to start a new chat
    if st.button("New Chat"):
        st.session_state.chat_history = []
        st.experimental_rerun()

    # Logout button
    if st.button("Logout"):
        st.session_state.authenticated = False
        st.session_state.username = ""
        st.experimental_rerun()

# Initialize the database
init_db()

# Main app logic
if st.session_state.authenticated:
    chatbot_page()
else:
    if 'page' not in st.session_state:
        st.session_state.page = "Login"

    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to", ["Login", "Register", "Forgot Password"], index=["Login", "Register", "Forgot Password"].index(st.session_state.page))

    if page == "Login":
        login_page()
    elif page == "Register":
        registration_page()
    elif page == "Forgot Password":
        forgot_password_page()
