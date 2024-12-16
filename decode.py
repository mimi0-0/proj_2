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

# 作成したDatasetクラスをインポート
from my_dataset import SequenceDataset

# モデルの定義をインポート
from my_model import MyCTCModel

# 数値演算用モジュール(numpy)をインポート
import numpy as np

# json形式の入出力を行うモジュールをインポート
import json

# os, sysモジュールをインポート
import os
import sys


class FeatureExtractor():
    ''' 特徴量(MFCC)を抽出するクラス
    sample_frequency: 入力波形のサンプリング周波数 [Hz]
    frame_length: フレームサイズ [ミリ秒]
    frame_shift: 分析間隔(フレームシフト) [ミリ秒]
    num_mel_bins: メルフィルタバンクの数(=FBANK特徴の次元数)
    num_ceps: MFCC特徴の次元数(0次元目を含む)
    lifter_coef: リフタリング処理のパラメータ
    low_frequency: 低周波数帯域除去のカットオフ周波数 [Hz]
    high_frequency: 高周波数帯域除去のカットオフ周波数 [Hz]
    dither: ディザリング処理のパラメータ(雑音の強さ)
    '''
    # クラスを呼び出した時点で最初に1回実行される関数
    def __init__(self, 
                 sample_frequency=16000, 
                 frame_length=25, 
                 frame_shift=10, 
                 num_mel_bins=23, 
                 num_ceps=13, 
                 lifter_coef=22, 
                 low_frequency=20, 
                 high_frequency=8000, 
                 dither=1.0):
        # サンプリング周波数[Hz]
        self.sample_freq = sample_frequency
        # 窓幅をミリ秒からサンプル数へ変換
        self.frame_size = int(sample_frequency * frame_length * 0.001)
        # フレームシフトをミリ秒からサンプル数へ変換
        self.frame_shift = int(sample_frequency * frame_shift * 0.001)
        # メルフィルタバンクの数
        self.num_mel_bins = num_mel_bins
        # MFCCの次元数(0次含む)
        self.num_ceps = num_ceps
        # リフタリングのパラメータ
        self.lifter_coef = lifter_coef
        # 低周波数帯域除去のカットオフ周波数[Hz]
        self.low_frequency = low_frequency
        # 高周波数帯域除去のカットオフ周波数[Hz]
        self.high_frequency = high_frequency
        # ディザリング係数
        self.dither_coef = dither

        # FFTのポイント数 = 窓幅以上の2のべき乗
        self.fft_size = 1
        while self.fft_size < self.frame_size:
            self.fft_size *= 2

        # メルフィルタバンクを作成する
        self.mel_filter_bank = self.MakeMelFilterBank()

        # 離散コサイン変換(DCT)の基底行列を作成する
        self.dct_matrix = self.MakeDCTMatrix()

        # リフタ(lifter)を作成する
        self.lifter = self.MakeLifter()


    def Herz2Mel(self, herz):
        ''' 周波数をヘルツからメルに変換する
        '''
        return (1127.0 * np.log(1.0 + herz / 700))


    def MakeMelFilterBank(self):
        ''' メルフィルタバンクを作成する
        '''
        # メル軸での最大周波数
        mel_high_freq = self.Herz2Mel(self.high_frequency)
        # メル軸での最小周波数
        mel_low_freq = self.Herz2Mel(self.low_frequency)
        # 最小から最大周波数まで，
        # メル軸上での等間隔な周波数を得る
        mel_points = np.linspace(mel_low_freq, 
                                 mel_high_freq, 
                                 self.num_mel_bins+2)

        # パワースペクトルの次元数 = FFTサイズ/2+1
        # ※Kaldiの実装ではナイキスト周波数成分(最後の+1)は
        # 捨てているが，本実装では捨てずに用いている
        dim_spectrum = int(self.fft_size / 2) + 1

        # メルフィルタバンク(フィルタの数 x スペクトルの次元数)
        mel_filter_bank = np.zeros((self.num_mel_bins, dim_spectrum))
        for m in range(self.num_mel_bins):
            # 三角フィルタの左端，中央，右端のメル周波数
            left_mel = mel_points[m]
            center_mel = mel_points[m+1]
            right_mel = mel_points[m+2]
            # パワースペクトルの各ビンに対応する重みを計算する
            for n in range(dim_spectrum):
                # 各ビンに対応するヘルツ軸周波数を計算
                freq = 1.0 * n * self.sample_freq/2 / dim_spectrum
                # メル周波数に変換
                mel = self.Herz2Mel(freq)
                # そのビンが三角フィルタの範囲に入っていれば，重みを計算
                if mel > left_mel and mel < right_mel:
                    if mel <= center_mel:
                        weight = (mel - left_mel) / (center_mel - left_mel)
                    else:
                        weight = (right_mel-mel) / (right_mel-center_mel)
                    mel_filter_bank[m][n] = weight
         
        return mel_filter_bank

    
    def ExtractWindow(self, waveform, start_index, num_samples):
        '''
        1フレーム分の波形データを抽出し，前処理を実施する．
        また，対数パワーの値も計算する
        '''
        # waveformから，1フレーム分の波形を抽出する
        window = waveform[start_index:start_index + self.frame_size].copy()

        # ディザリングを行う
        # (-dither_coef～dither_coefの一様乱数を加える)
        if self.dither_coef > 0:
            window = window \
                     + np.random.rand(self.frame_size) \
                     * (2*self.dither_coef) - self.dither_coef

        # 直流成分をカットする
        window = window - np.mean(window)

        # 以降の処理を行う前に，パワーを求める
        power = np.sum(window ** 2)
        # 対数計算時に-infが出力されないよう，フロアリング処理を行う
        if power < 1E-10:
            power = 1E-10
        # 対数をとる
        log_power = np.log(power)

        # プリエンファシス(高域強調) 
        # window[i] = 1.0 * window[i] - 0.97 * window[i-1]
        window = np.convolve(window,np.array([1.0, -0.97]), mode='same')
        # numpyの畳み込みでは0番目の要素が処理されない
        # (window[i-1]が存在しないので)ため，
        # window[0-1]をwindow[0]で代用して処理する
        window[0] -= 0.97*window[0]

        # hamming窓をかける 
        # hamming[i] = 0.54 - 0.46 * np.cos(2*np.pi*i / (self.frame_size - 1))
        window *= np.hamming(self.frame_size)

        return window, log_power


    def ComputeFBANK(self, waveform):
        '''メルフィルタバンク特徴(FBANK)を計算する
        出力1: fbank_features: メルフィルタバンク特徴
        出力2: log_power: 対数パワー値(MFCC抽出時に使用)
        '''
        # 波形データの総サンプル数
        num_samples = np.size(waveform)
        # 特徴量の総フレーム数を計算する
        num_frames = (num_samples - self.frame_size) // self.frame_shift + 1
        # メルフィルタバンク特徴
        fbank_features = np.zeros((num_frames, self.num_mel_bins))
        # 対数パワー(MFCC特徴を求める際に使用する)
        log_power = np.zeros(num_frames)

        # 1フレームずつ特徴量を計算する
        for frame in range(num_frames):
            # 分析の開始位置は，フレーム番号(0始まり)*フレームシフト
            start_index = frame * self.frame_shift
            # 1フレーム分の波形を抽出し，前処理を実施する．
            # また対数パワーの値も得る
            window, log_pow = self.ExtractWindow(waveform, start_index, num_samples)
            
            # 高速フーリエ変換(FFT)を実行
            spectrum = np.fft.fft(window, n=self.fft_size)
            # FFT結果の右半分(負の周波数成分)を取り除く
            # ※Kaldiの実装ではナイキスト周波数成分(最後の+1)は捨てているが，
            # 本実装では捨てずに用いている
            spectrum = spectrum[:int(self.fft_size/2) + 1]

            # パワースペクトルを計算する
            spectrum = np.abs(spectrum) ** 2

            # メルフィルタバンクを畳み込む
            fbank = np.dot(spectrum, self.mel_filter_bank.T)

            # 対数計算時に-infが出力されないよう，フロアリング処理を行う
            fbank[fbank<0.1] = 0.1

            # 対数をとってfbank_featuresに加える
            fbank_features[frame] = np.log(fbank)

            # 対数パワーの値をlog_powerに加える
            log_power[frame] = log_pow

        return fbank_features, log_power


    def MakeDCTMatrix(self):
        ''' 離散コサイン変換(DCT)の基底行列を作成する
        '''
        N = self.num_mel_bins
        # DCT基底行列 (基底数(=MFCCの次元数) x FBANKの次元数)
        dct_matrix = np.zeros((self.num_ceps,self.num_mel_bins))
        for k in range(self.num_ceps):
            if k == 0:
                dct_matrix[k] = np.ones(self.num_mel_bins) * 1.0 / np.sqrt(N)
            else:
                dct_matrix[k] = np.sqrt(2/N) \
                    * np.cos(((2.0*np.arange(N)+1)*k*np.pi) / (2*N))

        return dct_matrix


    def MakeLifter(self):
        ''' リフタを計算する
        '''
        Q = self.lifter_coef
        I = np.arange(self.num_ceps)
        lifter = 1.0 + 0.5 * Q * np.sin(np.pi * I / Q)
        return lifter


    def ComputeMFCC(self, waveform):
        ''' MFCCを計算する
        '''
        # FBANKおよび対数パワーを計算する
        fbank, log_power = self.ComputeFBANK(waveform)
        
        # DCTの基底行列との内積により，DCTを実施する
        mfcc = np.dot(fbank, self.dct_matrix.T)

        # リフタリングを行う
        mfcc *= self.lifter

        # MFCCの0次元目を，前処理をする前の波形の対数パワーに置き換える
        mfcc[:,0] = log_power

        return mfcc
    

