from telegram import Update, ForceReply
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, ConversationHandler
from googletrans import Translator

# Constants for conversation states
SELECT_LANGUAGE, CHAT = range(2)

# Dictionary to store user chat states and preferences
user_sessions = {}

translator = Translator()

def start(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    user_sessions[user.id] = {'partner': None, 'language': 'en'}  # default language English
    update.message.reply_text(
        'Welcome to the Translator Bot. Please enter the language code (e.g., "es" for Spanish) you want to communicate in:',
        reply_markup=ForceReply(selective=True),
    )
    return SELECT_LANGUAGE

def select_language(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    language = update.message.text.lower()
    user_sessions[user.id]['language'] = language
    update.message.reply_text(f'Language set to {language}. Please start sending messages. Send /cancel to end chat.')
    return CHAT

def chat(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    message = update.message.text
    partner_id = user_sessions[user.id]['partner']
    if partner_id:
        target_language = user_sessions[partner_id]['language']
        translated_text = translator.translate(message, dest=target_language).text
        context.bot.send_message(chat_id=partner_id, text=translated_text)
    return CHAT

def cancel(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    update.message.reply_text('Chat ended.')
    if user.id in user_sessions:
        del user_sessions[user.id]
    return ConversationHandler.END

def main():
    TOKEN = '7074974145:AAFZg1WAK3Tw9c6WQKLNudPoMz1yqlnajKk'
    updater = Updater(TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            SELECT_LANGUAGE: [MessageHandler(Filters.text & ~Filters.command, select_language)],
            CHAT: [MessageHandler(Filters.text & ~Filters.command, chat)]
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    dispatcher.add_handler(conv_handler)

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
