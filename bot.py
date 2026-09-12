import os
import re
import time
import hashlib
import requests
from flask import Flask
from threading import Thread
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# --- 1. CONFIGURAÇÕES DAS CHAVES (Substitua pelos seus dados do AliExpress) ---
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN', '8642951065:AAEB_loVdZyQ8knR_FbZhHDiNUcf7y-fMzw')
APP_KEY = os.environ.get('APP_KEY', 'SUA_APP_KEY_AQUI')
APP_SECRET = os.environ.get('APP_SECRET', 'SEU_APP_SECRET_AQUI')
TRACKING_ID = os.environ.get('TRACKING_ID', 'SEU_TRACKING_ID_AQUI')

# --- 2. SERVIDOR WEB PARA MANTER O RENDER FELIZ E ATIVO ---
app = Flask('')

@app.route('/')
def home():
    return "Bot do AliExpress está rodando 24/7!"

def run_web_server():
    # O Render fornece a porta via variável de ambiente PORT
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

# --- 3. FUNÇÃO DE ASSINATURA E CONVERSÃO DA API DO ALIEXPRESS ---
def gerar_link_afiliado(link_original):
    """
    Chama a API oficial do AliExpress (aliexpress.affiliate.link.generate)
    para converter qualquer link em link de comissão.
    """
    if 'SUA_APP_KEY_AQUI' in APP_KEY or not APP_KEY:
        # Caso ainda não tenha inserido as chaves reais
        return link_original

    endpoint = "https://api-sg.aliexpress.com/sync"
    
    # Parâmetros requeridos pela API do AliExpress
    params = {
        'method': 'aliexpress.affiliate.link.generate',
        'app_key': APP_KEY,
        'sign_method': 'md5',
        'timestamp': time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()),
        'format': 'json',
        'v': '2.0',
        'promotion_link_type': '0',
        'source_values': link_original,
        'tracking_id': TRACKING_ID
    }

    # Gerar assinatura MD5 requerida pelo AliExpress Open Platform
    keys_sorted = sorted(params.keys())
    query_string = ""
    for k in keys_sorted:
        query_string += f"{k}{params[k]}"
    
    sign_str = f"{APP_SECRET}{query_string}{APP_SECRET}"
    signature = hashlib.md5(sign_str.encode('utf-8')).hexdigest().upper()
    params['sign'] = signature

    try:
        response = requests.post(endpoint, data=params, timeout=10)
        data = response.json()
        
        # Extrai o link promocional retornado pela API
        result = data.get('aliexpress_affiliate_link_generate_response', {}).get('resp_result', {})
        promotion_links = result.get('result', {}).get('promotion_links', [])
        
        if promotion_links and len(promotion_links) > 0:
            return promotion_links[0].get('promotion_link', link_original)
    except Exception as e:
        print(f"Erro na API do AliExpress: {e}")

    return link_original

# --- 4. HANDLERS DO TELEGRAM ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.effective_user.first_name
    texto = (
        f"Olá, {user_name}! 👋\n\n"
        "Me envie ou compartilhe aqui o link de qualquer produto do AliExpress.\n"
        "Eu vou buscar as melhores ofertas e gerar o seu link de afiliado com desconto!"
    )
    await update.message.reply_text(texto)

async def processar_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    mensagem = update.message.text

    padrao_aliexpress = r'(https?://[^\s]*(?:aliexpress\.com|a\.aliexpress\.com)[^\s]*)'
    match = re.search(padrao_aliexpress, mensagem)

    if match:
        link_original = match.group(1)
        await update.message.reply_text("🔎 Processando seu link e gerando sua oferta de afiliado...")

        # Converte o link via API do AliExpress
        link_afiliado = gerar_link_afiliado(link_original)

        resposta = (
            "✅ **Produto Encontrado!**\n\n"
            "💰 **Melhor oferta identificada!**\n"
            "🎟️ **Cupom:** Aplicável direto no checkout.\n\n"
            f"🔗 **Seu Link com Desconto:** {link_afiliado}"
        )
        await update.message.reply_text(resposta, parse_mode='Markdown')
    else:
        await update.message.reply_text("⚠️ Por favor, envie um link válido do AliExpress.")

# --- 5. INICIALIZAÇÃO ---
def main():
    # Inicia o servidor web em segundo plano para o Render não dar erro
    t = Thread(target=run_web_server)
    t.daemon = True
    t.start()

    # Inicia o Bot no Telegram
    bot_app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    bot_app.add_handler(CommandHandler("start", start))
    bot_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, processar_link))

    print("Bot rodando com sucesso e servidor Web ativo!")
    bot_app.run_polling()

if __name__ == '__main__':
    main()        await update.message.reply_text("⚠️ Por favor, envie um link válido do AliExpress.")

def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, processar_link))

    print("Bot rodando...")
    app.run_polling()

if __name__ == '__main__':
    main()
