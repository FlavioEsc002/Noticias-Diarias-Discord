import os
import re
import html
import time
import hashlib
import requests
import feedparser

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from email.utils import parsedate_to_datetime


WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK")

if not WEBHOOK_URL:
    raise Exception("DISCORD_WEBHOOK não configurado.")


MAX_NOTICIAS_POR_CATEGORIA = 2
MAX_IDADE_HORAS = 48

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

    return titulo, "Fonte"


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
    titulo = normalizar_titulo(titulo)

    return hashlib.md5(
        titulo.encode("utf-8")
    ).hexdigest()


def obter_data(item):
    if item.get("published"):
        try:
            data = parsedate_to_datetime(
                item.published
            )

            if data.tzinfo is None:
                data = data.replace(
                    tzinfo=ZoneInfo(
                        "America/Sao_Paulo"
                    )
                )

            return data

        except Exception:
            pass

    return None


def enviar_discord(payload):
    resposta = requests.post(
        WEBHOOK_URL,
        json=payload,
        timeout=30
    )

    print(
        "Discord HTTP:",
        resposta.status_code
    )

    if resposta.status_code not in (200, 204):
        print(resposta.text)

    resposta.raise_for_status()


def buscar_noticias(url, ids_usados):
    feed = feedparser.parse(url)

    agora = datetime.now(
        ZoneInfo("America/Sao_Paulo")
    )

    limite = agora - timedelta(
        hours=MAX_IDADE_HORAS
    )

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

        data = obter_data(item)

        if data:
            data_sp = data.astimezone(
                ZoneInfo("America/Sao_Paulo")
            )

            if data_sp < limite:
                continue

        link = item.get(
            "link",
            ""
        )

        if not link:
            continue

        titulo = limpar_texto(titulo)
        fonte = limpar_texto(fonte)

        if len(titulo) > 170:
            titulo = titulo[:167] + "..."

        noticias.append({
            "titulo": titulo,
            "fonte": fonte,
            "link": link,
            "data": data
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


cabecalho = {
    "username": "Daily News",

    "content": (
        "# 📰・DAILY NEWS\n\n"
        f"📅 **{agora.strftime('%d/%m/%Y')}**\n"
        "🕕 Atualização diária das **06:00**\n\n"
        "As principais notícias de tecnologia para começar o dia."
    )
}


enviar_discord(
    cabecalho
)

time.sleep(1)

total_noticias = 0


for categoria, url in CATEGORIAS.items():

    noticias = buscar_noticias(
        url,
        ids_usados
    )

    if not noticias:
        continue

    total_noticias += len(
        noticias
    )

    descricao = ""

    for noticia in noticias:
        descricao += (
            f"### {noticia['titulo']}\n"
            f"📰 **{noticia['fonte']}**\n"
            f"🔗 [Ler notícia completa]({noticia['link']})\n\n"
        )

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

    enviar
