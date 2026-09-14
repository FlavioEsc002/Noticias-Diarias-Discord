import os
import re
import html
import time
import requests
import feedparser
from datetime import datetime
from zoneinfo import ZoneInfo

WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK")

if not WEBHOOK_URL:
    raise Exception("DISCORD_WEBHOOK não configurado.")

CATEGORIAS = {
    "🤖 Inteligência Artificial":
        "https://news.google.com/rss/search?q=inteligencia+artificial+OR+OpenAI+OR+ChatGPT&hl=pt-BR&gl=BR&ceid=BR:pt-419",

    "💻 Tecnologia":
        "https://news.google.com/rss/search?q=tecnologia&hl=pt-BR&gl=BR&ceid=BR:pt-419",

    "🔐 Cibersegurança":
        "https://news.google.com/rss/search?q=ciberseguranca+OR+vulnerabilidade+OR+hacker&hl=pt-BR&gl=BR&ceid=BR:pt-419",

    "👨‍💻 Programação":
        "https://news.google.com/rss/search?q=programacao+OR+desenvolvimento+software+OR+GitHub&hl=pt-BR&gl=BR&ceid=BR:pt-419",

    "🖥️ Hardware":
        "https://news.google.com/rss/search?q=hardware+OR+Nvidia+OR+AMD+OR+Intel&hl=pt-BR&gl=BR&ceid=BR:pt-419",

    "🎮 Games":
        "https://news.google.com/rss/search?q=games+OR+PlayStation+OR+Xbox+OR+Nintendo+OR+GTA&hl=pt-BR&gl=BR&ceid=BR:pt-419"
}


def limpar_texto(texto):
    texto = html.unescape(texto or "")
    texto = re.sub(r"<[^>]+>", "", texto)
    texto = re.sub(r"\s+", " ", texto)
    return texto.strip()


def enviar(payload):
    resposta = requests.post(
        WEBHOOK_URL,
        json=payload,
        timeout=30
    )

    print("Status:", resposta.status_code)

    if resposta.status_code not in (200, 204):
        print("Resposta:", resposta.text)

    resposta.raise_for_status()


agora = datetime.now(
    ZoneInfo("America/Sao_Paulo")
)

# Cabeçalho
enviar({
    "username": "Daily News",
    "content": (
        "# 📰・DAILY NEWS\n"
        f"📅 **{agora.strftime('%d/%m/%Y')}**\n"
        "🕕 Atualização diária das **06:00**\n\n"
        "Principais notícias de tecnologia para começar o dia."
    )
})

time.sleep(1)

# Categorias
for categoria, url in CATEGORIAS.items():

    feed = feedparser.parse(url)

    noticias = []

    for item in feed.entries[:2]:

        titulo = limpar_texto(
            item.get("title", "Sem título")
        )

        link = item.get("link", "")

        # Evita títulos gigantes
        if len(titulo) > 180:
            titulo = titulo[:177] + "..."

        noticias.append(
            f"**{titulo}**\n"
            f"🔗 [Ler notícia]({link})"
        )

    if not noticias:
        continue

    descricao = "\n\n".join(noticias)

    payload = {
        "username": "Daily News",
        "embeds": [
            {
                "title": categoria,
                "description": descricao,
                "color": 3447003,
                "footer": {
                    "text": "Daily News • ADS"
                }
            }
        ]
    }

    enviar(payload)

    # Pequena pausa para evitar limite de requisições
    time.sleep(1)


print("Daily News enviado com sucesso!")
