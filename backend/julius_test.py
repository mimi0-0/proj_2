import subprocess
import re
import sys
import os
import julius

#相対パス設定
julius_path = "./dictation-kit-4.5/bin/windows/julius.exe"
main = "./dictation-kit-4.5/main.jconf"
am_dnn = "./dictation-kit-4.5/am-dnn.jconf"
julius_dnn = "./dictation-kit-4.5/julius.dnnconf"
input_file = "./dictation-kit-4.5/BASIC5000_0001.wav"

#インスタント化、関数呼び出し
reco = julius.Julius_Recognition(julius_path, main, am_dnn, julius_dnn, input_file)
result = reco.recognition()
print(result) #認識結果出力