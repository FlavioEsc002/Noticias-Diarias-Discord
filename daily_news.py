import os
import re
import html
import requests
import feedparser
from datetime import datetime
from zoneinfo import ZoneInfo

WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK")

if not WEBHOOK_URL:
    raise Exception("DISCORD_WEBHOOK não configurado.")

CATEGORIAS = {
    "🤖 Inteligência Artificial": [
        "https://news.google.com/rss/search?q=inteligencia+artificial+OR+OpenAI+OR+ChatGPT&hl=pt-BR&gl=BR&ceid=BR:pt-419"
    ],
    "💻 Tecnologia": [
        "https://news.google.com/rss/search?q=tecnologia&hl=pt-BR&gl=BR&ceid=BR:pt-419"
    ],
    "🔐 Cibersegurança": [
        "https://news.google.com/rss/search?q=ciberseguranca+OR+vulnerabilidade+OR+hacker&hl=pt-BR&gl=BR&ceid=BR:pt-419"
    ],
    "👨‍💻 Programação": [
        "https://news.google.com/rss/search?q=programacao+OR+desenvolvimento+software+OR+GitHub&hl=pt-BR&gl=BR&ceid=BR:pt-419"
    ],
    "🖥️ Hardware": [
        "https://news.google.com/rss/search?q=hardware+OR+Nvidia+OR+AMD+OR+Intel&hl=pt-BR&gl=BR&ceid=BR:pt-419"
    ],
    "🎮 Games": [
        "https://news.google.com/rss/search?q=games+OR+PlayStation+OR+Xbox+OR+Nintendo+OR+GTA&hl=pt-BR&gl=BR&ceid=BR:pt-419"
    ]
}


def limpar_texto(texto):
    if not texto:
        return ""

    texto = html.unescape(texto)
    texto = re.sub(r"<[^>]+>", "", texto)
    texto = re.sub(r"\s+", " ", texto)

    return texto.strip()


def buscar_noticias(url, quantidade=2):
    feed = feedparser.parse(url)

    noticias = []

    for item in feed.entries[:quantidade]:
        titulo = limpar_texto(item.get("title", "Sem título"))
        link = item.get("link", "")

        noticias.append({
            "titulo": titulo,
            "link": link
        })

    return noticias


def criar_embeds():
    agora = datetime.now(
        ZoneInfo("America/Sao_Paulo")
    )

    embeds = []

    for categoria, feeds in CATEGORIAS.items():

        noticias = []

        for feed in feeds:
            noticias.extend(buscar_noticias(feed))

        if not noticias:
            continue

        descricao = ""

        for noticia in noticias[:2]:
            descricao += (
                f"**{noticia['titulo']}**\n"
                f"[🔗 Ler notícia]({noticia['link']})\n\n"
            )

        embeds.append({
            "title": categoria,
            "description": descricao,
            "color": 3447003
        })

    embeds.insert(0, {
        "title": "📰 DAILY NEWS",
        "description": (
            f"Principais notícias para começar o dia.\n\n"
            f"📅 {agora.strftime('%d/%m/%Y')}\n"
            f"🕕 Atualização das 06:00"
        ),
        "color": 3447003
    })

    return embeds


payload = {
    "username": "Daily News",
    "content": "## 📰 Bom dia! Seu resumo diário já está disponível.",
    "embeds": criar_embeds()
}

response = requests.post(
    WEBHOOK_URL,
    json=payload,
    timeout=30
)

print("Status HTTP:", response.status_code)
print("Resposta:", response.text)

response.raise_for_status()

print("Daily News enviado com sucesso!")
