#Time          = 4           # 録音時間[s]
#sample_rate   = 16000        # サンプリングレート
#frame_size    = 1024         # フレームサイズ
#channels      = 1            # モノラルかバイラルか
#mic_channel = 0       # マイクのチャンネル
#wav_file = "./output.wav"

from datetime import datetime
import wave
import time

import pyaudio

class Record():
    def __init__(self, time, sample_rate, frame_size, channels, mic_channnel, wav_file):
        self.format = pyaudio.paInt16
        self.time = time
        self.sample_rate = sample_rate #16000
        self.frame_size = frame_size #1024
        self.channels = channels #1? モノラルかバイラルか
        self.mic_channnel = mic_channnel #0
        self.num_of_loop = int(sample_rate / frame_size * time)
        self.wav_file = wav_file

    def look_for_audio_input():
        """
        デバイス上でのオーディオ系の機器情報を表示する
        """
        pa = pyaudio.PyAudio()
        for i in range(pa.get_device_count()):
            print(pa.get_device_info_by_index(i))
            print()
        pa.terminate()


    def record_and_save(self):
        """
        デバイスから出力される音声の録音をする
        """
        pa = pyaudio.PyAudio()

        stream = pa.open(format   = self.format,
                        channels = self.channels,
                        rate     = self.sample_rate,
                        input    = True,
                        input_device_index = self.mic_channnel,
                        frames_per_buffer  = self.frame_size)

        print("RECORDING...")

        list_frame = []


        for i in range(self.num_of_loop):
            data = stream.read(self.frame_size)
            list_frame.append(data)

        print("RECORDING DONE!")

        # close and terminate stream object "stream"
        stream.stop_stream()
        stream.close()
        pa.terminate()


        wf = wave.open(self.wav_file, 'wb')
        wf.setnchannels(self.channels)
        wf.setsampwidth(pa.get_sample_size(self.format))
        wf.setframerate(self.sample_rate)
        wf.writeframes(b''.join(list_frame))
        wf.close()
