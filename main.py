import os
import logging
from telegram.ext import Application, CommandHandler
from flask import Flask
from threading import Thread

# Web-Server für Render
app = Flask('')
@app.route('/')
def home():
    return "Bot is alive!"
def run():
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)

def main():
    # Starte Web-Server
    t = Thread(target=run)
    t.start()
    
    # Token-Abruf (Achte darauf, dass in Render die Variable exakt so heißt)
    token = os.environ.get("8975995836:AAEhxOhCGXPG4mDWtLtN_7eFx7RrcTMcNJ8")
    
    if not token:
        print("FEHLER: TELEGRAM_TOKEN ist nicht gesetzt!")
        return

    print("Starte Bot...")
    application = Application.builder().token(token).build()
    
    # Hier deine Handler
    # application.add_handler(CommandHandler("start", start_command))
    
    application.run_polling()

if __name__ == '__main__':
    main()
