import os
import requests

WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK")

if not WEBHOOK_URL:
    raise Exception("DISCORD_WEBHOOK não configurado.")

mensagem = """
# 📰・DAILY NEWS

✅ Bot funcionando corretamente!

Esta é uma mensagem de teste enviada automaticamente pelo GitHub Actions.
"""

response = requests.post(
    WEBHOOK_URL,
    json={
        "content": mensagem,
        "username": "Daily News"
    },
    timeout=30
)

print("Status HTTP:", response.status_code)
print("Resposta Discord:", response.text)

response.raise_for_status()

print("Mensagem enviada com sucesso!")
