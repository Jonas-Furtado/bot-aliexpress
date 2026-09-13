import os
import logging
from flask import Flask
from threading import Thread
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# Configuração de logs
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Servidor Flask para manter o Render ativo no plano gratuito
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot AliExpress está rodando 24/7!"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

# Lógica do Telegram Bot
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Olá! Envie um link do AliExpress para gerar seu link codificado.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    tracking_id = os.environ.get("TRACKING_ID", "teste")
    
    if "aliexpress.com" in text or "a.aliexpress.com" in text:
        # Gera o link formatado com o parâmetro de tracking
        link = f"https://s.click.aliexpress.com/e/_teste?tracking_id={tracking_id}"
        await update.message.reply_text(f"Aqui está o seu link formatado:\n{link}")
    else:
        await update.message.reply_text("Por favor, envie um link válido do AliExpress.")

def main():
    token = os.environ.get("TELEGRAM_TOKEN")
    if not token:
        raise ValueError("TELEGRAM_TOKEN não configurado!")

    # Inicia o servidor web em segundo plano
    Thread(target=run_flask).start()

    # Inicia o bot do Telegram
    application = ApplicationBuilder().token(token).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    application.run_polling()

if __name__ == "__main__":
    main()
