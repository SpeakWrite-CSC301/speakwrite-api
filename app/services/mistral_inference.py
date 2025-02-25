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
        tone: str = "casual"  # not used yet
    ) -> str:
    """
    Convert a raw user prompt into a format that encourages the LLM to 
    consider chat_history and tone when generating its response.
    """
    
    # Mistral instruction format
    mistral_prompt_template = """
    [INST] 
    You are a helpful assistant. Your task is to perform the user_prompt on chat_history if it is a command, otherwise just append it:
    chat_history: {CHAT_HISTORY}
    user_prompt: {COMMAND}
    Just return the new chat_history without explanations:
    [/INST]
    """.strip()

    # request response in specified tone
    #prompt = f"{user_prompt} Rewrite in a {tone} tone."
    
    # insert into Mistral template
    return mistral_prompt_template.format(CHAT_HISTORY=chat_history, COMMAND=user_prompt)


def generate_mistral_response(chat_history: str, user_prompt: str, tone: str = "casual") -> str:
    """
    Return the resultant chat history of performing user_prompt on chat_history
    """
    formatted_prompt = apply_prompt_template(chat_history, user_prompt, tone)
    return call_llm(llm_client, prompt)


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