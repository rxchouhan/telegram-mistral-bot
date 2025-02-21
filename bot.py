import os
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, CallbackContext

# Load API keys from environment variables
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")

# Function to call Mistral API
def get_mistral_response(message):
    url = "https://api.mistral.ai/v1/chat/completions"  # Updated endpoint
    headers = {
        "Authorization": f"Bearer {MISTRAL_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "mistral-small-latest",
        "messages": [{"role": "user", "content": message}],  # Updated payload
        "max_tokens": 100
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        response_json = response.json()

        # Print API response for debugging
        print("Mistral API Raw Response:", response_json)

        # Extract AI-generated text
        if "choices" in response_json and response_json["choices"]:
            return response_json["choices"][0]["message"]["content"]
        elif "error" in response_json:
            return f"Error: {response_json['error']['message']}"
        else:
            return f"Unexpected API response format: {response_json}"

    except Exception as e:
        return f"API Error: {str(e)}"

# Start command
async def start(update: Update, context: CallbackContext):
    await update.message.reply_text("Hello! I am a Telegram bot powered by Mistral AI. Send me a message!")

# Message handler
async def handle_message(update: Update, context: CallbackContext):
    user_message = update.message.text
    bot_response = get_mistral_response(user_message)
    await update.message.reply_text(bot_response)

# Main function to start the bot
def main():
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
