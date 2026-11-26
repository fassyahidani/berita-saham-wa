import os
import feedparser
import requests
from google import genai

# 1. Tarik berita saham Indonesia 24 jam terakhir
RSS_URL = "https://news.google.com/rss/search?q=saham+IHSG+OR+emiten+BEI+when:1d&hl=id&gl=ID&ceid=ID:id"
feed = feedparser.parse(RSS_URL)

daftar_berita = []
for entry in feed.entries[:20]:
    daftar_berita.append(f"- {entry.title} ({entry.published})")

teks_berita = "\n".join(daftar_berita)

# 2. Rangkum berita pakai Gemini API
client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

prompt = f"""
Kamu adalah analis pasar modal Indonesia. Rangkum daftar berita saham berikut menjadi morning briefing singkat untuk trader/investor IHSG sebelum pasar buka.
Gunakan bahasa Indonesia yang padat, tanpa format markdown rumit, cukup pakai emoji dan poin.

Format:
📊 SENTIMEN UTAMA IHSG & MAKRO (2-3 poin)
🏢 EMITEN & AKSI KORPORASI SOROTAN (3-5 poin, sebutkan kode saham jika ada)
⚠️ HAL YANG PERLU DIPANTAU HARI INI (1-2 poin)

Daftar berita:
{teks_berita}
"""

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=prompt,
)
ringkasan = response.text

# 3. Kirim hasil rangkuman ke Telegram (BAGIAN YANG BERBEDA)
bot_token = os.environ["TELEGRAM_BOT_TOKEN"]
chat_id = os.environ["TELEGRAM_CHAT_ID"]

url_telegram = f"https://api.telegram.org/bot{bot_token}/sendMessage"
payload = {
    "chat_id": chat_id,
    "text": f"☀️ MORNING BRIEFING SAHAM INDO\n\n{ringkasan[:3800]}"
}

res = requests.post(url_telegram, json=payload)
res.raise_for_status()
print("Berita berhasil dikirim ke Telegram!")
