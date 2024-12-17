import os
from CTC_yobidashi import CTC
import soundfile as sf
import soundcard as sc
import socket 
from sound_edit_sr_16000 import record_and_save
import pyaudio


TELLO_IP = "192.168.10.1"  # TelloのIPアドレス
TELLO_PORT = 8889  # Telloが受信するポート番号
LOCAL_PORT = 8890  # ローカルでTelloからの応答を受信するポート


sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


def send_to_tello(command):
    """
    ドローンTelloにコマンドを送る関数
    """
    try:
        print(f"Sending command to Tello: {command}")
        sock.sendto(command.encode('utf-8'), (TELLO_IP, TELLO_PORT))
        # 応答を受信（タイムアウトを設定可能）
        sock.settimeout(5.0)  # 5秒でタイムアウト
        response, _ = sock.recvfrom(1024)  # 最大1024バイト受信
        print(f"Response from Tello: {response.decode('utf-8')}")
        return response.decode('utf-8')
    except socket.timeout:
        print("No response from Tello (timeout)")
        return "No response (timeout)"
    except Exception as e:
        print(f"Error sending command to Tello: {e}")
        return f"Error: {str(e)}"

if __name__ == "__main__":

    unit = "kana"
    path = "/Users/owner/proj/decode/record"
    exp_dir =  "/Users/Owner/proj/ex" 
    token_list_path = os.path.join(exp_dir, 'data', unit,
                                   'token_list')
    
    model_dir = os.path.join(exp_dir, unit+'_model_ctc')

    mean_std_file = os.path.join(model_dir, 'mean_std.txt')

    model_file = os.path.join(model_dir, 'best_model.pt')

    config_file = os.path.join(model_dir, 'config.json')


    fs = 16000
    recording_sec = 5
    file = "recording.wav"

    for n in range(10):

        #録音する。
        wav_path = os.path.join(path,file)
        default_mic = sc.default_microphone()
        print("Recording...")
        data = default_mic.record(samplerate=fs, numframes=fs*recording_sec)
        print("Saving...")
        sf.write(wav_path, data =data[:, 0], samplerate = fs)
        print("Done.")

        #wav_path = "/Users/owner/proj/decode/record/received_audio.wav"

        command = CTC(unit =unit,wav_path = wav_path,token_list=token_list_path,mean_std=mean_std_file,model=model_file,config=config_file,recording_path=path)
        print(command)

        send_to_tello("command")

        print(f"Received command from audio: {command}")
        # Telloにコマンドを送信
        send_to_tello(command)