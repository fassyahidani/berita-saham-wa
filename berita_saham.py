import os
import feedparser
import requests
from google import genai

# 1. Tarik berita saham Indonesia 24 jam terakhir via Google News RSS
RSS_URL = "https://news.google.com/rss/search?q=saham+IHSG+OR+emiten+BEI+when:1d&hl=id&gl=ID&ceid=ID:id"
feed = feedparser.parse(RSS_URL)

daftar_berita = []
for entry in feed.entries[:20]:  # Ambil 20 berita teratas
    daftar_berita.append(f"- {entry.title} ({entry.published})\n  Link: {entry.link}")

teks_berita = "\n".join(daftar_berita)

# 2. Rangkum berita pakai Gemini API
client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

prompt = f"""
Kamu adalah analis pasar modal Indonesia. Rangkum daftar berita saham berikut menjadi morning briefing singkat untuk trader/investor IHSG sebelum pasar buka.

Format output (gunakan bahasa Indonesia yang padat, tanpa format markdown rumit, cukup pakai emoji dan poin):
📊 SENTIMEN UTAMA IHSG & MAKRO (2-3 poin)
🏢 AKSI KORPORASI & EMITEN SOROTAN (3-5 poin, sebutkan kode saham jika ada)
⚠️ RISIKO / HAL YANG PERLU DIPANTAU HARI INI (1-2 poin)

Daftar berita:
{teks_berita}
"""

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=prompt,
)
ringkasan = response.text

import urllib.parse

# ... (bagian 1 & 2 tarik RSS dan rangkum Gemini tetap sama persis) ...

# 3. Kirim hasil rangkuman ke WhatsApp via CallMeBot
wa_phone = os.environ["WA_PHONE"]       # Format: 6281234567890 (tanpa tanda +)
wa_apikey = os.environ["WA_API_KEY"]

# Gabungkan judul dan ringkasan, lalu encode agar aman dikirim lewat URL
pesan = f"☀️ *MORNING BRIEFING SAHAM INDO*\n\n{ringkasan[:1500]}"
pesan_encoded = urllib.parse.quote(pesan)

url_wa = f"https://api.callmebot.com/whatsapp.php?phone={wa_phone}&text={pesan_encoded}&apikey={wa_apikey}"

res = requests.get(url_wa)
res.raise_for_status()
print("Berita berhasil dikirim ke WhatsApp!")