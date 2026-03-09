import re
import time
import feedparser
from datetime import datetime, timedelta, timezone

RSS_FEEDS = [
    # --- グローバル スタートアップ ---
    {"url": "https://techcrunch.com/feed/",          "source": "TechCrunch"},
    {"url": "https://venturebeat.com/feed/",          "source": "VentureBeat"},
    {"url": "https://thenextweb.com/feed/",           "source": "The Next Web"},
    {"url": "https://eu-startups.com/feed/",          "source": "EU-Startups"},
    {"url": "https://www.startupgrind.com/blog/feed/","source": "Startup Grind"},
    # --- アクセラレーター・VC ---
    {"url": "https://news.ycombinator.com/rss",       "source": "Hacker News"},
    {"url": "https://a16z.com/feed/",                 "source": "a16z"},
    # --- 日本 ---
    {"url": "https://bridge.jp/feed/",                "source": "Bridge"},
    {"url": "https://coralcap.co/feed/",              "source": "Coral Capital"},
    {"url": "https://thebridge.jp/feed",              "source": "The Bridge JP"},
]

def _clean_html(text: str) -> str:
    return re.sub(r"<[^>]+>", "", text or "").strip()

def collect_all() -> list[dict]:
    cutoff = datetime.now(timezone.utc) - timedelta(hours=24)
    articles = []

    for feed_info in RSS_FEEDS:
        try:
            feed = feedparser.parse(feed_info["url"])
            for entry in feed.entries[:15]:
                # 公開日時を取得
                published = None
                if hasattr(entry, "published_parsed") and entry.published_parsed:
                    published = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)

                # 24時間以内の記事のみ
                if published and published < cutoff:
                    continue

                raw_summary = getattr(entry, "summary", "") or getattr(entry, "description", "")
                summary = _clean_html(raw_summary)[:500]

                articles.append({
                    "title":     entry.get("title", "").strip(),
                    "url":       entry.get("link", ""),
                    "summary":   summary,
                    "published": published.strftime("%Y-%m-%d %H:%M UTC") if published else "不明",
                    "source":    feed_info["source"],
                })
        except Exception as e:
            print(f"[WARN] フィード取得エラー ({feed_info['source']}): {e}")

        time.sleep(0.3)  # レート制限対策

    print(f"[INFO] 収集件数: {len(articles)} 件")
    return articles
