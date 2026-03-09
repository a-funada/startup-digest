import os
import smtplib
import ssl
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def _importance_color(importance: str) -> str:
    return {"高": "#e74c3c", "中": "#f39c12", "低": "#95a5a6"}.get(importance, "#95a5a6")


def _build_highlights_html(highlights: list[dict]) -> str:
    html = ""
    for h in highlights:
        html += f"""
        <div class="highlight-item">
          <a href="{h['url']}">{h['title']}</a>
          <p>{h.get('reason', '')}</p>
        </div>"""
    return html


def _build_section(items: list[dict], icon: str, title: str) -> str:
    if not items:
        return ""
    html = f'<h2>{icon} {title}</h2>'
    for item in items:
        color = _importance_color(item.get("importance", "中"))
        html += f"""
        <div class="article-item">
          <span class="importance-dot" style="color:{color};">●</span>
          <a href="{item['url']}">{item['title']}</a>
          <p>{item.get('summary_ja', '')}</p>
        </div>"""
    return html


def build_html(digest: dict) -> str:
    today = datetime.now().strftime("%Y年%m月%d日")
    cats = digest.get("categories", {})

    return f"""<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>
  body {{ margin:0; padding:0; background:#f0f2f5; font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif; }}
  .wrapper {{ max-width:680px; margin:24px auto; }}
  .header {{ background:#0f172a; color:white; padding:28px 32px; border-radius:10px 10px 0 0; text-align:center; }}
  .header h1 {{ margin:0; font-size:24px; letter-spacing:.5px; }}
  .header p {{ margin:6px 0 0; opacity:.6; font-size:14px; }}
  .body {{ background:white; padding:28px 32px; border-radius:0 0 10px 10px; }}
  .highlights {{ background:#eff6ff; border-left:4px solid #3b82f6; padding:16px 20px; border-radius:4px; margin-bottom:28px; }}
  .highlights h2 {{ margin:0 0 12px; color:#1e40af; font-size:17px; }}
  .highlight-item {{ margin:12px 0; }}
  .highlight-item a {{ font-weight:600; color:#1d4ed8; text-decoration:none; font-size:15px; }}
  .highlight-item a:hover {{ text-decoration:underline; }}
  .highlight-item p {{ margin:4px 0 0; color:#475569; font-size:13px; line-height:1.6; }}
  h2 {{ font-size:17px; color:#1e293b; border-bottom:2px solid #e2e8f0; padding-bottom:8px; margin:28px 0 16px; }}
  .article-item {{ padding:12px 14px; background:#f8fafc; border-radius:6px; margin:10px 0; }}
  .article-item a {{ color:#2563eb; text-decoration:none; font-weight:500; font-size:14px; }}
  .article-item a:hover {{ text-decoration:underline; }}
  .article-item p {{ margin:5px 0 0; color:#64748b; font-size:13px; line-height:1.6; }}
  .importance-dot {{ font-size:9px; margin-right:6px; }}
  .footer {{ text-align:center; color:#94a3b8; font-size:12px; margin-top:24px; padding-bottom:12px; }}
  .footer a {{ color:#94a3b8; }}
</style>
</head>
<body>
<div class="wrapper">
  <div class="header">
    <h1>🌍 Startup Digest</h1>
    <p>{today} の注目情報</p>
  </div>
  <div class="body">

    <div class="highlights">
      <h2>⭐ 今日のハイライト</h2>
      {_build_highlights_html(digest.get('highlights', []))}
    </div>

    {_build_section(cats.get('startup', []),        '🚀', 'スタートアップ')}
    {_build_section(cats.get('open_innovation', []),'🤝', 'オープンイノベーション')}
    {_build_section(cats.get('accelerator', []),    '🏃', 'アクセラレーター・VC')}

  </div>
  <div class="footer">
    <p>Startup Digest | 毎朝7時配信 | Powered by Gemini &amp; GitHub Actions</p>
  </div>
</div>
</body>
</html>"""


def send_digest(digest: dict) -> None:
    from_email   = os.environ["GMAIL_ADDRESS"]
    app_password = os.environ["GMAIL_APP_PASSWORD"]
    to_email     = os.environ.get("TO_EMAIL", from_email)

    today = datetime.now().strftime("%Y/%m/%d")
    subject = f"🚀 Startup Digest {today} — 今日のスタートアップ注目情報"

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"]    = from_email
    msg["To"]      = to_email
    msg.attach(MIMEText(build_html(digest), "html", "utf-8"))

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(from_email, app_password)
        server.sendmail(from_email, to_email, msg.as_string())
        print(f"[INFO] メール送信完了 → {to_email}")
