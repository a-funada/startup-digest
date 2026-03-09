import os
import json
from groq import Groq

def summarize_articles(articles):
    client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
    
    texts = []
    for a in articles:
        texts.append(f"タイトル: {a['title']}\nURL: {a['url']}\n概要: {a.get('summary', '')}")
    
    prompt = """以下のスタートアップ関連記事を分析し、必ず以下のJSON形式のみで返してください。他のテキストは一切含めないでください。

{
  "highlights": [
    {"title": "記事タイトル", "url": "URL", "reason": "注目理由"}
  ],
  "categories": {
    "startup": [
      {"title": "記事タイトル", "url": "URL", "summary_ja": "日本語要約", "importance": "高"}
    ],
    "open_innovation": [],
    "accelerator": []
  }
}

記事一覧:
""" + "\n\n---\n\n".join(texts)
    
    chat_completion = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="llama-3.3-70b-versatile",
    )
    
    content = chat_completion.choices[0].message.content
    # JSON部分を抽出
    start = content.find("{")
    end = content.rfind("}") + 1
    json_str = content[start:end]
    return json.loads(json_str)
