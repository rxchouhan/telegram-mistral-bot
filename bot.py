import os
import logging
import re
import requests
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, CallbackContext, CommandHandler

# Load environment variables
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
MISTRAL_MODEL = "mistral-small-latest"

# Configure logging
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

def format_response(text):
    """Formats response text for Telegram using MarkdownV2."""
    escape_chars = "_~`>#+-=|{}.!"
    for char in escape_chars:
        text = text.replace(char, f"\\{char}")

    # Convert headings and bold text
    text = text.replace("### ", "📌 ")  # Convert ### to 📌
    text = re.sub(r"\*\*(.*?)\*\*", r"*\1*", text)  # Convert **bold** to *bold*

    return text

def get_mistral_response(prompt):
    """Fetches a response from Mistral API."""
    try:
        headers = {
            "Authorization": f"Bearer {MISTRAL_API_KEY}",
            "Content-Type": "application/json",
        }
        data = {
            "model": MISTRAL_MODEL,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 500,
        }
        response = requests.post("https://api.mistral.ai/v1/chat/completions", json=data, headers=headers)
        response_json = response.json()
        return response_json["choices"][0]["message"]["content"].strip()
    except Exception as e:
        logger.error(f"Error fetching response from Mistral: {e}")
        return "Sorry, I couldn't generate a response."

async def handle_message(update: Update, context: CallbackContext):
    """Handles incoming messages and responds with AI-generated text."""
    user_message = update.message.text
    ai_response = get_mistral_response(user_message)
    formatted_response = format_response(ai_response)
    await update.message.reply_text(formatted_response, parse_mode="MarkdownV2")

async def start(update: Update, context: CallbackContext):
    """Handles the /start command."""
    welcome_message = "Hello! I'm your AI bot. Ask me anything."
    await update.message.reply_text(welcome_message)

def main():
    """Main function to start the bot."""
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    logger.info("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
