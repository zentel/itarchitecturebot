from settings import settings
from telegram import ParseMode, Emoji
from telegram.ext import Updater, CommandHandler

updater = Updater(settings.token)
dispatcher = updater.dispatcher

def start(bot, update):
    #Home message
    msg = "Hello {user_name}! I'm {bot_name}. \n"
    msg += "What would you like to do? \n"
    msg += "/projects - List your projects \n"
    msg += "/addproject + projectname - Add a projet \n"
    msg += "/help - This message"

    # Send the message
    bot.send_message(chat_id=update.message.chat_id,
                     text=msg.format(
                         user_name=update.message.from_user.first_name,
                         bot_name=bot.name))

def help(bot, update):
    #Help message
    msg = "Commands: \n"
    msg += "/projects - List your projects \n"
    msg += "/addproject + projectname - Add a projet \n"
    msg += "/help - This message"

    # Send the message
    bot.send_message(chat_id=update.message.chat_id,
                     text=msg.format(
                         user_name=update.message.from_user.first_name,
                         bot_name=bot.name))

# Add handlers to dispatcher
dispatcher.add_handler(CommandHandler('start', start))
dispatcher.add_handler(CommandHandler('help', help))

# Start the program
updater.start_polling()