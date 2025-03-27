import os
import google.generativeai as genai

# Configure your API key
gemini_key = os.getenv("GEMINI_KEY")
genai.configure(api_key=gemini_key)  # Replace with your actual API key

# Model Selection
model = genai.GenerativeModel('gemini-2.0-flash')


def transcribe_speech(user_input, file_content):
    prompt = (
        "You are a transcription assistant. Transcribe the incoming user input in a refined manner, ignoring natural mistakes such as 'sorry' or 'uh' or 'hmm' and "
        "append it to the File content provided below, returning the updated text with no commentary. If you don't hear any speech, then return an empty string.\n\n"
        "File content: " + file_content
    )
    try:
        response = model.generate_content([
            f"User input: {user_input}",
            prompt
        ])
        return response.text.strip()
    except Exception as e:
        print(f"Transcription error: {e}")
        return file_content


def execute_command(user_input, file_content):
    prompt = (
        "You are an advanced text-editing assistant. "
        "If the user input is a text-editing command, apply it to the File content provided below "
        "and return the updated text (with no explanations). If the command is not possible, leave as is.\n\n"
        "File content: " + file_content
    )

        # Create the instance payload
    try:
        response = model.generate_content([
            f"User input: {user_input}",
            prompt
        ])
        return response.text.strip()
    except Exception as e:
        print(f"Transcription error: {e}")
        return file_content


def classify_input(chat_history, user_input):
    """Sends audio to Gemini and returns the text response."""
    try:
        response = model.generate_content([
            f"User input: {user_input}"
            "Determine if the following user input is a text-editing command or normal speech. Return only one word: 'command' if it is a text-editing command, or 'speech' if it is normal speech.",
        ])
        classification = response.text.lower().strip()
    except Exception as e:
        print(f"Classification error: {e}")
        classification = "speech"  # default to speech if something goes wrong
    
    if classification == "command":
        chat_history = execute_command(user_input, chat_history)
    elif classification == "speech":
        chat_history += " " + transcribe_speech(user_input, chat_history)
    
    return chat_history


