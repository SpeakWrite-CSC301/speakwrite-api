import os
from huggingface_hub import InferenceClient
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# define model and API client
repo_id = os.getenv("REPO_ID")
hf_token = os.getenv("HF_TOKEN")

llm_client = InferenceClient(
    model=repo_id,
    timeout=120,
    token=hf_token
)


# function to call Mistral
def call_llm(inference_client: InferenceClient, prompt: str):
    response = inference_client.text_generation(
        prompt,
        max_new_tokens=100,  # adjust as needed
        do_sample=True,      # enables randomness in responses
        temperature=0.7       # Ccntrols creativity
    )
    return response  # directly returns the text


def apply_prompt_template(
        chat_history: str,
        user_prompt: str, 
        tone: str = "friendly"  # default tone changed to "friendly"
    ) -> str:
    """
    Convert a raw user prompt into a format that encourages the LLM to 
    consider chat_history and tone when generating its response.
    """
    
    # Base Mistral instruction format
    base_template = """
    [INST] 
    You are a helpful assistant. Your task is to perform the user_prompt on chat_history if it is a command, otherwise just append it:
    chat_history: {CHAT_HISTORY}
    user_prompt: {COMMAND}
    {TONE_INSTRUCTION}
    Just return the new chat_history without explanations, do not edit too much of the earlier chat_history:
    [/INST]
    """.strip()
    
    # Tone-specific instructions
    tone_instructions = {
        "friendly": "Rewrite the following transcribed text into a set of notes that are friendly and inviting. The style should be relaxed and conversational, using everyday language and a personal touch. Ensure to maintain consistency with context and style. Ensure the final output feels like a friendly conversation rather than a formal report. ",
        "professional": "You are an AI writing assistant. Your task is to convert the following transcription into well-organized, professional notes. The writing should be formal, clear, and polished. Focus on clarity, structure, and a refined tone appropriate for business or academic settings. Ensure to maintain consistency with context and style. Output: Professional notes with a balanced and articulate style.",
        "technical": "Please transform the provided transcription into technical notes that are analytical and methodical. The language should be formal and technical, with a focus on clarity and logical organization. Use technical jargon appropriately to suit the context of the provided text, do not deter from or use ambiguous terms that may confuse the theme of the text. Ensure to maintain consistency with context and style. Ensure that the notes are clear, detailed, and accurately reflect the technical content and context.",
        "Summary": "You are an AI assistant tasked with converting the following transcription into a concise summary. Extract the key points and present them in a brief, clear format. The tone should be succinct, focusing on the most important details without unnecessary elaboration. Ensure to maintain consistency with context and style. Output: A set of summarized notes that capture the essential points in a concise manner."
    }
    
    # Get the appropriate tone instruction or use default if not found
    tone_instruction = tone_instructions.get(tone.lower(), tone_instructions["friendly"])
    
    # Insert into template
    return base_template.format(
        CHAT_HISTORY=chat_history, 
        COMMAND=user_prompt, 
        TONE_INSTRUCTION=f"Use the following tone: {tone_instruction}"
    )
    return mistral_prompt_template.format(CHAT_HISTORY=chat_history, COMMAND=user_prompt)


def generate_mistral_response(chat_history: str, user_prompt: str, tone: str = "casual") -> str:
    """
    Return the resultant chat history of performing user_prompt on chat_history
    """
    formatted_prompt = apply_prompt_template(chat_history, user_prompt, tone)
    return call_llm(llm_client, formatted_prompt)


if __name__ == '__main__':
    # testing prompt template + model inference individually
    chat_history = "Tasks: Submit report, update spreadsheet."
    user_prompt =  "In brackets, write high priority after Submit report."  # "hello"
    prompt = apply_prompt_template(chat_history, user_prompt)
    print(f"prompt: {prompt}")
    response = call_llm(llm_client, prompt)
    print(f"response: {response}")

    # let pipeline do everything
    #print(f"pipeline response: {generate_mistral_response(chat_history, user_prompt)}")