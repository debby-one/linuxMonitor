import os
import psycopg2
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from dotenv import load_dotenv

# .envファイルから環境変数を読み込む
load_dotenv()

# FastAPIアプリケーションのインスタンスを作成
app = FastAPI()

# データベース接続情報を環境変数から取得
DATABASE_URL = os.getenv("DATABASE_URL")

# 受け取るデータの型をPydanticモデルで定義
class AgentData(BaseModel):
    hostname: str

@app.post("/push_data/")
def push_data(data: AgentData):
    """
    エージェントからデータを受け取り、PostgreSQLに保存するエンドポイント
    """
    conn = None
    try:
        # データベースに接続
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()

        # SQLインジェクションを防ぐため、プレースホルダを使用
        insert_query = "INSERT INTO agent_data (hostname) VALUES (%s)"
        cur.execute(insert_query, (data.hostname,))

        # 変更をコミット
        conn.commit()

        cur.close()
        return {"status": "success", "message": f"Data from {data.hostname} received and stored."}

    except Exception as e:
        # エラーが発生した場合はロールバック
        if conn:
            conn.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

    finally:
        # 接続を閉じる
        if conn:
            conn.close()

@app.get("/")
def read_root():
    return {"message": "Agent data receiver is running."}
