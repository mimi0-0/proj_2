FROM python:3.9-alpine

WORKDIR /app

ENV FLASK_APP=main.py

COPY ./docker/python/lib.txt .
RUN pip install --upgrade pip
RUN pip install --upgrade setuptools
RUN pip install -r /app/lib.txt

COPY ./back/ .

CMD ["flask", "run"]