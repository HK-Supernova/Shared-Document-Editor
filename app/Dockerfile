# FROM python:3.13

# WORKDIR /app

# COPY . .
# COPY UI app/UI
# COPY Server app/Server
# COPY cert.pem .
# COPY key.pem .

# RUN pip3 install -r requirements.txt

# EXPOSE 443

# CMD ["uvicorn", "Server.server:app", "--host", "0.0.0.0", "--port", "443", "--ssl-certfile=cert.pem", "--ssl-keyfile=key.pem"]


FROM python:3.13

WORKDIR /app

COPY Server app/Server
COPY requirements.txt .
COPY . . 

RUN pip3 install -r requirements.txt

EXPOSE 8000

CMD ["uvicorn", "Server.server:app", "--host", "0.0.0.0", "--port", "8000"]
