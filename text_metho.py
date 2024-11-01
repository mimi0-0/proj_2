import speech_recognition as sr
# Recognizerのインスタンスを作成
def out_put(audio_file):
    recognizer = sr.Recognizer()
    # 音声ファイルを読み込む
    with sr.AudioFile(audio_file) as source:
        audio_data = recognizer.record(source)
    # Google Web Speech APIを使って文字起こし
    try:
        text = recognizer.recognize_google(audio_data, language='ja-JP')
        print("文字起こし結果:", text)
        return text
    except sr.UnknownValueError:
        print("音声を認識できませんでした。")
        return "Sorry, I couldn't understand the audio."
    except sr.RequestError as e:
        print(f"APIリクエストエラー: {e}")
        return "Sorry, I couldn't understand the audio."