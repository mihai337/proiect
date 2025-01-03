Follow these instructions to run the project:
```bash
python main.py
```

You may need to install some packages using the command:
```bash
pip3 install fastapi python-multipart redis rq pydantic typing uvicorn requests pytest httpx firebase-admin
```

If you want to use docker, you just need to run:
```bash
docker compose up
```

You should pay attention to the ports, as the app is designed to work on docker.
