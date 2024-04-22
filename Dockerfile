FROM --platform=linux/amd64 python:3.10.9-slim-buster
LABEL authors="ilya.grynyshyn@gmail.com"


WORKDIR /app


ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1


RUN pip install --upgrade pip
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . /app
