import re
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# Cole seu Token entre as aspas simples abaixo
TOKEN = '8642951065:AAEB_loVdZyQ8knR_FbZhHDiNUcf7y-fMzw'

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.effective_user.first_name
    texto = (
        f"Olá, {user_name}! 👋\n\n"
        "Me envie ou compartilhe aqui o link de um produto do AliExpress.\n"
        "Eu vou buscar a melhor oferta e gerar o seu link com desconto!"
    )
    await update.message.reply_text(texto)

async def processar_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    mensagem = update.message.text

    # Captura links no formato do app ou do site
    padrao_aliexpress = r'(https?://[^\s]*(?:aliexpress\.com|a\.aliexpress\.com)[^\s]*)'
    match = re.search(padrao_aliexpress, mensagem)

    if match:
        link_original = match.group(1)
        await update.message.reply_text("🔎 Processando seu link e buscando ofertas no AliExpress...")

        # Estrutura preparada para receber as credenciais de afiliado
        resposta = (
            "✅ **Produto Encontrado!**\n\n"
            "💰 **Menor Preço Encontrado:** R$ --,--\n"
            "🎟️ **Cupom:** Buscando cupons disponíveis...\n\n"
            f"🔗 **Link com Desconto:** {link_original}"
        )
        await update.message.reply_text(resposta, parse_mode='Markdown')
    else:
        await update.message.reply_text("⚠️ Por favor, envie um link válido do AliExpress.")

def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, processar_link))

    print("Bot rodando...")
    app.run_polling()

if __name__ == '__main__':
    main()