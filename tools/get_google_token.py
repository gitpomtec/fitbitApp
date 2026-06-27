# get_google_token.py
import json
import os
import urllib.parse
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer

import requests

curdir = os.path.dirname(__file__) + "/"

with open(f"{curdir}Config.json", "r") as f:
    CONFIG = json.load(f)

CLIENT_ID = CONFIG["CLIENT_ID"]
CLIENT_SECRET = CONFIG["CLIENT_SECRET"]
REDIRECT_URI = "http://localhost:8000"

AUTH_ENDPOINT = "https://accounts.google.com/o/oauth2/v2/auth"
TOKEN_ENDPOINT = "https://oauth2.googleapis.com/token"

# 必要なスコープだけ残してください(最初はreadonlyのみで十分なはず)
SCOPES = [
    "https://www.googleapis.com/auth/googlehealth.activity_and_fitness.readonly",
    "https://www.googleapis.com/auth/googlehealth.health_metrics_and_measurements.readonly",
    "https://www.googleapis.com/auth/googlehealth.sleep.readonly",
    "https://www.googleapis.com/auth/googlehealth.profile.readonly",
    "https://www.googleapis.com/auth/googlehealth.settings.readonly",
    # 必要なら追加:
    # "https://www.googleapis.com/auth/googlehealth.nutrition.readonly",
    # "https://www.googleapis.com/auth/googlehealth.ecg.readonly",
    # "https://www.googleapis.com/auth/googlehealth.irn.readonly",
    # "https://www.googleapis.com/auth/googlehealth.location.readonly",
]

received_code = {}


class RedirectHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        query = urllib.parse.urlparse(self.path).query
        params = urllib.parse.parse_qs(query)
        received_code["code"] = params.get("code", [None])[0]

        self.send_response(200)
        self.send_header("Content-type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write("<h1>認可が完了しました。このタブは閉じて構いません。</h1>".encode("utf-8"))

    def log_message(self, format, *args):
        pass  # サーバーログを抑制


def main():
    # access_type=offline ... refresh_tokenを発行してもらうために必須
    # prompt=consent ... 過去に許可済みでも毎回確認画面を出し、refresh_tokenを確実に再発行させる
    auth_params = {
        "client_id": CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "response_type": "code",
        "scope": " ".join(SCOPES),
        "access_type": "offline",
        "prompt": "consent",
    }
    auth_url = f"{AUTH_ENDPOINT}?{urllib.parse.urlencode(auth_params)}"

    print("ブラウザで以下のURLを開いてください(自動で開きます):")
    print(auth_url)
    webbrowser.open(auth_url)

    server = HTTPServer(("localhost", 8000), RedirectHandler)
    print("リダイレクト待機中...")
    server.handle_request()  # 1回だけリクエストを受けて終了

    code = received_code.get("code")
    if not code:
        print("認可コードを取得できませんでした。")
        return

    print(f"認可コード取得: {code[:10]}...")

    token_data = {
        "code": code,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "redirect_uri": REDIRECT_URI,
        "grant_type": "authorization_code",
    }
    res = requests.post(TOKEN_ENDPOINT, data=token_data)
    res_json = res.json()

    if res.status_code != 200:
        print(f"トークン取得失敗: {res.status_code}")
        print(res_json)
        return

    with open(f"{curdir}Token.json", "w", encoding="utf-8") as f:
        json.dump(res_json, f, indent=2, ensure_ascii=False)

    print("Token.json に保存しました。")
    print(f"取得スコープ: {res_json.get('scope')}")


if __name__ == "__main__":
    main()