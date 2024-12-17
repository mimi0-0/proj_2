let mediaRecorder;
let audioChunks = [];

const chatMessages = document.getElementById("chatMessages");

// コマンド送信時にチャット履歴に追加し、ドローンからのレスポンスを表示
function sendCommand(command) {
    addChatBubble(`コマンド: ${command}`, "user");
    chatMessages.scrollTop = chatMessages.scrollHeight;

    // ドローンのレスポンスをシミュレート
    setTimeout(() => {
        const response = getDroneResponse(command);
        addChatBubble(response, "drone");
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }, 1000); // レスポンスは1秒後に返す
}

// 吹き出しを追加
function addChatBubble(message, sender) {
    const bubble = document.createElement("div");
    bubble.classList.add("chat-bubble", sender === "user" ? "user-bubble" : "drone-bubble");
    bubble.textContent = message;
    chatMessages.appendChild(bubble);
}

// ドローンからの簡単なレスポンスを返す（シミュレート）
function getDroneResponse(command) {
    switch (command) {
        case "takeoff":
            return "ドローンが離陸しました！";
        case "land":
            return "ドローンが着陸しました。";
        case "Command":
            return "ドローンと接続しました。";
        case "flip":
            return "ドローンがフリップしました！";
        case "up":
            return "ドローンが上昇しました。";
        case "down":
            return "ドローンが下降しました。";
        case "left":
            return "ドローンが左に移動しました。";
        case "right":
            return "ドローンが右に移動しました。";
        default:
            return "コマンドを実行しました。";
    }
}

// モード切り替え処理
function changeMode() {
    const mode = document.querySelector('input[name="mode"]:checked').value;
    
    const manualPanel = document.getElementById("manualControls");
    const voicePanel = document.getElementById("voiceControls");
    const textPanel = document.getElementById("textControls");

    if (mode === 'manual') {
        manualPanel.style.display = 'block';
        voicePanel.style.display = 'none';
        textPanel.style.display = 'none';
    } else if (mode === 'voice') {
        manualPanel.style.display = 'none';
        voicePanel.style.display = 'block';
        textPanel.style.display = 'none';
    } else if (mode === 'text') {
        manualPanel.style.display = 'none';
        voicePanel.style.display = 'none';
        textPanel.style.display = 'block';
    }
}

/*
// 音声コマンド処理
document.getElementById("micButton").onclick = async () => {
    try {
        console.log("録音ボタンがクリックされました。");
        audioChunks = [];
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        console.log("オーディオストリーム取得成功:", stream);
        
        mediaRecorder = new MediaRecorder(stream);
        mediaRecorder.ondataavailable = (event) => {
            console.log("データが利用可能:", event);
            audioChunks.push(event.data);
        };

        mediaRecorder.onstop = async () => {
            console.log("録音停止。データ送信を開始します。");
            const audioBlob = new Blob(audioChunks, { type: "audio/wav" });
            console.log("Blob生成成功:", audioBlob);
            const formData = new FormData();
            formData.append("audio", audioBlob, "received_audio.wav"); // ファイル名を指定

            try {
                const response = await fetch("http://localhost:5001/upload", {
                    method: "POST",
                    body: formData,
                });
                const result = await response.json();
                alert(`音声データ送信結果: ${result.status}`);
                console.log("サーバー応答:", result);
            } catch (error) {
                console.error("送信エラー:", error);
            }
        };

        mediaRecorder.start();
        alert("録音開始。マイクを話したら停止します。");
        console.log("録音開始");

        setTimeout(() => {
            mediaRecorder.stop();
            alert("録音停止しました。送信します。");
            console.log("録音停止");
        }, 3000); // 3秒後に録音停止
    } catch (error) {
        console.error("録音エラー:", error);
        alert("マイクのアクセス許可が必要です。");
    }
};

// テキスト送信処理


// テキスト送信処理
function sendTextCommand() {
    const textCommand = document.getElementById("textCommand").value;
    alert(`テキスト送信: ${textCommand}`);
}



function sendCommand(command) {
    fetch('http://localhost:5001/command', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ command })
    })
    .then(response => response.json())
    .then(data => console.log(data))
    .catch(error => console.error('Error:', error));
}

*/