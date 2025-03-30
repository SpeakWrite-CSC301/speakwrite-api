import os
import google.generativeai as genai
import requests

# Replace with your actual access token
access_token = os.getenv("GCLOUD_ACCESS_TOKEN")
model_region = os.getenv("TRAINED_MODEL_LOCATION")
project_id = os.getenv("PROJECT_ID")
endpoint_id = os.getenv("ENDPOINT_ID")


trained_model_url = f"https://{model_region}-aiplatform.googleapis.com/v1/projects/{project_id}/locations/{model_region}/endpoints/{endpoint_id}:generateContent"

headers = {
    "Authorization": f"Bearer {access_token}",
    "Content-Type": "application/json; charset=utf-8"
}


# Configure your API key
gemini_key = os.getenv("GEMINI_KEY")
genai.configure(api_key=gemini_key)  # Replace with your actual API key

# SPEECH REFINEMENT model
speech_refinement_instructions = (
    "You are a smart note-taking assistant. Rewrite the incoming user input in a refined manner, ignoring natural mistakes and filler words, like 'sorry', 'uh' or 'hmm'. You may paraphrase the text slightly, but make sure it maintains the intended meaning and relevant word choices."
    "Append the refined text to the total text provided, returning the updated total text  with no commentary. You may append it as a new sentence, or attach it to the previous sentence if it seems appropriate. If you don't hear any speech, then return an empty string. The user input will include tone and style guidelines."
)
speech_refine_model = genai.GenerativeModel(
    'gemini-2.0-flash',
    system_instructions = speech_refinement_instructions
)


# COMMAND CLASSIFICATION model
cmd_classification_instructions = "Classify the user input as [speech, command]. Only return the exact lowercase word representing the classification."
cmd_classification_model = genai.GenerativeModel(
    'gemini-2.0-flash',
    system_instructions = cmd_classification_instructions
)

def transcribe_speech(user_input, chat_history, tone = "normal"):
    """
    Clean the user's speech and append it to the chat history. Paraphrase the speech
    into the tone, if specified.

    Precondition: user_input represents speech to be transcribed, and not a command.
    """
    tone_instructions = {
        "normal": {
            "description": "exact, refined, and definite",
            "style_guide": "Exactly what the user said, but without filler words",
            "example": "I have put together some notes about the project we discussed."
        },
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
            "style_guide": "Use domain-specific terminology, logical structure, and precise descriptions. Include relevant technical details. You may use bullet points and similar structures if needed.",
            "example": "The system architecture implements a three-tier model with the following components:"
        },
        "summary": {
            "description": "concise, focused, and essential",
            "style_guide": "Extract only key information, eliminate redundancy, and prioritize critical points.",
            "example": "Main takeaways: 1) Project deadline extended to June 15, 2) Budget approved for additional resources."
        }
    }

    # rectify unrecognized tones
    tone_data = tone_instructions.get(tone, {})
    tone_description = tone_data.get("description", "None")
    tone_style_guide = tone_data.get("style_guide", "None")
    tone_example = tone_data.get("example", "None")

    try:
        response = speech_refine_model.generate_content([
            f"Total text: {chat_history}",
            f"User input: {user_input}",
            "Adhere to the following tone guidelines when transcribing new text or making any changes:\n"
            f"Selected tone: {tone}\n"
            f"Tone description: {tone_description}\n"
            f"Style guide: {tone_style_guide}\n"
            f"Example: {tone_example}\n\n"  # example to enable few-shot learning
        ])
        return response.text.strip()
    except Exception as e:
        print(f"Transcription error: {e}")
        return chat_history


def execute_command(user_input, chat_history, max_chat_len = 1_000):
    system_message = (
        "You are a smart text-editing assistant. If the User input is a text-editing command, apply it to the chat history provided "
        "and return the updated chat history after performing the command (with no explanations and no commentary). If the command is not possible, leave the chat history as is."
    )

    payload = {
        "systemInstruction": {"role": "system", "parts": [{"text": system_message}]},
        "contents": [
            {"role": "user", "parts": [
                {"text": f"User input: {user_input}"},
                {"text": f"Chat history: {chat_history}"}
            ]}
        ],
        "generation_config": {
            "temperature": 1,
            "topP": 0.5,
            "topK": 3,
            "maxOutputTokens": max_chat_len
        }
    }

    try:
        response = requests.post(trained_model_url, headers=headers, json=payload)
        response_json = response.json()
        return response_json.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "No response").strip()
    except Exception as e:
        print(f"Execution error: {e}")
        return chat_history


def classify_input(chat_history, user_input, tone="normal"):
    """
    Sends audio to Gemini and returns the text response.
    """
    try:
        response = cmd_classification_model.generate_content([
            f"User input: {user_input}"
        ])
        classification = response.text.lower().strip()
    except Exception as e:
        print(f"Classification error: {e}")
        classification = "speech"  # default to speech if something goes wrong

    if classification == "command":
        chat_history = execute_command(user_input, chat_history)
    elif classification == "speech":
        chat_history += " " + transcribe_speech(user_input, chat_history, tone)

    return chat_history


if __name__ == "__main__":
    # exemplar lecture script on 3D videogame development
    chat_history = (
        # starts with well-flowing sentences and points

        "Welcome everyone to today’s lecture on 3D videogame development. In this session, "
        "we will explore the fundamental concepts that are essential for creating immersive, interactive 3D worlds. "
        "We will begin by discussing the basics of 3D modeling, including the creation of meshes, textures, and materials. "
        "These elements form the visual foundation of any 3D game, and understanding them is crucial for effective design. "
        "Next, we will examine the principles of animation, which bring these static models to life. "
        "Through keyframing and skeletal rigging, characters and objects are animated to interact with the game environment in realistic ways. "
        "We will also dive into the physics engines that simulate realistic motion and collisions, creating a believable world for the players. "
        "The integration of artificial intelligence in NPC behavior and dynamic world events will be highlighted as well, showcasing the interplay between programming and creativity. "
        "Furthermore, we will cover game engines such as Unity and Unreal Engine, exploring how they streamline development through built-in tools and asset libraries. "
        "By understanding the core architecture of these engines, developers can harness their power to build games more efficiently and creatively. "
        "We will discuss optimization techniques that ensure games run smoothly on various hardware platforms and examine common pitfalls and debugging strategies. "
        "As we move toward the end of the lecture, consider how these concepts interrelate to form a complete development pipeline. "
        "Game development pipelines are complex. They require integration of various modules. Some parts need coordination. "
        
        # very rough notes start here

        "Systems fail without understanding. Code errors make issues worse. Projects face deadlines badly. "
        "Graphics, physics, and AI mix badly. NVIDIA has made some progress though. Problems like feedback loops not connecting properly. Tools work like broken bridges. "
        "Procedures end abruptly. Design notes float, disconnected. Errors and fixes mix with unsteady thoughts."
    )
    
    user_input = "Please refine and improve the flow of the sentences in the last paragraph."
    print(f"\nNEW CHAT HISTORY:\n\n{classify_input(chat_history, user_input)}")