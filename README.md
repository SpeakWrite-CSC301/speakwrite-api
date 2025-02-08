## Setting up FastAPI

1. Create a Python virtual environment

```bash
python3 -m venv sw-env # do not do this within the repo
source sw-env/bin/activate # activate when on same directory as sw-env
```

2. Install dependencies listed in requirements.txt
```bash
pip install -r requirements.txt
```

3. Run the main API gateway service
```bash
python3 app/main.py
```

4. Run the speech transcription WebSocket service
```bash
python3 app/services/websocket.py
```

Open [http://127.0.0.1:8001](http://127.0.0.1:8001) with your browser to see the result. Open [http://127.0.0.1:8001/docs](http://127.0.0.1:8001/docs) or [http://127.0.0.1:8001/redoc](http://127.0.0.1:8001/redoc) to see the API docs, as a Swagger doc or a ReDoc, respectively.

Reference: [FastAPI Setup](https://fastapi.tiangolo.com/tutorial/first-steps/)