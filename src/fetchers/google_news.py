from urllib.parse import urlencode

from fetchers.rss import parse


def fetch(source, topic):
    hl, gl = source.get("hl", "ko"), source.get("gl", "KR")
    query = " OR ".join(topic["keywords"]) + " when:1d"
    url = "https://news.google.com/rss/search?" + urlencode(
        {"q": query, "hl": hl, "gl": gl, "ceid": f"{gl}:{hl}"}
    )
    return list(parse(url, "Google News"))
