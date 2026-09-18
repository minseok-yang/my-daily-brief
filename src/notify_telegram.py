"""페이지 링크 하나를 텔레그램으로 보낸다. env: TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, PAGE_URL"""
import json
import os
import urllib.request
from datetime import datetime
from zoneinfo import ZoneInfo

today = datetime.now(ZoneInfo("Asia/Seoul")).strftime("%Y-%m-%d")
# 쿼리스트링: 텔레그램 링크 미리보기가 어제 페이지를 캐시해서 보여주는 것 방지
url = f"{os.environ['PAGE_URL'].rstrip('/')}/?d={today}"
req = urllib.request.Request(
    f"https://api.telegram.org/bot{os.environ['TELEGRAM_BOT_TOKEN']}/sendMessage",
    data=json.dumps({"chat_id": os.environ["TELEGRAM_CHAT_ID"], "text": f"Daily Brief {today}\n{url}"}).encode(),
    headers={"Content-Type": "application/json"},
)
urllib.request.urlopen(req, timeout=30)  # 실패 시 HTTPError로 워크플로 실패 처리
print("sent:", url)
