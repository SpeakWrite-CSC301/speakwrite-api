"""
Speech Transcription system:

- recognize_speech() to listen with default Microphone
- generate_response() to generate SLM response to recognized speech
- main() calls each method alternatively to simulate a conversation in the console (STRICTLY FOR DEMO PURPOSES)
"""

import speech_recognition as sr
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
import os

# avoid logging about parallelism (not sure what it is)
os.environ["TOKENIZERS_PARALLELISM"] = "false"

# load the Hugging Face model + tokenizer
model_name = "microsoft/DialoGPT-medium"  # SLM with 355M parameters
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name)

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


def generate_response(input_text: str, chat_history_ids=None):
    """
    Generate model's response to the input text.
    """
    new_user_input_ids = tokenizer.encode(input_text + tokenizer.eos_token, return_tensors='pt')
    bot_input_ids = torch.cat([chat_history_ids, new_user_input_ids], dim=-1) if chat_history_ids is not None else new_user_input_ids
    chat_history_ids = model.generate(bot_input_ids, max_length=1000, pad_token_id=tokenizer.eos_token_id)
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
            response, chat_history_ids = generate_response(user_input, chat_history_ids)
            print(f"Model: {response}")

if __name__ == "__main__":
    main()