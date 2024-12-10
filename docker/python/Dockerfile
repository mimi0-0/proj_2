FROM python:3.9-alpine

WORKDIR /app

COPY ./docker/python/lib.txt .
RUN pip install --no-cache-dir --upgrade -r /app/lib.txt

COPY ./back/ .

CMD ["uvicorn", "main:app", "--reload", "--host", "0.0.0.0", "--port", "8080"]