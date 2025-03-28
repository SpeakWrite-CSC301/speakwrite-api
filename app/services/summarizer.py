import os
import google.generativeai as genai
import requests

# Replace with your actual access token
access_token = os.getenv("GCLOUD_ACCESS_TOKEN")
model_region = os.getenv("TRAINED_MODEL_LOCATION")
project_id = os.getenv("PROJECT_ID")
endpoint_id = os.getenv("ENDPOINT_ID")


url = f"https://{model_region}-aiplatform.googleapis.com/v1/projects/{project_id}/locations/{model_region}/endpoints/{endpoint_id}:generateContent"

headers = {
    "Authorization": f"Bearer {access_token}",
    "Content-Type": "application/json; charset=utf-8"
}


# Configure your API key
gemini_key = os.getenv("GEMINI_KEY")
genai.configure(api_key=gemini_key)  # Replace with your actual API key

# Model Selection
model = genai.GenerativeModel('gemini-2.0-flash')


def transcribe_speech(user_input, file_content, tone):
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
        "You are a transcription assistant. Transcribe the incoming user input in a refined manner, ignoring natural mistakes such as 'sorry' or 'uh' or 'hmm' and "
        "append it to the File content provided below, returning the updated text with no commentary. If you don't hear any speech, then return an empty string.\n\n"
        "Follow the following tone guidelines when transcribing new text or making any changes:\n"
        f"Selected tone: {tone}\n"
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


def execute_command(user_input, file_content):
    payload = {
        "contents": [
            {
                "role": "USER",
                "parts": [
                    { "text": f"User input: {user_input}" },
                    { "text":  "Instruction: You are an advanced text-editing assistant. If the User input is a text-editing command, apply it to the File content provided below and return the updated text (with no explanations and no commentary). If the command is not possible, leave the file content as is.\n\n" }, 
                    { "text": f"File content: {file_content}" }
                ]
                    
            }
        ],
        "generation_config": {
            "temperature":1,
            "topP": 0.5,
            "topK": 3,
            "maxOutputTokens": 100
        }
    }
    try:
        response = requests.post(url, headers=headers, json=payload)
        response_json = response.json()
        print(response_json)
        return response_json.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "No response").strip()
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
        chat_history = execute_command(user_input, chat_history)
    elif classification == "speech":
        chat_history += " " + transcribe_speech(user_input, chat_history, tone = "friendly")
    
    return chat_history


