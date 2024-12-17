import subprocess

# 日本語のパスはエラーがでる
julius      = "C:/cygwin64/home/Hoshi_Manami/Python/project/julius-4.5-win32bin/bin/julius.exe"
main        = "C:/cygwin64/home/Hoshi_Manami/Python/project/dictation-kit-4.5/main.jconf"
am_dnn      = "C:/cygwin64/home/Hoshi_Manami/Python/project/dictation-kit-4.5/am-dnn.jconf"
julius_dnn  = "C:/cygwin64/home/Hoshi_Manami/Python/project/dictation-kit-4.5/julius.dnnconf"

input_audio_file  = "./BASIC5000_0001.wav"

args = [julius, "-C", main, "-C", am_dnn, "-dnnconf", julius_dnn, "-input", "rawfile", "-charconv", "utf-8", "sjis"]

p = subprocess.run(args, stdout=subprocess.PIPE, input=input_audio_file, encoding='utf-8', text=True)
print("p.stdout: ", p.stdout)
output = p.stdout.split("### read waveform input")[1].split("\n\n")
print("output: " ,output)
for i in output:
    if "sentence1:" not in i:
        continue
    sentence = i.split("sentence1:")[1].split("\n")[0].replace(" ", "")
    print("sentence: ", sentence)
