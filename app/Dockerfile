FROM python:3.11

WORKDIR /app

COPY Server app/Server
COPY requirements.txt .
COPY . . 

RUN pip3 install -r requirements.txt

EXPOSE 8000

CMD ["uvicorn", "Server.server:app", "--host", "0.0.0.0", "--port", "8000"]