#デコード用関数
    
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

#レーベンシュタイン距離をはかる関数

def edit_dist(a, b, add=1, remove=1, replace=1):
  len_a = len(a) + 1
  len_b = len(b) + 1
  # 配列の初期化
  arr = [[-1 for col in range(len_a)] for row in range(len_b)]
  arr[0][0] = 0
  for row in range(1, len_b):
    arr[row][0] = arr[row - 1][0] + add
  for col in range(1, len_a):
    arr[0][col] = arr[0][col - 1] + remove
  # 編集距離の計算
  def go(row, col):
    if (arr[row][col] != -1):
      return arr[row][col]
    else:
      dist1 = go(row - 1, col) + add
      dist2 = go(row, col - 1) + remove
      dist3 = go(row - 1, col - 1)
      arr[row][col] = min(dist1, dist2, dist3) if (b[row - 1] == a[col - 1]) else min(dist1, dist2, dist3 + replace)
      return arr[row][col]
  return go(len_b - 1, len_a - 1)
    

if __name__ == "__main__":

    
    fs = 16000
    recording_sec = 5
    path = "/Users/rknsm/proj/decode/record"
    file = "recording.wav"
    exp_dir = "/Users/rknsm/proj/ex/exp_train_large"
    unit = 'kana'

    #録音する。
    wav_path = os.path.join(path,file);
    
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
    feat_scp = os.path.join(path, 'feats.scp')


    feat_extractor = FeatureExtractor(
                       sample_frequency=fs, 
                       frame_length=frame_length, 
                       frame_shift=frame_shift, 
                       num_mel_bins=num_mel_bins, 
                       num_ceps=num_ceps,
                       low_frequency=low_frequency, 
                       high_frequency=high_frequency, 
                       dither=dither)
    

    with open(feat_scp, mode='w',encoding='utf-8') as file_feat:

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
        out_file = os.path.join(os.path.abspath(path), 
                                out_file + '.bin')

        # データをfloat32形式に変換
        mfcc = mfcc.astype(np.float32)

        # データをファイルに出力
        mfcc.tofile(out_file)

        # 発話ID，特徴量ファイルのパス，フレーム数，
                # 次元数を特徴量リストに書き込む
        file_feat.write("%s %s %d %d\n" %
                    (utterance_id, out_file, num_frames, num_dims))
        

    print("Done.")
    print("Recognizing...")
    #ここから認識

    

    # 評価データのラベルファイル
    label_test = os.path.join(exp_dir, 'data', unit, 'label_test')

    # トークンリスト
    token_list_path = os.path.join(exp_dir, 'data', unit,
                                   'token_list')

    # 学習済みモデルが格納されているディレクトリ
    model_dir = os.path.join(exp_dir, unit+'_model_ctc')

    # 訓練データから計算された特徴量の平均/標準偏差ファイル
    mean_std_file = os.path.join(model_dir, 'mean_std.txt')

    # 学習済みのモデルファイル
    model_file = os.path.join(model_dir, 'best_model.pt')

    # デコード結果を出力するディレクトリ
    output_dir = os.path.join(model_dir, 'decode_test')

    # デコード結果および正解文の出力ファイル
    hypothesis_file = os.path.join(output_dir, 'hypothesis.txt')
    reference_file = os.path.join(output_dir, 'reference.txt')

    # 学習時に出力した設定ファイル
    config_file = os.path.join(model_dir, 'config.json')

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

     # 出力ディレクトリが存在しない場合は作成する
    os.makedirs(output_dir, exist_ok=True)

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
    with open(hypothesis_file, mode='w',encoding='utf-8') as hyp_file, \
         open(reference_file, mode='w',encoding = 'utf-8') as ref_file:
        
        #feat_lens
        feat_len = num_frames
        #feat_lens_list = [[feat_len]]
        #print(feat_lens_list)
        #feat_lens = torch.tensor(feat_lens_list)
        feat_lens = torch.zeros(1,1)
        feat_lens[0,0]=feat_len
        #feats
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

            #認識結果から最も近い距離の単語を取得
            dictionary = ["まえ","うしろ","みぎ","ひだり","りりく","ちゃくりく"]
            distance = []
            for ward in dictionary:
                distance.append(edit_dist(string_hypothesis, ward))
            min_index = distance.index(min(distance))
            print(dictionary[min_index])