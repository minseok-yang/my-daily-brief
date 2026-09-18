import calendar
from functools import lru_cache

import feedparser


@lru_cache  # 같은 피드를 주제마다 다시 받지 않도록
def parse(url, name):
    items = []
    for e in feedparser.parse(url).entries:
        source = e.get("source", {}).get("title") or name
        title = e.get("title", "").removesuffix(f" - {source}").strip()
        ts = e.get("published_parsed") or e.get("updated_parsed")
        items.append({
            "title": title,
            "link": e.get("link", ""),
            "source": source,
            "published": calendar.timegm(ts) if ts else 0,
        })
    return tuple(items)


def fetch(source, topic):
    keywords = [k.lower() for k in topic["keywords"]]
    items = parse(source["url"], source.get("name", source["url"]))
    return [i for i in items if any(k in i["title"].lower() for k in keywords)]
