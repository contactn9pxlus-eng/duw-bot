import os
import logging
import nest_asyncio
import json
import urllib.request
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import mplfinance as mpf
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, CallbackQueryHandler
from flask import Flask
from threading import Thread

# --- Web-Server für Render (Keep Alive) ---
app = Flask('')
@app.route('/')
def home():
    return "Bot is alive!"
def run():
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
def keep_alive():
    t = Thread(target=run)
    t.start()

# --- Setup ---
nest_asyncio.apply()
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)

ADMIN_ID = 8453096596
ALLOWED_USERS = set()

def has_access(user_id):
    return user_id in ALLOWED_USERS or user_id == ADMIN_ID or ADMIN_ID == 0

# --- Chart Engine (dein Code bleibt gleich) ---
def draw_pure_matplotlib_chart(coin_name):
    np.random.seed(1337)
    periods = 60
    prices = 0.085 + 0.01 * np.cumsum(np.random.randn(periods))
    prices = np.clip(prices, 0.06, 0.12)
    df = pd.DataFrame(index=range(periods))
    df['Close'] = prices
    df['Open'] = prices + np.random.uniform(-0.003, 0.003, periods)
    df['High'] = df[['Open', 'Close']].max(axis=1) + np.random.uniform(0, 0.002, periods)
    df['Low'] = df[['Open', 'Close']].min(axis=1) - np.random.uniform(0, 0.002, periods)
    fig, ax = plt.subplots(figsize=(12, 6), dpi=100)
    fig.patch.set_facecolor('black')
    ax.set_facecolor('black')
    ax.grid(color='#1c1c1c', linestyle='-', linewidth=1)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color('gray')
    ax.spines['bottom'].set_color('gray')
    ax.tick_params(colors='white', labelsize=10)
    for i in range(periods):
        open_p, close_p = df['Open'].iloc[i], df['Close'].iloc[i]
        high_p, low_p = df['High'].iloc[i], df['Low'].iloc[i]
        color = 'white' if close_p >= open_p else '#0026ff'
        ax.plot([i, i], [low_p, high_p], color=color, linewidth=1)
        ax.fill_between([i-0.3, i+0.3], open_p, close_p, color=color, edgecolor=color)
    ax.text(0.01, 1.05, f"{coin_name.upper()}/USDT - 1H", transform=ax.transAxes, color='white', fontsize=14, fontweight='bold', ha='left')
    ax.set_xticks([])
    out = f"chart_{coin_name}.png"
    plt.savefig(out, bbox_inches='tight', facecolor='black', dpi=100)
    plt.close()
    return out

def fetch_live_chart_built_in(coin_name):
    symbol = f"{coin_name.upper()}USDT"
    url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval=1h&limit=80"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=4) as response:
            data = json.loads(response.read().decode())
        extracted = [[pd.to_datetime(c[0], unit='ms'), float(c[1]), float(c[2]), float(c[3]), float(c[4])] for c in data]
        df = pd.DataFrame(extracted, columns=['timestamp', 'Open', 'High', 'Low', 'Close']).set_index('timestamp')
        colors = mpf.make_marketcolors(up='white', down='#0026ff', edge='inherit', wick='inherit')
        custom_style = mpf.make_mpf_style(marketcolors=colors, facecolor='black', figcolor='black', gridcolor='#1c1c1c', rc={'text.color': 'white'})
        fig, ax = mpf.plot(df, type='candle', style=custom_style, returnfig=True, figsize=(11, 5.5))
        ax[0].set_title(f"{coin_name.upper()}/USDT - 1H", loc='left', color='white', fontsize=14, fontweight='bold')
        out = f"chart_{coin_name}.png"
        plt.savefig(out, bbox_inches='tight', facecolor='black', dpi=100)
        plt.close()
        return out
    except Exception:
        return draw_pure_matplotlib_chart(coin_name)

# --- Commands ---
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global ADMIN_ID
    user_id = update.effective_user.id
    if ADMIN_ID == 0: ADMIN_ID = user_id
    if not has_access(user_id):
        await update.message.reply_text("⛔ *Access Denied.*")
        return
    await update.message.reply_text("👋 *Bot is ready!*", parse_mode="Markdown")

async def handle_signal(update: Update, context: ContextTypes.DEFAULT_TYPE, is_long: bool):
    user_id = update.effective_user.id
    if not has_access(user_id): return
    args = context.args
    if len(args) < 1: return
    coin = args[0].upper()
    status = await update.message.reply_text(f"🔄 Generating chart...")
    path = fetch_live_chart_built_in(coin)
    with open(path, 'rb') as p:
        await update.message.reply_photo(photo=p)
    os.remove(path)
    await status.delete()

# --- Main Engine ---
def main():
    keep_alive()  # <--- Startet den Web-Server für Render
    token = os.environ.get("T8975995836:AAEhxOhCGXPG4mDWtLtN_7eFx7RrcTMcNJ8")
    if not token:
        print("FEHLER: TELEGRAM_TOKEN wurde nicht gefunden!")
        return
    
    app = Application.builder().token(token).build()
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("long", lambda u, c: handle_signal(u, c, True)))
    app.add_handler(CommandHandler("short", lambda u, c: handle_signal(u, c, False)))
    
    print("Bot läuft...")
    app.run_polling()

if __name__ == '__main__':
    main()
