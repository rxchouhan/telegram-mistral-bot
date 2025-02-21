import os
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, CallbackContext

# Load API keys from environment variables
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")

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

        # Print full API response for debugging
        print("Mistral API Raw Response:", response_json)

        # Ensure the response contains 'choices' and extract content safely
        if isinstance(response_json, dict):
            if "choices" in response_json and response_json["choices"]:
                first_choice = response_json["choices"][0]
                if isinstance(first_choice, dict) and "message" in first_choice and "content" in first_choice["message"]:
                    return first_choice["message"]["content"]
                else:
                    return "Error: No valid response content found."
            elif "error" in response_json:
                return f"Error: {response_json['error'].get('message', 'Unknown API error')}"
        
        return f"Unexpected API response format: {response_json}"

    except requests.exceptions.RequestException as e:
        return f"API Request Error: {str(e)}"
    except Exception as e:
        return f"Unexpected Error: {str(e)}"

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
