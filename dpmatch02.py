import librosa
import numpy as np
import os
import csv
import librosa.display
import warnings

# Numbaの警告を無視する
warnings.filterwarnings("ignore", message="FNV hashing is not implemented in Numba")


# MFCC抽出
def get_mfcc(path):
    y, sr = librosa.load(path)
    mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=256)
    return mfccs

# データセットを読み込む関数
def load_dataset(dataset_dir):
    waveforms = []
    labels = []
    with open(os.path.join(dataset_dir, 'metadata.csv'), newline='') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            file_name, label = row
            file_path = os.path.join(dataset_dir, file_name)
            features = get_mfcc(file_path)
            waveforms.append(features)
            labels.append(label)
    return waveforms, labels

# DPマッチングにより距離を計算
def calc_dp_matching(feature_1, feature_2):
    (num_dims, nframes_1) = np.shape(feature_1)
    nframes_2 = np.shape(feature_2)[1]
    distance = np.zeros((nframes_1, nframes_2))
    for n in range(nframes_1):
        for m in range(nframes_2):
            distance[n, m] = np.sum((feature_1[:, n] - feature_2[:, m])**2)
    cost = np.zeros((nframes_1, nframes_2))
    track = np.zeros((nframes_1, nframes_2), np.int16)
    cost[0, 0] = distance[0, 0]
    for n in range(1, nframes_1):
        cost[n, 0] = cost[n-1, 0] + distance[n, 0]
        track[n, 0] = 0
    for m in range(1, nframes_2):
        cost[0, m] = cost[0, m-1] + distance[0, m]
        track[0, m] = 2
    for n in range(1, nframes_1):
        for m in range(1, nframes_2):
            vertical = cost[n-1, m] + distance[n, m]
            diagonal = cost[n-1, m-1] + 2 * distance[n, m]
            horizontal = cost[n, m-1] + distance[n, m]
            candidate = [vertical, diagonal, horizontal]
            transition = np.argmin(candidate)
            cost[n, m] = candidate[transition]
            track[n, m] = transition
    total_cost = cost[-1, -1] / (nframes_1 + nframes_2)
    return total_cost

# 正解のラベルを記録する関数
def record_result(query_file, predicted_label, correct_label, output_file="result/experiment_results.csv"):
    # "result" フォルダが存在しなければ作成
    os.makedirs("result", exist_ok=True)
    
    # 結果をCSVに追記
    with open(output_file, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([query_file, predicted_label, correct_label, predicted_label == correct_label])

# テストを実行し結果を記録する関数
def DP_test(query_file, correct_label):
    dataset_path = "/mnt/utm-shared/project/dataset/"
    query = get_mfcc(dataset_path + query_file)
    distances = {}
    for i, label in enumerate(labels):
        reference = waveforms[i]
        distance = calc_dp_matching(query, reference)
        distances[label] = distance
    min_label = min(distances, key=distances.get)
    record_result(query_file, min_label, correct_label)
    return min_label

# 連続実験を実行し、正解率を計算する関数
def run_experiments():
    total_tests = 0
    correct_predictions = 0
# ここにテストファイルを追加していく
    test_cases = [
        ("ex01_mae.wav", "まえ"),
        ("ex02_ushiro.wav", "うしろ"),
        ("ex03_migi.wav", "みぎ"),
        ("ex04_ushiro.wav", "うしろ"),
        ("ex05_mae.wav", "まえ"),
        ("ex06_mae.mp3", "まえ"),
        ("ex07_mae.mp3", "まえ"),
        ("ex08_mae.mp3", "まえ"),
        ("ex09_usiro.mp3", "うしろ"),
        ("ex10_usiro.mp3", "うしろ"),
    ]
    
    # 最初の実行でファイルを上書きする
    #record_result(None, None, None, overwrite=True)  # ファイルを上書きしてヘッダーを書き込む

    for query_file, correct_label in test_cases:
        total_tests += 1
        if DP_test(query_file, correct_label) == correct_label:
            correct_predictions += 1

    # 正解率の表示
    accuracy = correct_predictions / total_tests * 100
    print(f"Total Tests: {total_tests}")
    print(f"Correct Predictions: {correct_predictions}")
    print(f"Accuracy: {accuracy:.2f}%")

# メインプログラム
if __name__ == "__main__":
    dataset_dir = '/mnt/utm-shared/project/dataset'
    waveforms, labels = load_dataset(dataset_dir)

    run_experiments()

