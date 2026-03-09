import sys
from collectors.rss import collect_all
from processors.summarize import summarize_articles
from mailer.send import send_digest


def main() -> None:
    print("=== Startup Digest 開始 ===")

    articles = collect_all()
    if not articles:
        print("[WARN] 記事が収集できませんでした。終了します。")
        sys.exit(0)

    print("[INFO] Gemini で要約中...")
    digest = summarize_articles(articles)

    send_digest(digest)
    print("=== 完了 ===")


if __name__ == "__main__":
    main()
