import requests
import os
from telegram import Update
from telegram.ext import Updater, MessageHandler, Filters, CallbackContext

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
MISTRAL_API_URL = "https://api.mistral.ai/v1/chat/completions"

def get_mistral_response(prompt):
    headers = {"Authorization": f"Bearer {MISTRAL_API_KEY}", "Content-Type": "application/json"}
    data = {"model": "mistral-small", "messages": [{"role": "user", "content": prompt}]}
    response = requests.post(MISTRAL_API_URL, json=data, headers=headers)
    return response.json().get("choices", [{}])[0].get("message", {}).get("content", "No response")

def handle_message(update: Update, context: CallbackContext):
    user_message = update.message.text
    ai_response = get_mistral_response(user_message)
    update.message.reply_text(ai_response)

def main():
    updater = Updater(TELEGRAM_BOT_TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
