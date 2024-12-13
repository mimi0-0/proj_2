# -*- coding: utf-8 -*-

#
# MFCC特徴の計算を行います．
#

# wavデータを読み込むためのモジュール(wave)をインポート
import wave

# -*- coding: utf-8 -*-

#
# MFCC特徴の計算を行います．
#

# wavデータを読み込むためのモジュール(wave)をインポート
import wave

#録音用モジュールをインポート
import soundcard as sc

#音声ファイルの保存用モジュールをインポート
import soundfile as sf

# Pytorchを用いた処理に必要なモジュールをインポート
import torch
from torch.utils.data import DataLoader

#MFCCを計算するクラスをインポート
from compute_mfcc_to_decode import FeatureExtractor

#レーベンシュタイン距離を測る関数をインポート
from levenshtein import edit_dist

# モデルの定義をインポート
from my_model import MyCTCModel

# 数値演算用モジュール(numpy)をインポート
import numpy as np

# json形式の入出力を行うモジュールをインポート
import json

# os, sysモジュールをインポート
import os
import sys

def ctc_simple_decode(int_vector, token_list):
    ''' 以下の手順で，フレーム単位のCTC出力をトークン列に変換する
        1. 同じ文字が連続して出現する場合は削除
        2. blank を削除
    int_vector: フレーム単位のCTC出力(整数値列)
    token_list: トークンリスト
    output:     トークン列
    '''
    # 出力文字列
    output = []
    # 一つ前フレームの文字番号
    prev_token = -1
    # フレーム毎の出力文字系列を前から順番にチェックしていく
    for n in int_vector:
        if n != prev_token:
            # 1. 前フレームと同じトークンではない
            if n != 0:
                # 2. かつ，blank(番号=0)ではない
                # --> token_listから対応する文字を抽出し，
                #     出力文字列に加える
                output.append(token_list[n])
            # 前フレームのトークンを更新
            prev_token = n
    return output

    
