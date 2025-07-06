#!/bin/bash

# FastAPIサーバーのエンドポイントURL
# 例: http://192.168.1.10:8000/push_data/
API_ENDPOINT="http://<YOUR_FASTAPI_SERVER_IP>:8000/push_data/"

# 送信するデータを取得（この場合はホスト名）
HOSTNAME=$(hostname)

# JSON形式でデータを準備
JSON_PAYLOAD=$(printf '''{"hostname": "%s"}''' "$HOSTNAME")

# curlコマンドでFastAPIにPOSTリクエストを送信
curl -X POST \
     -H "Content-Type: application/json" \
     -d "$JSON_PAYLOAD" \
     "$API_ENDPOINT"

# 実行結果をログに出力したい場合は以下のように追記
# echo "$(date): Sent data for $HOSTNAME" >> /var/log/agent.log

