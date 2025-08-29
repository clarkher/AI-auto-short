import requests
import json
import traceback
import sys
import urllib3
import argparse
import os

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def main():
    parser = argparse.ArgumentParser(description="Login API Test - 動態驗證用戶帳密")
    parser.add_argument("--account", required=True, help="用戶帳號（email）")
    parser.add_argument("--password", required=True, help="用戶密碼")
    args = parser.parse_args()

    url = "https://social.cmoney.tw/identity/token"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {
        "grant_type": "password",
        "login_method": "email",
        "client_id": "cmstockcommunity",
        "account": args.account,
        "password": args.password
    }

    try:
        response = requests.post(url, headers=headers, data=data, verify=False)
        print("Status:", response.status_code)
        print("Response:", response.text)

        # 自動建立 docs 目錄（如不存在）
        docs_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "docs"))
        os.makedirs(docs_dir, exist_ok=True)
        output_path = os.path.join(docs_dir, "api-login-response.json")

        # 儲存 response 為 artifacts
        try:
            resp_json = response.json()
        except Exception:
            resp_json = {}

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump({
                "status_code": response.status_code,
                "headers": dict(response.headers),
                "body": resp_json if resp_json else response.text
            }, f, ensure_ascii=False, indent=2)

        # 嚴格驗證 access_token
        if (
            response.status_code == 200
            and isinstance(resp_json, dict)
            and "access_token" in resp_json
            and resp_json.get("access_token")
        ):
            print("✅ 登入成功")
            sys.exit(0)
        else:
            # 顯示 API 回傳錯誤訊息
            err_msg = ""
            if isinstance(resp_json, dict):
                err_msg = resp_json.get("error_description") or resp_json.get("error") or ""
            print(f"❌ 登入失敗，請檢查帳號密碼。{err_msg}", file=sys.stderr)
            sys.exit(2)
    except Exception as e:
        print("=== Exception Occurred ===", file=sys.stderr)
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()