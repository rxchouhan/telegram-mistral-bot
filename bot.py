import os
import logging
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext

# Load environment variables
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
MISTRAL_MODEL = "mistral-small-latest"

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# Function to format response text for Telegram
def format_response(text):
    # Escape special characters for Telegram MarkdownV2
    escape_chars = "_*[]()~`>#+-=|{}.!"
    for char in escape_chars:
        text = text.replace(char, f"\\{char}")

    # Apply structured formatting
    text = text.replace("### ", "*📌 ")  # H3 → Bold with Emoji  
    text = text.replace("#### ", "🔹 ")  # H4 → Bullet with Emoji  

    # Improve spacing for readability
    text = text.replace("\n", "\n\n")  # Double newlines for better separation  

    return text

# Function to fetch response from Mistral API
def get_mistral_response(user_input):
    try:
        url = "https://api.mistral.ai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {MISTRAL_API_KEY}",
            "Content-Type": "application/json",
        }
        data = {
            "model": MISTRAL_MODEL,
            "messages": [{"role": "user", "content": user_input}],
            "max_tokens": 500,
            "temperature": 0.7,
        }
        response = requests.post(url, json=data, headers=headers)
        response_json = response.json()

        if "choices" in response_json and response_json["choices"]:
            return response_json["choices"][0]["message"]["content"].strip()
        else:
            return "⚠️ *Sorry, no valid response from Mistral.*"

    except Exception as e:
        logger.error(f"Error fetching response: {e}")
        return "⚠️ *An error occurred while processing your request.*"

# Start command
async def start(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text("👋 *Hello!* I'm your AI bot. Send me a message and I'll respond!")

# Message handler
async def handle_message(update: Update, context: CallbackContext) -> None:
    user_message = update.message.text
    bot_response = get_mistral_response(user_message)

    # Format response properly
    formatted_response = format_response(bot_response)
    
    await update.message.reply_text(formatted_response, parse_mode="MarkdownV2")

# Main function to start the bot
def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logger.info("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
