"""config/*.yaml 을 읽어 소스별로 헤드라인을 모으고 output/index.html 로 만든다."""
import html
import time
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import yaml

from fetchers import FETCHERS

ROOT = Path(__file__).resolve().parent.parent
KST = ZoneInfo("Asia/Seoul")
MAX_AGE = 48 * 3600  # 이틀에 한 번 실행해도 빠지는 소식이 없도록


def load(name):
    return yaml.safe_load((ROOT / "config" / name).read_text(encoding="utf-8"))


def collect(topic, sources):
    items, seen = [], set()
    for source in sources:
        try:
            found = FETCHERS[source["type"]](source, topic)
        except Exception as e:  # 소스 하나가 죽어도 나머지는 계속
            print(f"[warn] {source['type']} / {topic['name']}: {e!r}")
            continue
        for item in found:
            too_old = item["published"] and time.time() - item["published"] > MAX_AGE
            if item["title"] in seen or too_old:
                continue
            seen.add(item["title"])
            items.append(item)
    items.sort(key=lambda i: i["published"], reverse=True)
    return items[: topic.get("limit", 5)]


def render(digest, now):
    sections = []
    for name, items in digest:
        rows = "".join(
            f'<li><a href="{html.escape(i["link"])}">{html.escape(i["title"])}</a>'
            f'<span>{html.escape(i["source"])}'
            + (f' · {datetime.fromtimestamp(i["published"], KST):%m/%d %H:%M}' if i["published"] else "")
            + "</span></li>"
            for i in items
        ) or '<li class="empty">새 소식 없음</li>'
        sections.append(f"<section><h2>{html.escape(name)}</h2><ul>{rows}</ul></section>")
    return f"""<!doctype html>
<html lang="ko"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Daily Brief {now:%Y-%m-%d}</title>
<style>
:root {{ color-scheme: light dark; --fg:#1a1a1a; --muted:#6b6b6b; --bg:#fafafa; --line:#e4e4e4; --link:#0b57d0; }}
@media (prefers-color-scheme: dark) {{ :root {{ --fg:#e8e8e8; --muted:#9a9a9a; --bg:#161616; --line:#2c2c2c; --link:#8ab4f8; }} }}
body {{ margin:0 auto; max-width:680px; padding:24px 16px 48px; background:var(--bg); color:var(--fg);
  font:16px/1.5 -apple-system, "Apple SD Gothic Neo", "Noto Sans KR", sans-serif; }}
h1 {{ font-size:1.4rem; margin:0 0 4px; }} .date {{ color:var(--muted); margin:0 0 24px; }}
h2 {{ font-size:1.05rem; margin:28px 0 8px; }}
ul {{ list-style:none; padding:0; margin:0; }}
li {{ padding:10px 0; border-bottom:1px solid var(--line); }}
a {{ color:var(--link); text-decoration:none; }}
li span {{ display:block; color:var(--muted); font-size:.8rem; margin-top:2px; }}
.empty {{ color:var(--muted); }}
</style></head><body>
<h1>Daily Brief</h1><p class="date">{now:%Y-%m-%d %H:%M} KST</p>
{"".join(sections)}
</body></html>
"""


def main():
    topics, sources = load("topics.yaml"), load("sources.yaml")
    digest = [(t["name"], collect(t, sources)) for t in topics]
    for name, items in digest:
        print(f"{name}: {len(items)}건")
    out = ROOT / "output" / "index.html"
    out.parent.mkdir(exist_ok=True)
    out.write_text(render(digest, datetime.now(KST)), encoding="utf-8")


if __name__ == "__main__":
    main()
