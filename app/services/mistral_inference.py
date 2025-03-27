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
        temperature=0.7       # Controls creativity
    )
    return response  # directly returns the text


def apply_prompt_template(
        chat_history: str,
        user_prompt: str, 
        tone: str = "friendly"  # default tone
    ) -> str:
    """
    Convert a raw user prompt into a format that encourages the LLM to 
    consider chat_history and tone when generating its response.
    """
    
    # Tone-specific instructions with more detailed formatting
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
            "style_guide": "Use domain-specific terminology, logical structure, and precise descriptions. Include relevant technical details.",
            "example": "The system architecture implements a three-tier model with the following components:"
        },
        "summary": {
            "description": "concise, focused, and essential",
            "style_guide": "Extract only key information, eliminate redundancy, and prioritize critical points.",
            "example": "Main takeaways: 1) Project deadline extended to June 15, 2) Budget approved for additional resources."
        }
    }
    
    # Get the appropriate tone configuration or use default if not found
    tone = tone.lower()
    tone_config = tone_instructions.get(tone, tone_instructions["friendly"])
    
    # Build a more structured tone instruction
    tone_instruction = f"""
Apply a {tone_config['description']} tone to the response.
Style guidelines:
- {tone_config['style_guide']}
- Maintain consistency with the context and content.
- Preserve all factual information while adapting the presentation style.
Example tone: "{tone_config['example']}"
"""
    
    # Base Mistral instruction format with improved tone integration
    prompt_template = f"""[INST] 
You are a helpful assistant. Your task is to perform the user_prompt on chat_history if it is a command, otherwise just append it:

CHAT HISTORY:
{chat_history}

USER PROMPT:
{user_prompt}

TONE INSTRUCTIONS:
{tone_instruction}

Just return the new chat_history without explanations, do not edit too much of the earlier chat_history. 
Also do not include chat_history at the start of the returned text. Only have the contents of the chat_history after the command is executed or new text is appended.
Do not alter the contents of the chat_history such that it can change context.
[/INST]
"""
    
    return prompt_template


def generate_mistral_response(chat_history: str, user_prompt: str, tone: str = "friendly") -> str:
    """
    Return the resultant chat history of performing user_prompt on chat_history
    """
    formatted_prompt = apply_prompt_template(chat_history, user_prompt, tone)
    return call_llm(llm_client, formatted_prompt)


if __name__ == '__main__':
    # testing prompt template + model inference individually
    chat_history = "Tasks: Submit report, update spreadsheet."
    user_prompt = "In brackets, write high priority after Submit report."
    prompt = apply_prompt_template(chat_history, user_prompt, "professional")
    print(f"prompt: {prompt}")
    response = call_llm(llm_client, prompt)
    print(f"response: {response}")

    # let pipeline do everything
    # print(f"pipeline response: {generate_mistral_response(chat_history, user_prompt, 'technical')}")