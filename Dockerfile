FROM python:3.10.12

WORKDIR /app

COPY backend/requirements.txt .
RUN pip install -r requirements.txt

RUN apt update && apt install ffmpeg -y

COPY backend/ .
