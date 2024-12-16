import subprocess
import re
import sys
import os
import julius

#相対パス設定
main = "/app/dictation-kit-4.5/main.jconf"
am_dnn = "/app/dictation-kit-4.5/am-dnn.jconf"
julius_dnn = "/app/dictation-kit-4.5/julius.dnnconf"
input_file = "/app/dictation-kit-4.5/BASIC5000_0001.wav"
julius_path = "/app/dictation-kit-4.5/bin/linux/julius"
#"C:\Users\misak\proj_2\backend\dictation-kit-4.5\bin\windows\julius.exe"

#インスタント化、関数呼び出し
reco = julius.Julius_Recognition(julius_path, main, am_dnn, julius_dnn, input_file)
result = reco.recognition()
print(result) #認識結果出力