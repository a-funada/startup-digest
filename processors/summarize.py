import os
from groq import Groq

def summarize_articles(articles):
    client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
    
    texts = []
    for a in articles:
        texts.append(f"タイトル: {a['title']}\nURL: {a['url']}\n概要: {a.get('summary', '')}")
    
    prompt = "以下のスタートアップ関連記事を日本語で要約してください。各記事を箇条書きで簡潔にまとめてください。\n\n" + "\n\n---\n\n".join(texts)
    
    chat_completion = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="llama-3.3-70b-versatile",
    )
    
    return chat_completion.choices[0].message.content
