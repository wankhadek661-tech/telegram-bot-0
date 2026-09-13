import os
import threading
from flask import Flask
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
)

# -----------------------------
# Telegram Bot
# -----------------------------

TOKEN = os.getenv("BOT_TOKEN")

if not TOKEN:
    raise RuntimeError("BOT_TOKEN environment variable is missing")

app = Flask(__name__)


@app.route("/")
def home():
    return "Telegram bot is running!"


def run_server():
    port = int(os.getenv("PORT", 10000))
    app.run(host="0.0.0.0", port=port)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 Aviator Statistics Bot\n\n"
        "Commands:\n"
        "/analyze 1.20 2.10 1.05 3.40 5.20\n"
        "/help\n\n"
        "⚠️ Analysis is statistical only. "
        "It cannot guarantee the next multiplier."
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Example:\n"
        "/analyze 1.20 1.50 2.30 5.10 1.10 3.20\n\n"
        "The bot calculates average, minimum, maximum "
        "and results below/above selected multipliers."
    )


async def analyze(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        values = []

        for item in context.args:
            value = float(item.replace("x", "").strip())
            if value >= 1:
                values.append(value)

        if len(values) < 2:
            await update.message.reply_text(
                "❌ Kam se kam 2 multipliers bhejo.\n\n"
                "Example:\n"
                "/analyze 1.20 2.10 1.50 3.40 5.20"
            )
            return

        total = len(values)
        average = sum(values) / total
        minimum = min(values)
        maximum = max(values)

        below_2 = sum(v < 2 for v in values)
        above_2 = total - below_2

        below_5 = sum(v < 5 for v in values)
        above_5 = total - below_5

        message = (
            "📊 STATISTICAL ANALYSIS\n\n"
            f"Total results: {total}\n"
            f"Average: {average:.2f}x\n"
            f"Minimum: {minimum:.2f}x\n"
            f"Maximum: {maximum:.2f}x\n\n"
            f"Below 2x: {below_2} ({below_2/total*100:.1f}%)\n"
            f"2x or higher: {above_2} ({above_2/total*100:.1f}%)\n\n"
            f"Below 5x: {below_5} ({below_5/total*100:.1f}%)\n"
            f"5x or higher: {above_5} ({above_5/total*100:.1f}%)\n\n"
            "⚠️ These statistics do NOT predict the next round."
        )

        await update.message.reply_text(message)

    except ValueError:
        await update.message.reply_text(
            "❌ Sirf numbers bhejo.\n\n"
            "Example:\n"
            "/analyze 1.20 2.10 1.50 3.40 5.20"
        )


# -----------------------------
# Start
# -----------------------------

async def post_init(application):
    print("Bot started successfully!")


def main():
    threading.Thread(target=run_server, daemon=True).start()

    application = (
        Application.builder()
        .token(TOKEN)
        .post_init(post_init)
        .build()
    )

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("analyze", analyze))

    application.run_polling()


if __name__ == "__main__":
    main()
