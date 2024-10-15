# app.py

import os
import streamlit as st
from dotenv import load_dotenv
from streamlit_chat import message
import streamlit.components.v1 as components

from utils import (
    init_app,
    check_login,
    register_user,
    handle_submit,
    gpt_model,
    save_chat_history,
    get_question_description,
    get_latest_submission,
    display_question_images
)

def main():
    # Initialize the app and load environment variables
    init_app()

    # Sidebar for user authentication
    if 'logged_in' not in st.session_state or not st.session_state['logged_in']:
        # Authentication is handled here
        handle_authentication()
    else:
        # Main application logic is handled here once the user is authenticated
        handle_application_logic()

def handle_authentication():
    st.sidebar.title("Authentication")
    registration_mode = st.sidebar.checkbox("Register a new user")
    if registration_mode:
        # Registration form
        new_username = st.sidebar.text_input("New Username")
        new_password = st.sidebar.text_input("New Password", type="password")
        if st.sidebar.button("Register"):
            if new_username and new_password:
                user_credentials = register_user(new_username, new_password)
                st.sidebar.success("Registration successful. You can now login.")
            else:
                st.sidebar.error("Please enter both username and password.")
    else:
        # Login form
        username = st.sidebar.text_input("Username")
        password = st.sidebar.text_input("Password", type="password")
        if st.sidebar.button("Login"):
            if check_login(username, password):
                st.session_state['logged_in'] = True
                st.session_state['user_id'] = username
                st.experimental_rerun()  # Refresh the page
            else:
                st.sidebar.error("Incorrect username or password.")

def handle_application_logic():
    user_id = st.session_state['user_id']
    key = f"messages_{user_id}"
    if key not in st.session_state:
        st.session_state[key] = []

    st.header(f"Chatbot (User: {user_id})")
    st.sidebar.title("Navigation")

    # Page selection
    page = st.sidebar.radio("Go to", ["Question 1", "Question 2", "Question 3"])

    # Language selection
    language = st.sidebar.selectbox("Output Language for the Chatbot", ['Marathi', 'English'])

    # Display the selected question with images
    display_question(page)

    # Handle code submission
    if st.button("Submit"):
        user_code = st.session_state.get(f"text_area_{page}", "")
        handle_submit(page, user_code)

    # Chatbot interaction
    handle_chatbot_interaction(user_id, key, language, page)

def display_question(question_key):
    # Display the question images
    st.subheader(question_key)
    display_question_images(question_key)

    # Embed the online compiler iframe
    components.html(
        """
        <iframe width="700px" height="500px" src="https://www.programiz.com/c-programming/online-compiler/"></iframe>
        """,
        height=500,
        width=700,
    )

    # Fetch and display the latest submission if any
    user_id = st.session_state['user_id']
    latest_submission = get_latest_submission(user_id, question_key)
    if latest_submission:
        st.text_area("Your previous answer:", value=latest_submission['answer'], height=200, key=f"text_area_{question_key}")
    else:
        st.text_area("Copy Paste your code here and click submit to save it:", key=f"text_area_{question_key}", height=200)

def handle_chatbot_interaction(user_id, key, language, question):
    # Chatbot input and interaction in the sidebar
    with st.sidebar:
        st.markdown("## Chatbot Assistant")

        user_input_key = f"user_input_{user_id}"

        def send_message():
            user_input = st.session_state[user_input_key]
            if user_input:
                # Append user message to session state
                st.session_state[key].append({'type': 'human', 'content': user_input})

                # Get chatbot response
                with st.spinner("Thinking..."):
                    response = gpt_model(user_input, language, user_id, question)

                # Append AI response to session state
                st.session_state[key].append({'type': 'ai', 'content': response})

                # Save chat history
                chat_history = st.session_state.get(key, [])
                save_chat_history(user_id, chat_history, language)

                # Clear user input
                st.session_state[user_input_key] = ""

        st.text_input("Your message:", key=user_input_key, on_change=send_message)

        # Display chat messages in the sidebar with the most recent messages first
        messages = st.session_state.get(key, [])
        reversed_messages = messages[::-1]  # Reverse the list to display recent messages first
        for i, msg in enumerate(reversed_messages):
            if msg['type'] == 'human':
                message(msg['content'], is_user=True, key=f"user_{i}")
            else:
                message(msg['content'], is_user=False, key=f"ai_{i}")

        if st.button("Clear Chat"):
            st.session_state[key] = []

if __name__ == '__main__':
    main()
