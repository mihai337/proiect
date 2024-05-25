To run the project you need 2 terminals for these 2 commands:

1. python main.py

2. python consumer-flask.py

You may need to install some packages using the command:
pip3 install fastapi python-multipart redis rq pymongo pydantic typing uvicorn requests flask pytest httpx

If you want to use docker, you just need to run:

docker compose up

You should pay attention to the ports, as the app is designed to work on docker.
