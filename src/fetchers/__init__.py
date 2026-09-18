"""소스 type -> fetch(source, topic) 함수. 새 소스는 모듈 하나 추가 후 여기 등록."""
from fetchers import google_news, rss

FETCHERS = {
    "rss": rss.fetch,
    "google_news": google_news.fetch,
}
