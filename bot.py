import os
import requests
import re
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, CallbackContext

# Load API keys from environment variables
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")

def escape_markdown_v2(text):
    """Escapes special characters for Telegram MarkdownV2."""
    special_chars = "_*[]()~`>#+-=|{}.!"
    return "".join(f"\\{char}" if char in special_chars else char for char in text)

def format_response(text):
    """Formats API response for Telegram with proper MarkdownV2."""
    if not text:
        return "Error: No valid response content found."

    # Convert headers
    text = re.sub(r"(?m)^###\s*", "📌 ", text)  # Convert ### to 📌
    text = re.sub(r"(?m)^####\s*", "🔹 ", text)  # Convert #### to 🔹

    # Convert **bold** to Telegram *bold* format
    text = re.sub(r"\*\*(.*?)\*\*", r"*\1*", text)

    # Escape Telegram MarkdownV2 special characters
    return escape_markdown_v2(text)

# Function to call Mistral API
def get_mistral_response(message):
    url = "https://api.mistral.ai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {MISTRAL_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "mistral-small-latest",
        "messages": [{"role": "user", "content": message}],
        "max_tokens": 100
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        response_json = response.json()

        print("Mistral API Raw Response:", response_json)  # Debugging

        if isinstance(response_json, dict) and "choices" in response_json:
            choices = response_json["choices"]
            if choices and isinstance(choices[0], dict):
                message_data = choices[0].get("message", {})
                raw_text = message_data.get("content", "Error: No valid response content found.")
                return format_response(raw_text)  # Apply formatting
        
        return f"Unexpected API response format: {response_json}"

    except requests.exceptions.RequestException as e:
        return f"API Request Error: {escape_markdown_v2(str(e))}"
    except Exception as e:
        return f"Unexpected Error: {escape_markdown_v2(str(e))}"

# Start command
async def start(update: Update, context: CallbackContext):
    await update.message.reply_text("Hello! I am a Telegram bot powered by Mistral AI. Send me a message!")

# Message handler with duplicate message prevention
async def handle_message(update: Update, context: CallbackContext):
    user_message = update.message.text

    if "processed_messages" not in context.bot_data:
        context.bot_data["processed_messages"] = set()

    if update.message.message_id in context.bot_data["processed_messages"]:
        print("Duplicate message detected, ignoring...")
        return

    context.bot_data["processed_messages"].add(update.message.message_id)

    bot_response = get_mistral_response(user_message)
    await update.message.reply_text(bot_response, parse_mode="MarkdownV2")

# Main function to start the bot
def main():
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
