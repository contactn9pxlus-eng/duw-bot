import os
import logging
from telegram.ext import Application, CommandHandler
from flask import Flask
from threading import Thread

# Web-Server für Render (damit Render den Bot nicht stoppt)
app = Flask('')
@app.route('/')
def home():
    return "Bot is alive!"
def run():
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 10000)))

# Haupt-Funktion
def main():
    # Starte den Web-Server
    t = Thread(target=run)
    t.start()
    
    # Token laden
    token = os.environ.get("8975995836:AAEhxOhCGXPG4mDWtLtN_7eFx7RrcTMcNJ8")
    if not token:
        print("FEHLER: TELEGRAM_TOKEN wurde in den Einstellungen nicht gefunden!")
        return
    
    # Bot starten
    print("Bot startet Polling...")
    application = Application.builder().token(token).build()
    
    # Hier deine Handler-Funktionen hinzufügen (start_command, etc.)
    # application.add_handler(CommandHandler("start", start_command))
    
    application.run_polling()

if __name__ == '__main__':
    main()
