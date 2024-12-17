import subprocess
import re
import sys
import os
import julius

#相対パス設定
main = "C:/Users/misak/proj_2/backend/testapp/dictation-kit-4.5/main.jconf"
am_dnn = "C:/Users/misak/proj_2/backend/test.app/dictation-kit-4.5/am-dnn.jconf"
julius_dnn = "C:/Users/misak/proj_2/backend/test.app/dictation-kit-4.5/julius.dnnconf"
input_file = "C:/Users/misak/proj_2/backend/testapp/output.wav"
julius_path = "C:/Users/misak/proj_2/backend/testapp/dictation-kit-4.5/bin/window/julius.exe"
#"C:\Users\misak\proj_2\backend\dictation-kit-4.5\bin\windows\julius.exe"

#インスタント化、関数呼び出し
def sentence():
    reco = julius.Julius_Recognition(julius_path, main, am_dnn, julius_dnn, input_file)
    result = reco.recognition()
    print(result) #認識結果出力
    return result
def main():
    sentence()
