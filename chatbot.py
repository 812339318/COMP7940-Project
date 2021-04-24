from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# import configparser
import os
import logging
import redis
import requests
import json
import time
import re

global redis1

def main():
    # Load your token and create an Updater for your Bot
    
    # config = configparser.ConfigParser()
    # config.read('config.ini')
    updater = Updater(token=(os.environ['ACCESS_TOKEN']), use_context=True)
    dispatcher = updater.dispatcher

    global redis1
    redis1 = redis.Redis(host=(os.environ['HOST']), password=(os.environ['PASSWORD']), port=(os.environ['REDISPORT']))

    # You can set this logging module, so you will know when and why things do not work as expected
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        level=logging.INFO)
    
    # register a dispatcher to handle message: here we register an echo dispatcher
    echo_handler = MessageHandler(Filters.text & (~Filters.command), echo)
    dispatcher.add_handler(echo_handler)

    # on different commands - answer in Telegram
    dispatcher.add_handler(CommandHandler("weight", weight))
    dispatcher.add_handler(CommandHandler("help", help_command))


    # To start the bot:
    updater.start_polling()
    updater.idle()


def echo(update, context):

    

    url = "https://spoonacular-recipe-food-nutrition-v1.p.rapidapi.com/food/converse"

    querystring = {"text":update.message.text}

    headers = {
        'x-rapidapi-key': "761b6bd801msh2c54d5c066730ebp1819fejsnc0bede413f78",
        'x-rapidapi-host': "spoonacular-recipe-food-nutrition-v1.p.rapidapi.com"
    }

    response = requests.request("GET", url, headers=headers, params=querystring)

    # print()
    answer=json.loads(response.text)
    reply_message = answer['answerText']
    # reply_message = update.message.text.upper()
    logging.info("Update: " + str(update))
    logging.info("context: " + str(context))
    context.bot.send_message(chat_id=update.effective_chat.id, text= reply_message)
    if answer['media']!=[]:
        for media in answer['media']:
            logging.info("Update: " + str(update))
            logging.info("context: " + str(context))
            context.bot.send_message(chat_id=update.effective_chat.id, text= media['title'])
            context.bot.send_message(chat_id=update.effective_chat.id, text= media['link'])
            context.bot.send_photo(update.effective_chat.id, media['image'])

# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.
def help_command(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""

    try: 
        logging.info(context.args[0])
        msg = context.args[0]   # /help keyword <-- this should store the keyword

        if msg=="weight":
            update.message.reply_text('Send /weight <date> to check your weight on a certain day. For example, /weight 20210424')
            update.message.reply_text('Send /weight <weight> to record your weight today. For example /weight 80(unit: kg)')

        else:
            update.message.reply_text('No such command')

    except (IndexError, ValueError):
        help_text="This chatbot supports queries related to food, such as nutritional content query and recipe query. You only need to send some keywords to query. For example, send ‘100g beef protein’ to query how much protein is in 100g of beef or send ‘chicken onion’ to query recipes related to chicken and onions."
        update.message.reply_text(help_text)
        help_command_text="It also supports some special commands, such as:"
        update.message.reply_text(help_command_text)
        update.message.reply_text("weight: Check or record your weight")
        update.message.reply_text("send /help <command> to see the detailed usage of the command")        


def weight(update: Update, context: CallbackContext) -> None:
    """Check or record your weight"""
    try: 
        global redis1
        logging.info(context.args[0])
        msg = context.args[0]   # /add keyword <-- this should store the keyword

        if check(msg)==True:
            try:
                time.strptime(msg,"%Y%m%d")
                if msg<=time.strftime("%Y%m%d", time.localtime()):
                    try:
                        redis1.get(msg)
                        reply_str="Your weight on "+time.strftime("%Y-%m-%d",time.strptime(msg,"%Y%m%d"))+" is "+redis1.get(msg).decode('UTF-8')+"kg"
                        update.message.reply_text(reply_str)
                    except:
                        update.message.reply_text("No related records found")
                else:
                    update.message.reply_text("You can't know your future weight")
            except:
                redis1.set(time.strftime("%Y%m%d", time.localtime()),msg)
                update.message.reply_text('Record added successfully')

        else:
            update.message.reply_text('Input format error')
            update.message.reply_text('Type /help weight to view the details')

    except (IndexError, ValueError):
        update.message.reply_text('Usage: /weight <date> or /weight <weight>')
        update.message.reply_text('Type /help weight to view the details')


def check(str):
 
    my_re = re.compile(r'[A-Za-z]',re.S)
    res = re.findall(my_re,str)
    if len(res):
        return False
    else:
        return True


if __name__ == '__main__':
    main()
    