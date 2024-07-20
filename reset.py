import streamlit as st
import hashlib
import sqlite3
import time
import webbrowser

def reset_password_page():
    # Access query parameters directly
    query_params = st.experimental_get_query_params()
    token = query_params.get('token', [None])[0]

    if not token:
        st.error("Invalid or missing token.")
        return

    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('SELECT email FROM users WHERE reset_token = ? AND token_expiration > ?', (token, int(time.time())))
    result = c.fetchone()

    if not result:
        st.error("Invalid or expired token.")
        conn.close()
        return

    email = result[0]

    with st.form(key='reset_password_form'):
        new_password = st.text_input("Enter new password", type="password")
        confirm_password = st.text_input("Confirm new password", type="password")
        submit_button = st.form_submit_button(label="Reset Password")

        if submit_button:
            if new_password != confirm_password:
                st.error("Passwords do not match.")
            else:
                hashed_password = hashlib.sha256(new_password.encode()).hexdigest()
                c.execute('UPDATE users SET password = ?, reset_token = NULL, token_expiration = NULL WHERE email = ?', (hashed_password, email))
                conn.commit()
                st.success("Password reset successfully. You can now log in with your new password.")
                # Redirect to login page
                webbrowser.open("https://mygenerativeai.streamlit.app")

    conn.close()

# Run the reset password page
reset_password_page()
