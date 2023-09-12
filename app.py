import json, os
from difflib import get_close_matches
import logging
from dotenv import load_dotenv
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import (ApplicationBuilder, CommandHandler, ContextTypes,
                          MessageHandler, filters, CallbackContext)
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

load_dotenv()

word = "Enter word: "

async def start(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    first_name = user.first_name
    # reply_keyboard = [
    #     [KeyboardButton("Button 1")], [KeyboardButton("Button 2")]
    # ]
    # markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True)
    reply_markup = ReplyKeyboardMarkup(
        [[KeyboardButton('Кнопка 1'), KeyboardButton('Кнопка 2')]],
        resize_keyboard=True,  # Разрешить клавиатуре изменять размер
        one_time_keyboard=True  # Клавиатура исчезнет после нажатия
    )
    bot_description = "I'm a bot that provides explanations for words. Simply type a word, and I'll give you its definition"
    welcome_message = f"Hello, {first_name}, {bot_description}!"
    await context.bot.send_message(chat_id=update.effective_chat.id, text=welcome_message, reply_markup=reply_markup)
    await context.bot.send_message(chat_id=update.effective_chat.id, text=word)


data = json.load(open("data.json"))


def translate(w):
    w = w.lower()
    if w in data:
        meanings = data[w]
        formatted_meanings = "\n\n".join([f"{i + 1}. {meaning}" for i, meaning in enumerate(meanings)])
        return formatted_meanings
    elif len(get_close_matches(w, data.keys())) > 0:
        yn = input("Did you mean %s instead? Enter Y if yes, or N if no: " % get_close_matches(w, data.keys())[0])
        if yn == "Y":
            return "\n".join(data[get_close_matches(w, data.keys())[0]])
        elif yn == "N":
            return "The word doesn't exist. Please double check it."
        else:
            return "We didn't understand your entry."
    else:
        return "The word doesn't exist. Please double check it."


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action='typing')
    response = translate(update.message.text)
    await context.bot.send_message(chat_id=update.effective_chat.id, text=response)
    await context.bot.send_message(chat_id=update.effective_chat.id, text=word)


if __name__ == "__main__":
    application = ApplicationBuilder().token(os.getenv('TOKEN')).build()

    start_handler = CommandHandler('start', start)
    echo_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), echo)


    application.add_handler(start_handler)
    application.add_handler(echo_handler)

    application.run_polling()