import socket
import time
import requests
from filler_to_newtext import load_ipadic_dict
from split_verb import process_text

if __name__ == "__main__":
    server_url = 'http://localhost:5011/upload'  # ローカルホスト上のFlaskサーバーに接続

    try:
        # サーバーに最初のPOSTリクエストを送信してsent_to_clientを取得
        response = requests.post(server_url, json={})
        response_data = response.json()

        if response.status_code == 200:
            # サーバーから送信されたテキストコマンドを取得
            text = response_data.get('sent_to_client', '')
            print(f"Command from server: {text}")

            if text:
                # 辞書を読み込む
                ipadic_dir_path = "/home/rf22127/mecab/mecab-ipadic-2.7.0-20070801/"
                dictionary = load_ipadic_dict(ipadic_dir_path)

                # テキスト処理
                command, verbs, verb_dependents = process_text(text, dictionary)

                # 結果を出力
                print("\n生成されたコマンド:")
                print(command)
                print("\n動詞リスト:")
                print(verbs)
                print("\n動詞依存語リスト:")
                print(verb_dependents)

                # サーバーにコマンドを送り返す
                for com_split in command.split(' /'):
                    if com_split.strip():
                        request_payload = {"response_command": com_split.strip()}
                        print(f"Sending to server: {request_payload}")  # デバッグ用に送信内容を表示
                        confirm_response = requests.post(server_url, json=request_payload)

                        if confirm_response.status_code == 200:
                            print(f"Server confirmation: {confirm_response.json()}")
                        else:
                            print(f"Error from server: {confirm_response.text}")
                        time.sleep(5)  # 5秒間待機
        else:
            print(f"Error from server: {response_data}")

    except Exception as e:
        print(f"Error connecting to server: {e}")