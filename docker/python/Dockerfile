
# ベースイメージ
FROM python:3.9-slim

# 作業ディレクトリの設定
WORKDIR /app

# Python依存関係をインストール
COPY ./docker/python/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
# 例: ALSA関連ツールをインストール
# 必要なパッケージのインストール
RUN apt-get update && apt-get install -y \
    pulseaudio \
    ffmpeg \
    alsa-utils \
    libsdl2-dev \
    && rm -rf /var/lib/apt/lists/*

#RUN apt install build-essential gcc g++
RUN pip install matplotlib
RUN apt -y update
RUN apt -y install libopencv-dev libopencv-core-dev python3-opencv libopencv-contrib-dev opencv-data
