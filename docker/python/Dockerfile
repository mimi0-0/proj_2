FROM python:3.9-alpine

WORKDIR /app

COPY ./docker/python/lib.txt .
RUN pip install --no-cache-dir --upgrade -r /app/lib.txt

COPY ./back/ .
# ポートの公開
EXPOSE 3000
CMD ["flask", "run", "--host=0.0.0.0"]

# コンテナ起動時にapp.pyを実行
CMD ["python", "app.py"]
CMD ["uvicorn", "main:app", "--reload", "--host", "0.0.0.0", "--port", "8080"]