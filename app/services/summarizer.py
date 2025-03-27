import google.generativeai as genai
import pyaudio
import wave
import io
import base64
import time
import collections

# Configure your API key
genai.configure(api_key="AIzaSyBGRMwk2ClenlLEfXIapmIJrvm3Oa5R9OQ")  # Replace with your actual API key

# Model Selection
model = genai.GenerativeModel('gemini-2.0-flash')

# tuned_model = genai.GenerativeModel('projects/749243599936/locations/us-east4/models/7211182195140984832')
# Audio Recording Parameters
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
CHUNK = 1024
WINDOW_SECONDS = 5  # Length of sliding window in seconds
CHUNKS_PER_WINDOW = int(RATE / CHUNK * WINDOW_SECONDS)


def transcribe_speech(audio_base64, file_content):
    prompt = (
        "You are a transcription assistant. Transcribe the incoming audio in a refined manner, ignoring natural mistakes such as 'sorry' or 'uh' or 'hmm' and "
        "append it to the File content provided below, returning the updated text with no commentary. If you don't hear any speech, then return an empty string.\n\n"
        "File content: " + file_content
    )
    try:
        response = model.generate_content([
            {
                "mime_type": "audio/wav",
                "data": audio_base64
            },
            prompt
        ])
        return response.text.strip()
    except Exception as e:
        print(f"Transcription error: {e}")
        return file_content


def execute_command(audio_base64, file_content):
    prompt = (
        "You are an advanced text-editing assistant. "
        "If the audio input is a text-editing command, apply it to the File content provided below "
        "and return the updated text (with no explanations). If the command is not possible, leave as is.\n\n"
        "File content: " + file_content
    )

        # Create the instance payload
    try:
        response = model.generate_content([
            {
                "mime_type": "audio/wav",
                "data": audio_base64
            },
            prompt
        ])
        print(response.text)
        return response.text.strip()
    except Exception as e:
        print(f"Transcription error: {e}")
        return file_content


def classify_input(audio_base64):
    """Sends audio to Gemini and returns the text response."""

    try:
        response = model.generate_content([
            {
                "mime_type": "audio/wav",
                "data": audio_base64
            },
            "Determine if the following audio input is a text-editing command or normal speech. Return only one word: 'command' if it is a text-editing command, or 'speech' if it is normal speech.",
        ])

        classification = response.text.lower()

        print(classification)
        if "command" in classification:
            return "command"
        else:
            return "speech"

    except Exception as e:
        print(f"Classification error: {e}")
        return "speech"  # default to speech if something goes wrong

def sliding_window_record_and_summarize():
    audio = pyaudio.PyAudio()
    stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE,
                        input=True, frames_per_buffer=CHUNK)
    print("Recording continuously with a sliding window...")
    file_content = ""

    # Initialize a deque to act as our sliding window buffer
    buffer = collections.deque(maxlen=CHUNKS_PER_WINDOW)
    last_summary_time = time.time()

    try:
        while True:
            try:
                # Use exception_on_overflow=False to avoid raising an error on overflow
                data = stream.read(CHUNK, exception_on_overflow=False)
            except OSError as e:
                print(f"Warning: {e}")
                continue  # Skip this chunk and continue recording

            buffer.append(data)

            # Perform summarization every WINDOW_SECONDS seconds
            if time.time() - last_summary_time >= WINDOW_SECONDS:
                wav_buffer = io.BytesIO()
                wav_file = wave.open(wav_buffer, 'wb')
                wav_file.setnchannels(CHANNELS)
                wav_file.setsampwidth(audio.get_sample_size(FORMAT))
                wav_file.setframerate(RATE)
                wav_file.writeframes(b''.join(buffer))
                wav_file.close()

                wav_bytes = wav_buffer.getvalue()
                audio_base64 = base64.b64encode(wav_bytes).decode('utf-8')

                classification = classify_input(audio_base64)
                if classification == "command":
                    file_content = execute_command(audio_base64, file_content)
                else:
                    file_content += " " + transcribe_speech(audio_base64, file_content)

                print("File content:", file_content)
                last_summary_time = time.time()
    except KeyboardInterrupt:
        print("Stopping recording...")
    finally:
        try:
            if stream.is_active():
                stream.stop_stream()
        except Exception as e:
            print("Error stopping stream:", e)
        stream.close()
        audio.terminate()

if __name__ == "__main__":
    sliding_window_record_and_summarize()
