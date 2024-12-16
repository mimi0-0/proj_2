from datetime import datetime
import wave
import time

import pyaudio


FORMAT        = pyaudio.paInt16
TIME          = 4           # 録音時間[s]
SAMPLE_RATE   = 44100        # サンプリングレート
FRAME_SIZE    = 1024         # フレームサイズ
CHANNELS      = 1            # モノラルかバイラルか
INPUT_DEVICE_INDEX = 0       # マイクのチャンネル
NUM_OF_LOOP   = int(SAMPLE_RATE / FRAME_SIZE * TIME)



WAV_FILE = "./output.wav"


def look_for_audio_input():
    """
    デバイス上でのオーディオ系の機器情報を表示する
    """
    pa = pyaudio.PyAudio()
    for i in range(pa.get_device_count()):
        print(pa.get_device_info_by_index(i))
        print()
    pa.terminate()


def record_and_save():
    """
    デバイスから出力される音声の録音をする
    """
    pa = pyaudio.PyAudio()

    stream = pa.open(format   = FORMAT,
                     channels = CHANNELS,
                     rate     = SAMPLE_RATE,
                     input    = True,
                     input_device_index = INPUT_DEVICE_INDEX,
                     frames_per_buffer  = FRAME_SIZE)

    print("RECORDING...")

    list_frame = []


    for i in range(NUM_OF_LOOP):
        data = stream.read(FRAME_SIZE)
        list_frame.append(data)

    print("RECORDING DONE!")

    # close and terminate stream object "stream"
    stream.stop_stream()
    stream.close()
    pa.terminate()


    wf = wave.open(WAV_FILE, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(pa.get_sample_size(FORMAT))
    wf.setframerate(SAMPLE_RATE)
    wf.writeframes(b''.join(list_frame))
    wf.close()


def main():
    look_for_audio_input() # デバイス探し
    record_and_save()      # デバイスから出力される音声を録音する


if __name__ == '__main__':
    main()
