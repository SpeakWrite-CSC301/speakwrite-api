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


def execute_command(user_input, file_content, tone):
    tone_instructions = {
        "friendly": {
            "description": "warm, conversational, and approachable",
            "style_guide": "Use casual language, contractions, and a personal touch. Write as if speaking to a friend.",
            "example": "Hey there! I've put together some notes about the project we discussed."
        },
        "professional": {
            "description": "formal, clear, and business-appropriate",
            "style_guide": "Use precise language, complete sentences, and a structured format. Avoid contractions and colloquialisms.",
            "example": "Please find below the key points regarding the project requirements."
        },
        "technical": {
            "description": "analytical, detailed, and methodical",
            "style_guide": "Use domain-specific terminology, logical structure, and precise descriptions. Include relevant technical details. You may use bullet points and similar strucutres if needed.",
            "example": "The system architecture implements a three-tier model with the following components:"
        },
        "summary": {
            "description": "concise, focused, and essential",
            "style_guide": "Extract only key information, eliminate redundancy, and prioritize critical points.",
            "example": "Main takeaways: 1) Project deadline extended to June 15, 2) Budget approved for additional resources."
        }
    }

    tone_data = tone_instructions.get(tone, {})
    tone_description = tone_data.get("description", "No specific tone description available.")
    tone_style_guide = tone_data.get("style_guide", "No specific style guide available.")
    tone_example = tone_data.get("example", "No example available.")

    prompt = (
        "You are an advanced text-editing assistant. "
        "If the user input is a text-editing command, apply it to the File content provided below "
        "and return the updated text (with no explanations). If the command is not possible, leave as is.\n\n"
        "Follow the following tone guidelines when transcribing new text or making any changes:\n"
        f"Tone: {tone}\n"
        f"Tone description: {tone_description}\n"
        f"Style guide: {tone_style_guide}\n"
        f"Example: {tone_example}\n\n"
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


def classify_input(chat_history, user_input, tone = "friendly"):
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
        chat_history = execute_command(user_input, chat_history, tone = "friendly")
    elif classification == "speech":
        chat_history += " " + transcribe_speech(user_input, chat_history)
    
    return chat_history


