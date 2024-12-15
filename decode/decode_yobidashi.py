import os
from CTC_yobidashi import CTC
import soundfile as sf;
import soundcard as sc;

if __name__ == "__main__":
    unit = "phone"
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

    #録音する。
    wav_path = os.path.join(path,file)
    default_mic = sc.default_microphone()
    print("Recording...")
    data = default_mic.record(samplerate=fs, numframes=fs*recording_sec)
    print("Saving...")
    sf.write(wav_path, data =data[:, 0], samplerate = fs)
    print("Done.")

    hypothesis = CTC(unit =unit,wav_path = wav_path,token_list=token_list_path,mean_std=mean_std_file,model=model_file,config=config_file,recording_path=path)
    print(hypothesis)