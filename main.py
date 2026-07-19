from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import os

TOKEN = os.getenv("8975995836:AAERVkAwmLJXYH3G4lbpDIE1AOUcihRwCdo")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Hallo! Mein Bot läuft auf Render.")

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))

app.run_polling()
