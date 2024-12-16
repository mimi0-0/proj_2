import numpy as np

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