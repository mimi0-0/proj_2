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


// 音声コマンド処理
document.getElementById("micButton1").onclick = async () => {
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
                const response = await fetch("http://localhost:5001/upload1", {
                    method: "POST",
                    body: formData,
                });
                const result = await response.json();
                alert(`音声データ送信結果: ${result.status},送信されたコマンド: ${result.sentcommand}`);
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

// 音声コマンド処理
document.getElementById("micButton2").onclick = async () => {
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
                const response = await fetch("http://localhost:5001/upload2", {
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

// 音声コマンド処理
document.getElementById("micButton3").onclick = async () => {
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
                const response = await fetch("http://localhost:5001/upload3", {
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
async function sendTextCommand() {
    const textCommand = document.getElementById("textCommand").value;

    if (textCommand) {
        try {
            const response = await fetch('/upload_keitaiso', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ textCommand: textCommand })
            });

            if (response.ok) {
                const result = await response.json();
                const chatContainer = document.getElementById("chatContainer");
                const newMessage = document.createElement("div");
                newMessage.classList.add("chat-message");
                newMessage.textContent = `${textCommand}:${result.command}`;
                chatContainer.appendChild(newMessage);

                // テキストボックスを空にする
                document.getElementById("textCommand").value = "";
                chatContainer.scrollTop = chatContainer.scrollHeight; // チャットをスクロールして最新メッセージを表示
            } else {
                alert('Error processing command.');
            }
        } catch (error) {
            console.error('Error:', error);
            alert('Failed to send command.');
        }
    } else {
        alert("コマンドを入力してください。");
    }
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

function updateData() {
    fetch('/update_data')  // サーバーのエンドポイントにリクエスト
        .then(response => response.json())  // JSONとしてレスポンスを解析
        .then(data => {
            // データをHTMLに反映
            document.getElementById('battery').textContent = `バッテリー: ${data.battery}`;
            document.getElementById('time').textContent = `飛行時間: ${data.time}`;
            document.getElementById('speed').textContent = `スピード(cm/s): ${data.speed}`;
        
        })
        .catch(error => {
            console.error('Error fetching data:', error);  // エラー時の処理
        });
}

// 1秒ごとにupdateDataを呼び出す
setInterval(updateData, 1000);
