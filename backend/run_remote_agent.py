
import paramiko
import getpass
import os

def run_remote_agent(hostname, username, password=None, key_filename=None):
    """
    リモートサーバーに接続し、agent.shを実行します。

    Args:
        hostname (str): 接続先サーバーのホスト名またはIPアドレス
        username (str): 接続に使用するユーザー名
        password (str, optional): パスワード認証の場合のパスワード. Defaults to None.
        key_filename (str, optional): 公開鍵認証の場合の秘密鍵のパス. Defaults to None.
    """
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        # 接続
        if key_filename:
            client.connect(hostname, username=username, key_filename=key_filename)
        elif password:
            client.connect(hostname, username=username, password=password)
        else:
            print("パスワードまたは秘密鍵のどちらかを指定してください。")
            return

        # SFTPクライアントの準備
        sftp = client.open_sftp()

        # agent.shをリモートにアップロード
        local_agent_path = os.path.join(os.path.dirname(__file__), '../agent/agent.sh')
        remote_agent_path = f'/tmp/agent.sh'
        sftp.put(local_agent_path, remote_agent_path)

        # 実行権限を付与
        sftp.chmod(remote_agent_path, 0o755)

        # agent.shを実行
        stdin, stdout, stderr = client.exec_command(remote_agent_path)

        # 実行結果の表示
        print("--- 実行結果 (stdout) ---")
        print(stdout.read().decode())
        print("--- 実行結果 (stderr) ---")
        print(stderr.read().decode())

        # 後片付け
        sftp.remove(remote_agent_path)
        sftp.close()

    except Exception as e:
        print(f"エラーが発生しました: {e}")
    finally:
        client.close()

if __name__ == '__main__':
    # 実行例
    # このスクリプトを直接実行する場合、以下の情報を適切に設定してください。
    REMOTE_HOSTNAME = "your_remote_host"  # 例: "192.168.1.100"
    REMOTE_USERNAME = "your_remote_user"    # 例: "user"

    # パスワード認証か公開鍵認証かを選択
    use_password_auth = True  # パスワード認証を使う場合はTrue, 鍵認証の場合はFalse

    if use_password_auth:
        REMOTE_PASSWORD = getpass.getpass("リモートサーバーのパスワードを入力してください: ")
        run_remote_agent(REMOTE_HOSTNAME, REMOTE_USERNAME, password=REMOTE_PASSWORD)
    else:
        # 秘密鍵のパス（必要に応じて変更）
        KEY_PATH = os.path.expanduser("~/.ssh/id_rsa")
        run_remote_agent(REMOTE_HOSTNAME, REMOTE_USERNAME, key_filename=KEY_PATH)
