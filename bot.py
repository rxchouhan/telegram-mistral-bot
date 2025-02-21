import os
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, CallbackContext

# Load API keys from environment variables
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")

# Function to format Mistral API response in MarkdownV2
def format_response(text):
    # Escape special MarkdownV2 characters
    escape_chars = "_*[]()~`>#+-=|{}.!"
    for char in escape_chars:
        text = text.replace(char, f"\\{char}")
    
    # Preserve line breaks for better readability
    text = text.replace("\n", "\n\n")
    return text

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
        "max_tokens": 500  # Allows longer responses
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        response_json = response.json()

        # Print full API response for debugging
        print("Mistral API Raw Response:", response_json)

        # Extract content safely
        if isinstance(response_json, dict) and "choices" in response_json:
            choices = response_json["choices"]
            if choices and isinstance(choices[0], dict):
                message_data = choices[0].get("message", {})
                content = message_data.get("content", "Error: No valid response content found.")
                return format_response(content)
        
        return f"Unexpected API response format: {response_json}"

    except requests.exceptions.RequestException as e:
        return f"API Request Error: {str(e)}"
    except Exception as e:
        return f"Unexpected Error: {str(e)}"

# Start command
async def start(update: Update, context: CallbackContext):
    await update.message.reply_text("Hello! I am a Telegram bot powered by Mistral AI. Send me a message!")

# Message handler with proper Markdown formatting
async def handle_message(update: Update, context: CallbackContext):
    user_message = update.message.text

    # Prevent duplicate responses
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
