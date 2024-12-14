import subprocess
import re
import sys
import os
sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', buffering=1)

#julius = "C:/.../dictation-kit-4.5/bin/windows/julius.exe"
#main = "C:/.../dictation-kit-4.5/main.jconf"
#am_dnn = "C:/.../dictation-kit-4.5/am-dnn.jconf"
#julius_dnn = "C:/.../dictation-kit-4.5/julius.dnnconf"
#input_file = "C:/.../BASIC5000_0001.wav"

class Julius_Recognition():
    def __init__(self, julius, main, am_dnn, julius_dnn, input_file):
        self.julius = julius
        self.main = main
        self.am_dnn = am_dnn
        self.julius_dnn = julius_dnn
        self.input_file = input_file

    def recognition(self):
        args = [self.julius, "-C", self.main, "-C", self.am_dnn, "-dnnconf", self.julius_dnn, "-input", "rawfile", "-charconv", "shift_jis", "sjis"]
        try:
            proc = subprocess.Popen(args, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                    encoding='utf-8', text=True, cwd="dictation-kit-4.5") #cwdは合っても無くても
            stdout, stderr = proc.communicate(input=self.input_file + "\n")
            #print(stdout)
            results = []
            for line in stdout.splitlines():
                match = re.search(r"sentence1:\s*(.+)", line)
                if match:
                    result = match.group(1).strip()
                    results.append(result)
            return result
        
        except Exception as e:
            print(f"[ERROR] {e}")
        
        finally:
            proc.terminate()
            print("[INFO] Julius process terminated.")
