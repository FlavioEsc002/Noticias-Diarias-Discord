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


# =========================
# CONFIGURAÇÕES
# =========================

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


# =========================
# FUNÇÕES
# =========================

def limpar_texto(texto):

    texto = html.unescape(texto or "")

    texto = re.sub(
        r"<[^>]+>",
        "",
        texto
    )

    texto = re.sub(
        r"\s+",
        " ",
        texto
    )

    return texto.strip()


def extrair_fonte(titulo):

    if " - " in titulo:
