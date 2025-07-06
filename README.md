# LinuxMonitor

## 概要

このプロジェクトは、複数のLinuxサーバーから情報を収集し、一元的に管理・監視するためのシンプルなシステムです。

各サーバーで**エージェント (agent.sh)** を実行すると、サーバーの情報（現在はホスト名）が収集され、**バックエンドサーバー**に送信されます。バックエンドサーバーは受け取ったデータをデータベースに保存します。

## 主な技術スタック

- **バックエンド:** Python, FastAPI, PostgreSQL, Docker
- **エージェント:** Bash Script
- **リモート実行:** Python, Paramiko

## ディレクトリ構成

```
.
├── agent/
│   └── agent.sh          # 各サーバーで実行するエージェントスクリプト
└── backend/
    ├── .env              # 環境変数設定ファイル（要作成）
    ├── docker-compose.yml  # Docker Compose設定ファイル
    ├── Dockerfile        # バックエンドアプリのDockerfile
    ├── init.sql          # DB初期化用SQL
    ├── main.py           # FastAPIアプリケーション本体
    ├── requirements.txt  # Pythonの依存ライブラリ
    └── run_remote_agent.py # リモートでエージェントを実行するスクリプト
```

## セットアップと実行方法

### 1. バックエンドサーバーの起動

バックエンドはDocker Composeを使って簡単に起動できます。

1.  **環境変数ファイルを作成します。**
    `.env.example` を参考に `backend` ディレクトリ内に `.env` ファイルを作成し、データベース接続情報を設定します。

    ```bash
    # backend/.env
    DATABASE_URL=postgresql://user:password@db:5432/monthly_portal
    ```

2.  **Dockerコンテナをビルドして起動します。**
    `backend` ディレクトリに移動し、以下のコマンドを実行します。

    ```bash
    cd backend
    docker-compose up --build -d
    ```

    これにより、FastAPIアプリケーション（ポート8000）とPostgreSQLデータベース（ポート5432）が起動します。

### 2. エージェントの実行

エージェントを実行して、バックエンドにデータを送信します。

#### 方法A: 手動でエージェントを実行する

1.  **APIエンドポイントを編集します。**
    `agent/agent.sh` を開き、`API_ENDPOINT` を自分のバックエンドサーバーのIPアドレスに変更します。

    ```sh
    # agent/agent.sh
    API_ENDPOINT="http://<YOUR_FASTAPI_SERVER_IP>:8000/push_data/"
    ```

2.  **スクリプトを実行します。**
    このシェルスクリプトを監視対象の各Linuxサーバーに配置し、実行権限を与えて実行します。

    ```bash
    chmod +x agent.sh
    ./agent.sh
    ```

#### 方法B: リモート実行スクリプトを使用する

`backend/run_remote_agent.py` を使うと、指定したリモートサーバーにSSH接続し、自動で `agent.sh` をアップロードして実行できます。

1.  **スクリプトを編集します。**
    `run_remote_agent.py` 内の接続先情報を、実際の環境に合わせて編集します。

    ```python
    # backend/run_remote_agent.py
    REMOTE_HOSTNAME = "your_remote_host"
    REMOTE_USERNAME = "your_remote_user"
    ```

2.  **スクリプトを実行します。**
    `backend` ディレクトリから以下のコマンドで実行します。パスワード認証か公開鍵認証かを選択できます。

    ```bash
    python run_remote_agent.py
    ```

## APIエンドポイント

-   `GET /`: アプリケーションが動作しているかを確認します。
-   `POST /push_data/`: エージェントからデータを受け取り、DBに保存します。
    -   **リクエストボディ (JSON):**
        ```json
        {
          "hostname": "string"
        }
        ```

## データベース

-   **テーブル名:** `agent_data`
-   **カラム:**
    -   `id`: SERIAL PRIMARY KEY
    -   `hostname`: VARCHAR(255)
    -   `received_at`: TIMESTAMP WITH TIME ZONE (データ受信時刻)
