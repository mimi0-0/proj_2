#FROM python:3.9-alpine

#WORKDIR /app

#COPY ./docker/python/requirements.txt .
#RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt
# ベースイメージ
FROM python:3.9-slim

# 必要なシステムパッケージをインストール
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    libsndfile1 \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# 作業ディレクトリの設定
WORKDIR /app

# Python依存関係をインストール
COPY ./docker/python/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN apt update
#RUN apt install build-essential gcc g++
RUN pip install matplotlib
RUN apt -y update
RUN apt -y install libopencv-dev libopencv-core-dev python3-opencv libopencv-contrib-dev opencv-data
