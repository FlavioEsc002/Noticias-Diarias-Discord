import os
import re
import html
import time
import hashlib
import requests
import feedparser

from datetime import datetime
from zoneinfo import ZoneInfo


WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK")

if not WEBHOOK_URL:
    raise Exception("DISCORD_WEBHOOK não configurado.")


MAX_NOTICIAS_POR_CATEGORIA = 2

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


def extrair_fonte(titulo):
    if " - " in titulo:
        partes = titulo.rsplit(" - ", 1)
        return partes[0], partes[1]

    return titulo, "Fonte não identificada"


def normalizar_titulo(titulo):
    titulo = titulo.lower()
    titulo = re.sub(
        r"[^a-záàâãéèêíïóôõöúçñ0-9 ]",
        "",
        titulo
    )
    titulo = re.sub(r"\s+", " ", titulo)

    return titulo.strip()


def gerar_id(titulo):
    return hashlib.md5(
        normalizar_titulo(titulo).encode("utf-8")
    ).hexdigest()


def enviar_discord(payload):
    resposta = requests.post(
        WEBHOOK_URL,
        json=payload,
        timeout=30
    )

    print("Discord HTTP:", resposta.status_code)

    if resposta.status_code not in (200, 204):
        print(resposta.text)

    resposta.raise_for_status()


def buscar_noticias(url, ids_usados):
    feed = feedparser.parse(url)

    print("Feed encontrado:", len(feed.entries), "itens")

    noticias = []

    for item in feed.entries:
        titulo_original = limpar_texto(
            item.get("title", "")
        )

        if not titulo_original:
            continue

        titulo, fonte = extrair_fonte(
            titulo_original
        )

        id_noticia = gerar_id(
            titulo
        )

        if id_noticia in ids_usados:
            continue

        link = item.get("link", "")

        if not link:
            continue

        titulo = limpar_texto(titulo)
        fonte = limpar_texto(fonte)

        if len(titulo) > 170:
            titulo = titulo[:167] + "..."

        noticias.append({
            "titulo": titulo,
            "fonte": fonte,
            "link": link
        })

        ids_usados.add(
            id_noticia
        )

        if len(noticias) >= MAX_NOTICIAS_POR_CATEGORIA:
            break

    return noticias


agora = datetime.now(
    ZoneInfo("America/Sao_Paulo")
)

ids_usados = set()
categorias_encontradas = []


for categoria, url in CATEGORIAS.items():

    noticias = buscar_noticias(
        url,
        ids_usados
    )

    if noticias:
        categorias_encontradas.append(
            (categoria, noticias)
        )


if not categorias_encontradas:
    enviar_discord({
        "username": "Daily News",
        "content": (
            "⚠️ **Daily News**\n\n"
            "Nenhuma notícia foi encontrada nesta atualização."
        )
    })

    raise SystemExit()


enviar_discord({
    "username": "Daily News",

    "content": (
        "# 📰・DAILY NEWS\n\n"
        f"📅 **{agora.strftime('%d/%m/%Y')}**\n"
        "🕕 Atualização diária das **06:00**\n\n"
        "As principais notícias de tecnologia para começar o dia."
    )
})

time.sleep(1)


total_noticias = 0


for categoria, noticias in categorias_encontradas:

    total_noticias += len(
        noticias
    )

    descricao = ""

    for noticia in noticias:

        descricao += (
            f"### {noticia['titulo']}\n"
            f"📰 **{noticia['fonte']}**\n"
            f"🔗 [Ler notícia]({noticia['link']})\n\n"
        )


    enviar_discord({
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
    })

    time.sleep(1)


enviar_discord({
    "username": "Daily News",

    "content": (
        f"📡 **{total_noticias} notícias selecionadas hoje.**\n"
        "Próxima atualização amanhã às **06:00**."
    )
})


print("Daily News concluído.")
