import logging
from settings import settings
from telegram import ParseMode, Emoji
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from telegram.error import (TelegramError, Unauthorized, BadRequest, TimedOut, ChatMigrated, NetworkError)
import sqlite3
import sys

#Logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',level=logging.DEBUG)
logger = logging.getLogger(__name__)

#Parametros por usuario
params = dict()
PROJECT_PORFOLIO = "ProjectPortfolio"
USER_NAME = "UserName"

#Updater
updater = Updater(settings.token)
dispatcher = updater.dispatcher

def getParams(bot, update):
    #Valida la existencia de los parámetros iniciales
    if (PROJECT_PORFOLIO not in params or USER_NAME not in params):
        dbConnection = None
        try:
            dbConnection = sqlite3.connect(settings.database)
            cursor = dbConnection.cursor()
            query = "SELECT * FROM PARAMS WHERE CHAT_ID=" + str(update.message.chat_id) + ""
            if cursor.rowcount > 0:
                rows = cursor.fetchall()
                for row in rows:
                    params[row["Param_Name"]] = row[["Param_Value"]]
            else:
                return False
        except sqlite3.Error as e:
            logger.error("%s", e.args[0])
            sys.exit(1)
        finally:
            if dbConnection:
                dbConnection.close()
            return False
    return True

def start(bot, update):
    #Home message
    msg = "Hello {user_name}! I'm {bot_name}. \n"
    if (getParams(bot, update)):
        msg+= "We are working on the project portfolio *{project_portfolio}*, with the user *{user}*"
        # Send the message
        bot.send_message(chat_id=update.message.chat_id,
                     text=msg.format(
                         user_name=update.message.from_user.first_name,
                         bot_name=bot.name,
                         project_portfolio=params[PROJECT_PORFOLIO], user=params[USER_NAME]),
                     parse_mode=ParseMode.MARKDOWN)
    else:
        msg += "I need more information to procede. \n"
        msg += "Please, use /setprojectportfolio <name> To set the project portfolio \n"
        msg += "And use /setUserName <name> To set the user name \n"
        bot.send_message(chat_id=update.message.chat_id,
                         text=msg.format(
                             user_name=update.message.from_user.first_name,
                             bot_name=bot.name
                         ),
                         parse_mode=ParseMode.MARKDOWN)

def help(bot, update):
    #Help message
    msg = "*Commands:* \n"
    msg += "/projects - List your projects \n"
    msg += "/addproject <projectname> - Add a project \n"
    msg += "/help - This message"
    msg += "/setprojectportfolio <name> - set the project portfolio"
    msg += "/setusername <name> - set the user name"

    # Send the message
    bot.send_message(chat_id=update.message.chat_id,
                     text=msg,
                     parse_mode=ParseMode.MARKDOWN)

def setProjectPortfolio(bot, update, args):
    #Set the project portfolio
    if len(args) <= 0:
        bot.send_message(chat_id=update.message.chat_id,
                         text = "Please, use /setprojectportfolio <name>")
        return
    dbConnection = None
    try:
        dbConnection = sqlite3.connect(settings.database)
        cursor = dbConnection.cursor()
        query = "SELECT * FROM PARAMS WHERE CHAT_ID=" + str(update.message.chat_id) + " and Param_Name='" + PROJECT_PORFOLIO + "';"

        logger.debug("Tengo el cursor, para el query: {%s}", query)
        cursor.execute(query)

        logger.debug("Ejecute el query de consulta, con rowcount {%d}", cursor.rowcount)
        if cursor.fetchone() is not None:
            query = "UPDATE PARAMS SET Param_Value='" + args[0] + "' WHERE CHAT_ID=" + str(update.message.chat_id) + " AND Param_Name ='" + PROJECT_PORFOLIO + "';"
        else:
            query = "INSERT INTO PARAMS (Chat_ID, Param_Name, Param_Value) VALUES(" + str(update.message.chat_id) + ",'" + PROJECT_PORFOLIO + "','" + args[0] + "');"

        logger.debug(query)
        cursor.execute(query)
        dbConnection.commit()
    except sqlite3.Error as e:
        logger.error("%s", e.args[0])
        sys.exit(1)
    finally:
        if dbConnection:
            dbConnection.close()

def unknown(bot, update):
    #Unknown command handler
    bot.send_message(chat_id=update.message.chat_id,
                     text="I'm sorry, I don't understand that command. Please use */help* for guidance.",
                     parse_mode=ParseMode.MARKDOWN)

def error_callback(bot, update, error):
    try:
        raise error
    except Unauthorized:
        # remove update.message.chat_id from conversation list
        logging.error("Unauthorized (CHAT_ID:" + update.message.chat_id + ")")
    except BadRequest:
        # handle malformed requests - read more below!
        logging.error("BadRequest (CHAT_ID:" + update.message.chat_id + ")")
    except TimedOut:
        # handle slow connection problems
        logging.error("TimedOut (CHAT_ID:" + update.message.chat_id + ")")
    except NetworkError:
        # handle other connection problems
        logging.error("NetworkError (CHAT_ID:" + update.message.chat_id + ")")
    except ChatMigrated as e:
        # the chat_id of a group has changed, use e.new_chat_id instead
        logging.error("ChatMigrated (CHAT_ID:" + update.message.chat_id + ")")
    except TelegramError:
        # handle all other telegram related errors
        logging.error("TelegramError (CHAT_ID:" + update.message.chat_id + ")")

# Add handlers to dispatcher
dispatcher.add_handler(CommandHandler('start', start))
dispatcher.add_handler(CommandHandler('help', help))
dispatcher.add_handler(CommandHandler('setprojectportfolio', setProjectPortfolio, pass_args=True))
dispatcher.add_error_handler(error_callback)
dispatcher.add_handler(MessageHandler(Filters.command, unknown))

# Start the program
updater.start_polling()