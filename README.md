# check availability

## 概要
ホテルやレストランのキャンセル状況をキャッチして、lineにメッセージを送信


## 機能
- 10分おきに予約ページをスクレイピングし、前回の予約状況との差分をlineに通知
- lineクライアントから「現在の空き状況を教えて」とメッセージを受けとった場合、現在のスクレイピングした結果を通知


## アーキテクチャ
<img src="https://github.com/user-attachments/assets/218e1dca-f7b4-4bfc-ae68-68a492cc03a0" width="50%">
