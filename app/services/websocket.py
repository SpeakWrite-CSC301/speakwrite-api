import uvicorn
import traceback
import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect

# calling methods/functiona from speech_transcription.py
from speech_transcription import recognize_speech, generate_response

app = FastAPI() # create a seperate WebSocket service
ERROR_LOG_FILE = "error.log"

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint that continuously listens to microphone input,
    generates an AI response, and sends it to the client in real time.

    In case of an error, it saves the input text, generated response (if any),
    and error details to a local file.
    """
    await websocket.accept()
    chat_history_ids = None  
    
    try:
        while True:
            # Run the speech recognition in a separate thread, so it doesn't block.
            user_input = await asyncio.to_thread(recognize_speech)
            if user_input:
                print(f"User said: {user_input}")

                if user_input.lower() in ["exit", "quit"]:
                    await websocket.send_json({"type":"content", "data":"Conversation ended."})
                    break

                response = None # setting it as none for later error checking
                try:
                    # Generate AI response in a separate thread.
                    response, chat_history_ids = await asyncio.to_thread(
                        generate_response, user_input, chat_history_ids
                    )
                    await websocket.send_json({"type":"content", "data":response})
                except Exception as gen_error:

                    # store error details locally, store response as well if it exists.
                    error_details = (
                        f"Error processing input:\n"
                        f"Input: {user_input}\n"
                        f"Response: {response if response is not None else 'None'}\n"
                        f"Error: {str(gen_error)}\n"
                        f"Traceback: {traceback.format_exc()}\n"
                        "-----------------------------\n"
                    )
                    with open(ERROR_LOG_FILE, "a") as f:
                        f.write(error_details)
                    await websocket.send_json({"type":"content", "data": "An error occurred processing your message. It has been logged."})
            else:
                # No input detected; wait a moment before trying again.
                await asyncio.sleep(0.2)
    except WebSocketDisconnect:
        print("WebSocket disconnected")
    except Exception as global_error:
        # Global error handling for the WebSocket endpoint.
        error_details = (
            f"Global WebSocket Error:\n"
            f"Error: {str(global_error)}\n"
            f"Traceback: {traceback.format_exc()}\n"
            "-----------------------------\n"
        )
        with open(ERROR_LOG_FILE, "a") as f:
            f.write(error_details)

if __name__ == "__main__":
    uvicorn.run("websocket:app", host="0.0.0.0", port=8000, reload=True)
    