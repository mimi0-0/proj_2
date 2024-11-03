import librosa
import numpy as np
import os
import csv
import librosa.display
#from scipy.spatial.distance import cdist
#import matplotlib.pyplot as plt
#from scipy.spatial.distance import euclidean
#from fastdtw import fastdtw

# MFCC抽出
def get_mfcc(path):
    y, sr = librosa.load(path)
    mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=256)
    return mfccs



# テンプレートとなるデータセットを読み込む関数
def load_dataset(dataset_dir):
    waveforms = []
    labels = []
    # metadata.csvを読み込んでファイル名とラベルを取得
    with open(os.path.join(dataset_dir, 'metadata.csv'), newline='') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            file_name, label = row
            file_path = os.path.join(dataset_dir, file_name)
            # 特徴量を抽出
            features = get_mfcc(file_path)
            
            waveforms.append(features)
            labels.append(label)
    
    return waveforms, labels


# DPマッチングにより距離を計算
def calc_dp_matching(feature_1, feature_2):
    
    # フレーム数と次元数を取得
    (num_dims, nframes_1) = np.shape(feature_1)
    nframes_2 = np.shape(feature_2)[1]

    # 距離(コスト)行列を計算
    distance = np.zeros((nframes_1, nframes_2))
    for n in range(nframes_1):
        for m in range(nframes_2):
            # feature_1 の n フレーム目と
            # feature_2 の m フレーム目の
            # ユークリッド距離の二乗を計算
            distance[n, m] = np.sum((feature_1[:, n] - feature_2[:, m])**2)

    # 累積コスト行列
    cost = np.zeros((nframes_1, nframes_2))
    # 遷移の種類(縦/斜め/横)を記録する行列
    # 0: 縦の遷移, 1:斜めの遷移, 2:横の遷移
    track = np.zeros((nframes_1, nframes_2), np.int16)

    # スタート地点の距離
    cost[0, 0] = distance[0, 0]

    # 縦の縁: 必ず縦に遷移する
    for n in range(1, nframes_1):
        cost[n, 0] = cost[n-1, 0] + distance[n, 0]
        track[n, 0] = 0

    # 横の縁: 必ず横に遷移する
    for m in range(1, nframes_2):
        cost[0, m] = cost[0, m-1] + distance[0, m]
        track[0, m] = 2

    # それ以外: 縦横斜めの内，最小の遷移を行う
    for n in range(1, nframes_1):
        for m in range(1, nframes_2):
            # 縦の遷移をしたときの累積コスト
            vertical = cost[n-1, m] + distance[n, m]
            # 斜めの遷移をしたときの累積コスト
            # (斜めは2倍のペナルティを与える)
            diagonal = cost[n-1, m-1] + 2 * distance[n, m]
            # 横の遷移をしたときの累積コスト
            horizontal = cost[n, m-1] + distance[n, m]

            # 累積コストが最小となる遷移を選択する
            candidate = [vertical, diagonal, horizontal]
            transition = np.argmin(candidate)

            # 累積コストと遷移を記録する
            cost[n, m] = candidate[transition]
            track[n, m] = transition

    # 総コストはcost行列の最終行最終列の値
    # 特徴量のフレーム数で正規化する
    total_cost = cost[-1, -1] / (nframes_1 + nframes_2)
    return total_cost

# 与えられた音声から4つそれぞれの単語との距離を計算して表示する関数
def DP_search(file_name):
    path = "/Users/abechika/project/dataset/"
    print("testfile:",file_name)  

    query = get_mfcc(path + file_name)  # クエリを読み込む
    
    distances = {}
    for i, label in enumerate(labels):
        reference = waveforms[i]  # 各ラベルの音声波形を参照に設定
        distance = calc_dp_matching(query, reference)  # DTWマッチング
        distances[label] = distance  # 結果を辞書に保存

    # 結果を表示
    for label, distance in distances.items():
        print(f'DTW Distance between query and "{label}": {distance}')

    min_label = min(distances, key=distances.get)
    min_distance = distances[min_label]

    # 結果を表示
    print(f'距離が最小の単語: "{min_label}", 距離: {min_distance}\n')
    
    
def DP_ans(file_name):
    path = "/Users/abechika/project/dataset/"
    #print("testfile:",file_name)  

    query = get_mfcc(path + file_name)  # クエリを読み込む
    
    distances = {}
    for i, label in enumerate(labels):
        reference = waveforms[i]  # 各ラベルの音声波形を参照に設定
        distance = calc_dp_matching(query, reference)  # DTWマッチング
        distances[label] = distance  # 結果を辞書に保存

    min_label = min(distances, key=distances.get)
    min_distance = distances[min_label]

    return min_label
    


# メインプログラム
if __name__ == "__main__":
    # データセットのパス
    dataset_dir = 'dataset'
    print(librosa.__version__)
    
    # データセットをロード
    waveforms, labels = load_dataset(dataset_dir)

    print("labels:" , labels)  # labels リストを表示

    DP_search("ex01_mae.wav")
    DP_search("ex02_ushiro.wav")
    DP_search("ex03_migi.wav")
    DP_search("ex04_ushiro.wav")

    print(DP_ans("ex01_mae.wav"))
