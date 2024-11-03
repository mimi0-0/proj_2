import subprocess

# HViteコマンドを実行し、出力ファイルreco.mlfを作成する
def run_hvite():
    command = [
        "HVite", "-T", "2", "-H", "hmmdefs.hmm", "-i", "reco.mlf",
        "-w", "net.slf", "voca.txt", "hmmlist.txt", "test/mae_test_woman.mfc"
    ]
    
    try:
        # コマンドの実行
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        
        # コマンドの標準出力および標準エラーの内容を表示（デバッグ用）
        print("Command output:", result.stdout)
        print("Command error output:", result.stderr)
        
    except subprocess.CalledProcessError as e:
        print("HViteコマンドの実行中にエラーが発生しました:", e)
        print("Error output:", e.stderr)
        
        
# reco.mlfファイルを読み込むPythonプログラム
def read_mlf_file(file_path):
    # 検索するラベル
    target_labels = ["mae", "migi", "hidari", "usiro", "sil"]
    found_labels = []  # 見つかったラベルを格納するリスト
    
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
        
        # MLFファイルの内容を表示する
        for line in lines:
            line = line.split()
            print(line)
            for index in range(len(line)):
                
                if line[index] in target_labels:
                    found_labels.append(line[index])
        # 見つかったラベルを配列で返す
        return found_labels
        
        # 必要に応じて各行の処理を行う
        # 例: 特定のラベルやスコア情報を取得するなど
        # ここに追加の処理を記述する
        
    except FileNotFoundError:
        print(f"ファイル '{file_path}' が見つかりません。")
    except Exception as e:
        print(f"エラーが発生しました: {e}")

# コマンドの実行
run_hvite()

# reco.mlfファイルのパスを指定
mlf_file_path = 'reco.mlf'

# ファイルを読み込む
labels = read_mlf_file(mlf_file_path)
if labels:
    print("見つかったラベル:", labels)
else:
    print("ラベルが見つかりませんでした。")
