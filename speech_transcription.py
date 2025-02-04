"""
Speech Transcription system:

- recognize_speech() to listen with default Microphone
- generate_response() to generate SLM response to recognized speech
- main() calls each method alternatively to simulate a conversation in the console (STRICTLY FOR DEMO PURPOSES)
"""

import os
import speech_recognition as sr
from transformers import AutoModelForCausalLM, AutoModelForSeq2SeqLM, AutoTokenizer
import torch

# avoid logging about parallelism (not sure what it is)
os.environ["TOKENIZERS_PARALLELISM"] = "false"

# select device
device = 'cuda' if torch.cuda.is_available() else 'mps' if torch.backends.mps.is_available() else 'cpu'
print(f"Using device: {device}")

# load the Hugging Face model + tokenizer

# models to try (none are working for me except Dialo)
model_options = [
    "microsoft/DialoGPT-medium",  # SLM with 355M parameters
    "facebook/blenderbot-1B-distill",
    "microsoft/GODEL-v1_1-large-seq2seq",  # knowledge-aware
    "mistralai/Mistral-7B-Instruct",  # a better small LLM for rewriting
    "t5-small",  # good for prompt eng
    "google/flan-t5-small",  # instruction-tuned
]
model_name = "google/flan-t5-large"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSeq2SeqLM.from_pretrained(model_name).to(device)
#model = AutoModelForCausalLM.from_pretrained(model_name)

# initialize Speech Recognizer
recognizer = sr.Recognizer()

def recognize_speech(mic_index: int = None, timeout: float = 10.0) -> str | None:
    """
    Capture speech input from a specified Microphone and return the transcribed text.

    Parameters:
    - mic_index (int | None): Index of the microphone to use. Defaults to the system default.
    - timeout (float): Maximum time (in seconds) to wait for speech input. Defaults to 10.0.

    Returns:
    - str | None: The recognized text or None if recognition fails.
    """
    with sr.Microphone(device_index=mic_index) as source:
        print("Listening...")
        recognizer.adjust_for_ambient_noise(source)
        try:
            audio = recognizer.listen(source, timeout=timeout)  # get audio (sr.AudioData object)
            text = recognizer.recognize_google(audio)  # convert audio to text (str if successful)
            return text
        
        # error cases
        except sr.UnknownValueError:
            print("Sorry, I didn't understand that.")
        except sr.RequestError as e:
            print(f"Could not request results from Google Speech Recognition service; {e}")
        except sr.WaitTimeoutError:
            print("No input detected. Please try again.")
        return None


def generate_response(input_text: str, chat_history_ids=None, tone: str = "friendly_casual"):
    """
    Generate model's response to the input text.
    """
    prompt_templates = {
    "friendly_casual": "Rewrite this in a friendly, casual tone:\n{TRANSCRIBED_TEXT}",
    "professional": "Rewrite this into well-organized, professional tone:\n{TRANSCRIBED_TEXT}",
    "technical": "Convert this into a clear, detailed, technical tone:\n{TRANSCRIBED_TEXT}",
    "summary_brief": "Summarize the key points from this tone:\n{TRANSCRIBED_TEXT}"
    }

    # add input text to prompt template
    prompt = prompt_templates.get(tone, prompt_templates["friendly_casual"])
    prompt = prompt.format(TRANSCRIBED_TEXT=input_text)

    new_user_input_ids = tokenizer.encode(prompt + tokenizer.eos_token, return_tensors='pt').to(device)
    bot_input_ids = torch.cat([chat_history_ids, new_user_input_ids], dim=-1) if chat_history_ids is not None else new_user_input_ids
    chat_history_ids = model.generate(
        bot_input_ids, 
        max_length=min(500, bot_input_ids.shape[-1] + 100),
        pad_token_id=tokenizer.eos_token_id
    )
    response = tokenizer.decode(chat_history_ids[:, bot_input_ids.shape[-1]:][0], skip_special_tokens=True)
    return response, chat_history_ids


def main():
    print("Start talking! Say 'exit' or 'quit' to end the conversation.")
    chat_history_ids = None
    
    while True:
        # get speech input
        user_input = recognize_speech()
        if user_input:
            print(f"You: {user_input}")
            
            # exit clause
            if user_input.lower() in ["exit", "quit"]:
                print("Conversation ended.")
                break

            # generate and print the model's response
            response, chat_history_ids = generate_response(user_input, chat_history_ids, tone="friendly_casual")
            print(f"Model: {response}")

if __name__ == "__main__":
    main()
