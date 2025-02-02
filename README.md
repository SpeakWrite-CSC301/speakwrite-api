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

3. Run the development server
```bash
fastapi dev main.py
```

Open [http://127.0.0.1:8000](http://127.0.0.1:8000) with your browser to see the result. Open [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) or [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc) to see the API docs, as a Swagger doc or a ReDoc, respectively.

Reference: [FastAPI Setup](https://fastapi.tiangolo.com/tutorial/first-steps/)