FROM python:3.9-alpine

WORKDIR /app

COPY ./docker/python/requirements.txt .
RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt
