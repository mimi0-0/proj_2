let mediaRecorder;
let audioChunks = [];
let currentMode = ""; // モードを保存

// モード切り替え処理
function changeMode() {
    const mode = document.querySelector('input[name="mode"]:checked').value;
    currentMode = mode; // モードを現在のモードに更新

    const manualPanel = document.getElementById("manualControls");
    const voice1Panel = document.getElementById("voice1Controls");
    const voice2Panel = document.getElementById("voice2Controls");
    const voice3Panel = document.getElementById("voice3Controls");
    const textPanel = document.getElementById("textControls");

    // 各パネルを切り替え
    manualPanel.style.display = (mode === 'manual') ? 'block' : 'none';
    voice1Panel.style.display = (mode === 'voice1') ? 'block' : 'none';
    voice2Panel.style.display = (mode === 'voice2') ? 'block' : 'none';
    voice3Panel.style.display = (mode === 'voice3') ? 'block' : 'none';
    textPanel.style.display = (mode === 'text') ? 'block' : 'none';
}

// 音声録音の開始
function startRecording() {
    if (mediaRecorder && mediaRecorder.state === "recording") return; // すでに録音中なら何もしない

    navigator.mediaDevices.getUserMedia({ audio: true })
        .then(stream => {
            mediaRecorder = new MediaRecorder(stream);
            audioChunks = []; // 録音データをリセット

            mediaRecorder.ondataavailable = event => {
                audioChunks.push(event.data);
            };

            mediaRecorder.onstop = () => {
                const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
                sendAudioToServer(audioBlob); // 録音が終了したらサーバーに送信
            };

            mediaRecorder.start();
        })
        .catch(error => {
            console.error("音声録音のエラー:", error);
        });
}

// 音声録音の停止
function stopRecording() {
    if (mediaRecorder && mediaRecorder.state === "recording") {
        mediaRecorder.stop();
    }
}

// 音声をサーバーに送信
function sendAudioToServer(audioBlob) {
    const formData = new FormData();
    formData.append("audio", audioBlob, "recording.wav");

    // モードごとに送信先を決定
    let endpoint = '';
    switch (currentMode) {
        case "voice1":
            endpoint = '/upload1';
            break;
        case "voice2":
            endpoint = '/upload2';
            break;
        case "voice3":
            endpoint = '/upload3';
            break;
    }

    fetch(endpoint, {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        console.log("サーバーからのレスポンス:", data);
    })
    .catch(error => {
        console.error("音声ファイル送信エラー:", error);
    });
}

// マイクボタンがクリックされた時の処理
document.getElementById("micButton1").addEventListener("click", () => {
    if (mediaRecorder && mediaRecorder.state === "recording") {
        stopRecording();
    } else {
        startRecording();
    }
});

document.getElementById("micButton2").addEventListener("click", () => {
    if (mediaRecorder && mediaRecorder.state === "recording") {
        stopRecording();
    } else {
        startRecording();
    }
});

document.getElementById("micButton3").addEventListener("click", () => {
    if (mediaRecorder && mediaRecorder.state === "recording") {
        stopRecording();
    } else {
        startRecording();
    }
});
