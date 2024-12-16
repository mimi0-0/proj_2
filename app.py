from flask import Flask, render_template, request, jsonify
import speech_recognition as sr
import io

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/command', methods=['POST'])
def command():
    data = request.get_json()
    command = data.get('command', '')
    # コマンド処理のロジックを追加
    print(f"受信したコマンド: {command}")
    return jsonify({'status': 'success', 'command': command})

@app.route('/transcribe', methods=['POST'])
def transcribe_audio():
    if 'audio' not in request.files:
        return jsonify({'error': 'Audio file not provided'}), 400

    audio_file = request.files['audio']
    recognizer = sr.Recognizer()
    try:
        # SpeechRecognition用の形式に変換
        audio_data = sr.AudioFile(io.BytesIO(audio_file.read()))
        with audio_data as source:
            audio = recognizer.record(source)
        transcription = recognizer.recognize_google(audio, language='ja-JP')
        return jsonify({'transcription': transcription})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