def CTC(unit,token_list,mean_std,model,config,recording_path="/Users/owner/proj/decode/record"):
    fs = 16000
    recording_sec = 5
    file = "recording.wav"

    #録音する。
    wav_path = os.path.join(recording_path,file)
    default_mic = sc.default_microphone()
    print("Recording...")
    data = default_mic.record(samplerate=fs, numframes=fs*recording_sec)
    print("Saving...")
    sf.write(wav_path, data =data[:, 0], samplerate = fs)
    print("Done.")

    print("Calculating MFCC...")

    #MFCC特徴量を計算
    frame_length = 25
    frame_shift = 10
    low_frequency = 20
    high_frequency = fs / 2
    num_mel_bins = 23
    num_ceps = 13
    dither=1.0
    np.random.seed(seed=0)


    feat_extractor = FeatureExtractor(
                       sample_frequency=fs, 
                       frame_length=frame_length, 
                       frame_shift=frame_shift, 
                       num_mel_bins=num_mel_bins, 
                       num_ceps=num_ceps,
                       low_frequency=low_frequency, 
                       high_frequency=high_frequency, 
                       dither=dither)
    

    with wave.open(wav_path) as wav:
        # サンプリング周波数のチェック
        if wav.getframerate() != fs:
            sys.stderr.write('The expected \
                sampling rate is 16000.\n')
            exit(1)
        # wavファイルが1チャネル(モノラル)
        # データであることをチェック
        if wav.getnchannels() != 1:
            sys.stderr.write('This program \
                supports monaural wav file only.\n')
            exit(1)
        
        # wavデータのサンプル数
        num_samples = wav.getnframes()

        # wavデータを読み込む
        waveform = wav.readframes(num_samples)

        # 読み込んだデータはバイナリ値
        # (16bit integer)なので，数値(整数)に変換する
        waveform = np.frombuffer(waveform, dtype=np.int16)
        
        # MFCCを計算する
        mfcc = feat_extractor.ComputeMFCC(waveform)

    # 特徴量のフレーム数と次元数を取得
    (num_frames, num_dims) = np.shape(mfcc)
   
    
    utterance_id = 1

    # 特徴量ファイルの名前(splitextで拡張子を取り除いている)
    out_file = os.path.splitext(file)[0]
    out_file = os.path.join(os.path.abspath(recording_path), 
                            out_file + '.bin')

    # データをfloat32形式に変換
    mfcc = mfcc.astype(np.float32)

    # データをファイルに出力
    mfcc.tofile(out_file)

        

    print("Done.")
    print("Recognizing...")
    #ここから認識


    # トークンリスト
    token_list_path = token_list

    mean_std_file = mean_std
    # 学習済みのモデルファイル
    model_file = model

    # 学習時に出力した設定ファイル
    config_file = config

    # ミニバッチに含める発話数
    batch_size = 10
    
    #
    # 設定ここまで
    #


    # 設定ファイルを読み込む
    with open(config_file, mode='r') as f:
        config = json.load(f)

    # 読み込んだ設定を反映する
    # 中間層のレイヤー数
    num_layers = config['num_layers']
    # 層ごとのsub sampling設定
    sub_sample = config['sub_sample']
    # RNNのタイプ(LSTM or GRU)
    rnn_type = config['rnn_type']
    # 中間層の次元数
    hidden_dim = config['hidden_dim']
    # Projection層の次元数
    projection_dim = config['projection_dim']
    # bidirectional を用いるか(Trueなら用いる)
    bidirectional = config['bidirectional']


     # 特徴量の平均/標準偏差ファイルを読み込む
    with open(mean_std_file, mode='r',encoding='utf-8') as f:
        # 全行読み込み
        lines = f.readlines()
        # 1行目(0始まり)が平均値ベクトル(mean)，
        # 3行目が標準偏差ベクトル(std)
        mean_line = lines[1]
        std_line = lines[3]
        # スペース区切りのリストに変換
        feat_mean = mean_line.split()
        feat_std = std_line.split()
        # numpy arrayに変換
        feat_mean = np.array(feat_mean, 
                                dtype=np.float32)
        feat_std = np.array(feat_std, 
                               dtype=np.float32)
        
     # 次元数の情報を得る
    feat_dim = np.size(feat_mean)

    
    # トークンリストをdictionary型で読み込む
    # このとき，0番目は blank と定義する
    token_list = {0: '<blank>'}
    with open(token_list_path, mode='r',encoding = 'utf-8') as f:
        # 1行ずつ読み込む
        for line in f: 
            # 読み込んだ行をスペースで区切り，
            # リスト型の変数にする
            parts = line.split()
            # 0番目の要素がトークン，1番目の要素がID
            token_list[int(parts[1])] = parts[0]

    
    # トークン数(blankを含む)
    num_tokens = len(token_list)

     # ニューラルネットワークモデルを作成する
    # 入力の次元数は特徴量の次元数，
    # 出力の次元数はトークン数となる
    model = MyCTCModel(dim_in=feat_dim,
                       dim_enc_hid=hidden_dim,
                       dim_enc_proj=projection_dim,
                       dim_out=num_tokens, 
                       enc_num_layers=num_layers,
                       enc_bidirectional=bidirectional,
                       enc_sub_sample=sub_sample,
                       enc_rnn_type=rnn_type)
    
    # モデルのパラメータを読み込む
    model.load_state_dict(torch.load(model_file))



    # CUDAが使える場合はモデルパラメータをGPUに，
    # そうでなければCPUに配置する
    if torch.cuda.is_available():
        device = torch.device('cuda')
    else:
        device = torch.device('cpu')
   
    # モデルを評価モードに設定する
    model.eval()

    # デコード結果および正解ラベルをファイルに書き込みながら
    # 以下の処理を行う
    #feat_lens
    feat_len = num_frames
    feat_lens = torch.zeros(1,1)
    feat_lens[0,0]=feat_len
    #splice
    splice = 0
    #max_feat_len
    max_feat_len = feat_len
    # 特徴量データを特徴量ファイルから読み込む
    feat = np.fromfile(out_file, 
                        dtype=np.float32)
        # フレーム数 x 次元数の配列に変形
    feat = feat.reshape(-1, feat_dim)
    # 平均と標準偏差を使って正規化(標準化)を行う
    feat = (feat - feat_mean) / feat_std
    # splicing: 前後 n フレームの特徴量を結合する
    org_feat = feat.copy()
    
    for n in range(-splice, splice+1):
        # 元々の特徴量を n フレームずらす
        tmp = np.roll(org_feat, n, axis=0)
        if n < 0:
            # 前にずらした場合は
            # 終端nフレームを0にする
            tmp[n:] = 0
            
        elif n > 0:
            # 後ろにずらした場合は
            # 始端nフレームを0にする
            tmp[:n] = 0
        else:
            continue
        # ずらした特徴量を次元方向に
        # 結合する
        feat = np.hstack([feat,tmp])   

    # 特徴量データのフレーム数を最大フレーム数に
    # 合わせるため，0で埋める
    pad_len = max_feat_len - feat_len
    feat = np.pad(feat,
                    [(0, pad_len), (0, 0)],
                    mode='constant',
                    constant_values=0)
    
    feats_list = feat.tolist()
    feats_list2 = [feats_list]
    features = torch.tensor(feats_list2)

    # PackedSequence の仕様上，
        # ミニバッチがフレーム長の降順で
        # ソートされている必要があるため，
        # ソートを実行する
    
    sorted_lens, indices = \
        torch.sort(feat_lens.view(-1),
                    dim=0,
                    descending=True)
    features = features[indices]
    feat_lens = sorted_lens

    # CUDAが使える場合はデータをGPUに，
    # そうでなければCPUに配置する
    features = features.to(device)

    # モデルの出力を計算(フォワード処理)
    # out_lensは処理後のフレーム数．
    # sub_sampleを行った場合は，
    # out_lensはfeat_lensより小さい値になる
   
    outputs, out_lens = model(features, feat_lens)

    # バッチ内の1発話ごとに以下の処理を行う
    for n in range(outputs.size(0)):
        # 出力はフレーム長でソートされている
        # 元のデータ並びに戻すため，
        # 対応する要素番号を取得する
        idx = 1
        # 本来のCTCの確率計算は，
        # 複数存在するパスを考慮するが，
        # ここでは簡単のため，各フレームのmax値を
        # たどる Best path decoding を行う
        _, hyp_per_frame = torch.max(outputs[0], 1)
        # numpy.array型に変換
        hyp_per_frame = hyp_per_frame.cpu().numpy()
        # 認識結果の文字列を取得
        hypothesis = \
            ctc_simple_decode(hyp_per_frame,
                                token_list)
        #認識結果を出力
        print("Done.")
        print("---result--- ")
        print(hypothesis)

        string_hypothesis = ""
        for letter in hypothesis:
            string_hypothesis = string_hypothesis + letter
        
        string_hypothesis = "みぎくめとん"
        dictionary = ["まえ","うしろ","みぎ","ひだり","に","ちゃくりく","すすんで","ひゃくせんちめーとる"]
        dictionary_char = ["前","後ろ","右","左","に","着陸","進んで","100cm"]
        dict = []
        distance = []
        time = []
        string = ""
        i = 0
        
        while i < len(string_hypothesis):
            for n in range(i,len(string_hypothesis)-1):
                for ward in dictionary:
                    if edit_dist(string_hypothesis[i:n],ward)>edit_dist(string_hypothesis[i:n+1],ward):
                        time.append(n+1)
                        distance.append(edit_dist(string_hypothesis[i:n],ward))
                        dict.append(ward)

            print(string_hypothesis[i:n])
            min_index=distance.index(min(distance))
            i = time[min_index]
            print(dict[min_index])
            index=dictionary.index(dict[min_index])
            string = string + dictionary_char[index]
            time = []
            distance = []
            dict = []
        

        #for ward in dictionary:
        #    distance.append(edit_dist(string_hypothesis, ward))
        #min_index = distance.index(min(distance))

    return dictionary_char[min_index]