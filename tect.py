/* チャット欄の吹き出しスタイル */
.chat-messages {
    max-height: 300px; /* 表示エリアの高さ */
    overflow-y: auto; /* スクロール可能 */
    padding: 10px;
    background-color: #f9f9f9;
    border-radius: 5px;
    border: 1px solid #ddd;
}

/* 吹き出し全体の基本スタイル */
.chat-bubble {
    max-width: 60%;
    padding: 10px 15px;
    margin: 5px 0;
    border-radius: 15px;
    position: relative;
    font-size: 14px;
    line-height: 1.5;
    word-wrap: break-word;
}

/* ユーザーの吹き出し（右側） */
.user-bubble {
    background-color: #007bff;
    color: #fff;
    align-self: flex-end;
    border-top-right-radius: 0;
    margin-left: auto; /* 右寄せ */
}

/* ドローンの吹き出し（左側） */
.drone-bubble {
    background-color: #e9ecef;
    color: #333;
    align-self: flex-start;
    border-top-left-radius: 0;
    margin-right: auto; /* 左寄せ */
}

/* 吹き出しの三角形部分（ユーザー側） */
.user-bubble::after {
    content: '';
    position: absolute;
    top: 10px;
    right: -10px;
    width: 0;
    height: 0;
    border-left: 10px solid #007bff;
    border-top: 10px solid transparent;
    border-bottom: 10px solid transparent;
}

/* 吹き出しの三角形部分（ドローン側） */
.drone-bubble::after {
    content: '';
    position: absolute;
    top: 10px;
    left: -10px;
    width: 0;
    height: 0;
    border-right: 10px solid #e9ecef;
    border-top: 10px solid transparent;
    border-bottom: 10px solid transparent;
}
