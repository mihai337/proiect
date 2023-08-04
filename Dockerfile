FROM python:3.11

WORKDIR /app

COPY . .

RUN pip3 install fastapi python-multipart redis rq pymongo pydantic typing uvicorn

CMD ["uvicorn" , "main:app" , "--reload"]
