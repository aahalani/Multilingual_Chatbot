# Streamlit AI Chatbot Application

## Overview

This project is a Streamlit application that provides an interactive platform for students to work on programming problems with the assistance of an AI chatbot. The application includes user authentication, code submission features, and an AI assistant that can communicate in both Marathi and English.

## Features

- User authentication
- Code submission
- AI chatbot
- Marathi and English language support

## Installation

1. Clone the repository
2. Install the required packages using the following command:

```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the root directory of the project and add the following environment variables:

```bash
MONGODB_URI=<MongoDB URI>
OPENAI_API_KEY=<OpenAI API>
```

Ensure that you have a MongoDB database set up and an OpenAI API key. Update the collection names in the `utils.py` file.

4. Run the application using the following command:

```bash
streamlit run app.py
```

## Support

If you have any questions or need assistance, please feel free to reach out to me at aahalani@gmail.com, or create an issue in the repository.
