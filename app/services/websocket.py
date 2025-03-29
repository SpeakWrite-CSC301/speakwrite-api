import uvicorn
import traceback
import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.middleware.cors import CORSMiddleware


# import the speech transcription function and Mistral response generator.
from summarizer import classify_input
from mistral_inference import generate_mistral_response

app = FastAPI() # create a seperate WebSocket service

#Allowed addresses
origins = [
    "http://localhost:3000",  # Frontend URL
    "http://127.0.0.1:3000",
    "*",  # Allow all origins (not recommended for production)
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

ERROR_LOG_FILE = "error.log"

chat_history = ""

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint that continuously listens to microphone input,
    generates an AI response, and sends it to the client in real time.

    In case of an error, it saves the input text, generated response (if any),
    and error details to a local file.
    """
    await websocket.accept()
    # Use an initial chat history (could be an empty string)

    global chat_history

    try:
        while True:
            # Get speech input in a separate thread.
            # user_input = await websocket.receive_text()
            data = await websocket.receive_json()
            user_input = data.get("content", "")
            user_tone = data.get("tone", "")
            # user_input = await asyncio.to_thread(recognize_speech)
            if user_input:
                print(f"Recognized speech: {user_input}")

                if user_input.lower() in ["exit", "quit"]:
                    await websocket.send_json({"type":"content", "data":"Conversation ended."})
                    break

                try:
                    # Generate the Mistral response based on current chat history and recognized speech.
                    updated_chat_history = await asyncio.to_thread(
                        classify_input, chat_history, user_input, user_tone
                    )
                    # Update the active chat history with the new result.
                    chat_history = updated_chat_history

                    await websocket.send_json({"type":"content", "data": updated_chat_history})
                except Exception as gen_error:

                    # store error details locally, store response as well if it exists.
                    error_details = (
                        f"Error processing input:\n"
                        f"Input: {user_input}\n"
                        f"Response: None"
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


@app.router.post("/chat_history")
async def update_chat_history(request: Request):
    """
    Update the global chat history with new content.
    This function can be called from other parts of the application.
    """
    raw_data = await request.json()
    print(f"Raw data received: {raw_data}")
    print(f"Updating chat history with: {raw_data.get('history', '')}")
    global chat_history
    chat_history = raw_data.get("history", chat_history)
    print(f"Chat history updated: {chat_history}")
    return {"message": "Chat history updated successfully."}

if __name__ == "__main__":
    uvicorn.run("websocket:app", host="0.0.0.0", port=8000, reload=True)
    