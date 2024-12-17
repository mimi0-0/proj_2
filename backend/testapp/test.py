from filler_to_newtext import load_ipadic_dict
from split_verb import CommandProcessor
import julius
import pyaudio
import subprocess
from subprocess import PIPE
main = "./dictation-kit-4.5/main.jconf"
am_dnn = "./dictation-kit-4.5/am-dnn.jconf"
julius_dnn = "./dictation-kit-4.5/julius.dnnconf"
input_file = "./output.wav"
julius_path = "./dictation-kit-4.5/bin/windows/julius.exe"
reco = julius.Julius_Recognition(julius_path, main, am_dnn, julius_dnn, input_file)
command_from_audio = reco.recognition()
print(f"Received command from audio: {command_from_audio}")