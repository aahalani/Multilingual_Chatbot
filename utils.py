# utils.py

import os
import json
from datetime import datetime
from dotenv import load_dotenv
from pymongo import MongoClient
from langchain.chat_models import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage

import streamlit as st

# Load environment variables
load_dotenv()

# Initialize MongoDB client
MONGO_URL = os.getenv("MONGO_URL")
client = MongoClient(MONGO_URL)
db = client['DB_Dis']

# MongoDB collections
users_collection = db['users']
chat_history_collection = db['chat_history']
submissions_collection = db['submissions']

# System prompt for the chatbot
SYSTEM_PROMPT = "You are a helper chatbot. You are assisting a student with their programming problem."

def init_app():
    """
    Initialize the Streamlit app and check for necessary configurations.
    """
    if not os.getenv("OPENAI_API_KEY"):
        st.error("OPENAI_API_KEY is not set in the environment variables.")
        st.stop()
    st.set_page_config(page_title="Helper Chatbot", page_icon="🤖")

def check_login(username, password):
    """
    Check if the user credentials are valid.

    :param username: The username entered by the user.
    :param password: The password entered by the user.
    :return: True if credentials are valid, False otherwise.
    """
    user = users_collection.find_one({'username': username, 'password': password})
    return user is not None

def register_user(username, password):
    """
    Register a new user in the database.

    :param username: The new user's username.
    :param password: The new user's password.
    :return: User credentials dictionary.
    """
    user_credentials = {
        'username': username,
        'password': password,
        'language': 'Marathi',
        'created_at': datetime.now()
    }
    users_collection.insert_one(user_credentials)
    return user_credentials

def handle_submit(question, code_text):
    """
    Handle the submission of code for a question.

    :param question: The question identifier.
    :param code_text: The code submitted by the user.
    """
    input_data = {
        'user_id': st.session_state['user_id'],
        'question': question,
        'answer': code_text,
        'timestamp': datetime.now()
    }

    # Save submission data to MongoDB
    save_submission(st.session_state['user_id'], input_data)
    st.success("Code submitted successfully!")

def save_submission(user_id, submission_data):
    """
    Save the user's submission to the database.

    :param user_id: The user's ID.
    :param submission_data: The submission data dictionary.
    """
    submissions_collection.update_one(
        {'user_id': user_id, 'question': submission_data['question']},
        {'$set': submission_data},
        upsert=True
    )

def gpt_model(user_input, language, user_id, question):
    """
    Get a response from the GPT model based on user input.

    :param user_input: The user's input message.
    :param language: The language for the output.
    :param user_id: The user's ID.
    :param question: The current question.
    :return: Response from the GPT model.
    """
    update_language_preference(user_id, language)
    question_description = get_question_description(question)
    if language == 'Marathi':
        prompt = f"""
                You are mentoring a student who is trying to solve the following programming problem:\n\"{question_description}\"\n"
                The student will ask questions related to the problem. DO NOT OUTPUT THE SOLUTION OF THE ENTIRE PROBLEM. You can provide hints and suggestions to their questions. If they have questions related to programming concepts, you can answer them by providing snippets of code.\n
                Only provide answers if it is related to the question.\n
                Provide the answer in Marathi\n
                The student's question is: {user_input}
                """
    else:
        prompt = f"""
                You are mentoring a student who is trying to solve the following programming problem:\n\"{question_description}\"\n
                The student will ask questions related to the problem. DO NOT OUTPUT THE SOLUTION OF THE ENTIRE PROBLEM. 
                You can provide hints and suggestions to their questions. If they have questions related to programming concepts, 
                you can answer them by providing snippets of code.\n
                Only provide answers if it is related to the question.\n
                The student's question is: {user_input}
                """

    chat = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0)
    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=prompt)
    ]
    response = chat(messages)
    return response.content

def update_language_preference(username, language):
    """
    Update the user's language preference in the database.

    :param username: The user's username.
    :param language: The selected language.
    """
    users_collection.update_one(
        {'username': username},
        {'$set': {'language': language}},
        upsert=True
    )

def save_chat_history(user_id, chat_history, language):
    """
    Save the user's chat history to the database.

    :param user_id: The user's ID.
    :param chat_history: List of chat messages.
    :param language: The language used in the conversation.
    """
    serialized_chat = serialize_chat_messages(chat_history, language)
    chat_history_collection.update_one(
        {'user_id': user_id},
        {'$set': {'chat_history': serialized_chat}},
        upsert=True
    )

def serialize_chat_messages(chat_history, language):
    """
    Serialize chat messages to a JSON-serializable format with timestamps.

    :param chat_history: List of chat messages.
    :param language: The language used in the conversation.
    :return: Serialized list of messages.
    """
    serialized_messages = []
    for message in chat_history:
        serialized_messages.append({
            'type': message['type'],
            'content': message['content'],
            'timestamp': datetime.now(),
            'language': language
        })
    return serialized_messages

def get_question_description(question_key):
    """
    Retrieve the description for a given question.

    :param question_key: The question identifier.
    :return: The question description string.
    """
    question_descriptions = {
        "Question 1": "Calculating Virus Spread...",
        "Question 2": "Eating Gems...",
        "Question 3": "Restroom Stall Occupancy Problem..."
    }
    return question_descriptions.get(question_key, "Question not found.")

def get_latest_submission(user_id, question):
    """
    Retrieve the latest submission for a user and question.

    :param user_id: The user's ID.
    :param question: The question identifier.
    :return: The latest submission data or None.
    """
    submission = submissions_collection.find_one(
        {'user_id': user_id, 'question': question},
        sort=[('timestamp', -1)]
    )
    return submission

def display_question_images(question_key):
    """
    Display images related to the question instead of text descriptions.

    :param question_key: The question identifier.
    """
    if question_key == "Question 1":
        st.image("./question_images/q1_1.png")
        st.image("./question_images/q1_2.png")
    elif question_key == "Question 2":
        st.image("./question_images/q2_1.png")
        st.image("./question_images/q2_2.png")
        st.image("./question_images/q2_3.png")
    elif question_key == "Question 3":
        st.image("./question_images/q3.png")
    else:
        st.write("Question images not found.")
