import os
import json
import google.generativeai as genai

PROMPT_TEMPLATE = """
あなたはスタートアップ・オープンイノベーション専門のアナリストです。
以下の記事（英語・日本語混在）を分析し、日本語でダイジェストを作成してください。

【分類ルール】
- startup        : 資金調達・新サービス・IPO・スタートアップ動向
- open_innovation: 大企業×スタートアップ連携・共同研究・CVC
- accelerator    : アクセラレータープログラム・VC投資動向・ピッチイベント

【記事一覧】
{articles_text}

【出力形式】JSONのみ出力してください（```json ブロック不要）:
{{
  "highlights": [
    {{"title": "記事タイトル", "url": "URL", "reason": "選んだ理由（1〜2文）"}}
  ],
  "categories": {{
    "startup":        [{{"title": "タイトル", "url": "URL", "summary_ja": "日本語要約（1〜2文）", "importance": "高/中/低"}}],
    "open_innovation":[{{"title": "タイトル", "url": "URL", "summary_ja": "日本語要約（1〜2文）", "importance": "高/中/低"}}],
    "accelerator":    [{{"title": "タイトル", "url": "URL", "summary_ja": "日本語要約（1〜2文）", "importance": "高/中/低"}}]
  }}
}}

highlights は重要度の高い記事を最大3件選んでください。
"""

def summarize_articles(articles: list[dict]) -> dict:
    genai.configure(api_key=os.environ["GEMINI_API_KEY"])
    model = genai.GenerativeModel("gemini-2.0-flash")

    # 記事をテキスト化（トークン節約のためsummaryは300字以内）
    lines = []
    for i, a in enumerate(articles, 1):
        lines.append(
            f"[{i}] {a['title']}\n"
            f"    出典: {a['source']} | {a['published']}\n"
            f"    URL: {a['url']}\n"
            f"    概要: {a['summary'][:300]}\n"
        )
    articles_text = "\n".join(lines)

    prompt = PROMPT_TEMPLATE.format(articles_text=articles_text)

    response = model.generate_content(prompt)
    raw = response.text.strip()

    # JSON部分の抽出（念のため）
    if "```json" in raw:
        raw = raw.split("```json")[1].split("```")[0].strip()
    elif "```" in raw:
        raw = raw.split("```")[1].split("```")[0].strip()

    try:
        return json.loads(raw)
    except json.JSONDecodeError as e:
        print(f"[ERROR] JSON解析失敗: {e}\n--- raw ---\n{raw}")
        raise
