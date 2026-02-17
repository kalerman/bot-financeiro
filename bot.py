# =========================
# BOT FINANCEIRO TELEGRAM
# =========================

import os
import re
from datetime import datetime
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# =========================
# CONFIGURAÇÃO DO ARQUIVO
# =========================

ARQUIVO = "/tmp/financas.csv"

# Cria o arquivo se não existir
if not os.path.exists(ARQUIVO):
    with open(ARQUIVO, "w", encoding="utf-8") as f:
        f.write("data,tipo,valor,descricao\n")

# =========================
# COMANDOS
# =========================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Olá! Sou seu bot financeiro.\n\n"
        "Você pode escrever normalmente, por exemplo:\n"
        "• paguei 30 lanche\n"
        "• mercado 120\n"
        "• recebi 1000 salário\n\n"
        "Use /saldo ou /resumo para ver seus dados."
    )

async def saldo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    entradas = 0.0
    saidas = 0.0

    with open(ARQUIVO, encoding="utf-8") as f:
        next(f)
        for linha in f:
            _, tipo, valor, _ = linha.strip().split(",", 3)
            valor = float(valor)
            if tipo == "recebi":
                entradas += valor
            else:
                saidas += valor

    saldo_total = entradas - saidas

    await update.message.reply_text(
        f"💰 Saldo atual\n"
        f"➕ Entradas: R$ {entradas:.2f}\n"
        f"➖ Saídas: R$ {saidas:.2f}\n"
        f"✅ Saldo: R$ {saldo_total:.2f}"
    )

async def resumo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    mes_atual = datetime.now().strftime("%Y-%m")
    entradas = 0.0
    saidas = 0.0

    with open(ARQUIVO, encoding="utf-8") as f:
        next(f)
        for linha in f:
            data, tipo, valor, _ = linha.strip().split(",", 3)
            if data.startswith(mes_atual):
                valor = float(valor)
                if tipo == "recebi":
                    entradas += valor
                else:
                    saidas += valor

    saldo_mes = entradas - saidas

    await update.message.reply_text(
        f"📊 Resumo {mes_atual}\n"
        f"➕ Entradas: R$ {entradas:.2f}\n"
        f"➖ Saídas: R$ {saidas:.2f}\n"
        f"✅ Saldo: R$ {saldo_mes:.2f}"
    )

# =========================
# REGISTRO INTELIGENTE
# =========================

async def registrar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        texto = update.message.text.lower()

        # Detecta o primeiro número como valor
        match = re.search(r"\d+[.,]?\d*", texto)
        if not match:
            await update.message.reply_text(
                "❌ Não achei o valor.\nEx: paguei 30 lanche"
            )
            return

        valor = float(match.group().replace(",", "."))

        palavras_gasto = [
            "gastei", "gasto", "paguei", "despesa",
            "mercado", "lanche", "gasolina", "almoço", "jantar"
        ]

        palavras_recebi = [
            "recebi", "entrou", "ganhei",
            "salário", "pix", "venda"
        ]

        if any(p in texto for p in palavras_gasto):
            tipo = "gasto"
        elif any(p in texto for p in palavras_recebi):
            tipo = "recebi"
        else:
            await update.message.reply_text(
                "❌ Não entendi se é gasto ou recebimento.\n"
                "Ex: paguei 30 lanche | recebi 100 pix"
            )
            return

        descricao = texto.replace(match.group(), "").strip()
        data = datetime.now().strftime("%Y-%m-%d")

        with open(ARQUIVO, "a", encoding="utf-8") as f:
            f.write(f"{data},{tipo},{valor},{descricao}\n")

        emoji = "❌" if tipo == "gasto" else "✅"

        await update.message.reply_text(
            f"{emoji} {tipo.capitalize()} registrado\n"
            f"💰 R$ {valor:.2f}\n"
            f"📝 {descricao}"
        )

    except Exception as e:
        await update.message.reply_text("❌ Erro ao registrar")
        print("ERRO:", e)

# =========================
# INICIALIZAÇÃO DO BOT
# =========================

import os
TOKEN = os.getenv("TOKEN")

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("saldo", saldo))
app.add_handler(CommandHandler("resumo", resumo))

# Mensagens de texto (sempre por último)
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, registrar))

print("🤖 Bot rodando...")
app.run_polling()