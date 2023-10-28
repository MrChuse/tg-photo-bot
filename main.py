from collections import defaultdict
from typing import Dict
from pprint import pprint
from traceback import print_exc
from threading import Thread
import datetime
import time
import sys

import telebot
from telebot import types
from PIL import Image, ImageDraw
import schedule

with open('api_token.txt', 'r') as f:
    API_TOKEN = f.read()

bot = telebot.TeleBot(API_TOKEN)


def backup_chats():
    with open('subscribed_chats.txt', 'w') as f:
        f.write('\n'.join(map(str, subscribed_chats)))

def load_chats():
    try:
        with open('subscribed_chats.txt', 'r') as f:
            chat_ids = set(map(int, f.read().split()))
            print('loaded chat ids')
            return chat_ids
    except FileNotFoundError:
        print('subscribed_chats.txt not found, set of chat ids is empty now')
        return set()
    except Exception:
        print_exc()
        return set()

subscribed_chats = load_chats()
@bot.message_handler(commands=['subscribe'])
def send_welcome(message):
    print('chat_id subscribed:', message.chat.id)
    if message.chat.id in subscribed_chats:
        bot.reply_to(message, 'This chat is already subscribed. Send /unsubscribe to unsubscribe.')
    else:
        subscribed_chats.add(message.chat.id)
        backup_chats()
        bot.reply_to(message, 'Successfully subscribed. This chat will receive photos now.')
        send_photo(message.chat.id)

@bot.message_handler(commands=['unsubscribe'])
def send_welcome(message):
    print('chat_id unsubscribed:', message.chat.id)
    if message.chat.id in subscribed_chats:
        subscribed_chats.remove(message.chat.id)
        backup_chats()
        bot.reply_to(message, 'Successfully unsubscribed. This chat won\'t receive photos anymore.')
    else:
        bot.reply_to(message, 'This chat isn\'t subscribed yet. Send /subscribe to subscribe.')

def send_photo(chat_id):
    dt = datetime.datetime.now()
    weekday = dt.strftime('%A')
    im = Image.open(f'photos/{weekday.lower()}.jpg')
    return bot.send_photo(chat_id, telebot.util.pil_image_to_file(im, quality=100))

def send_photos():
    print('sending photos')
    for chat_id in subscribed_chats:
        send_photo(chat_id)
    print('success')

def send_photos_each_day():
    schedule.every().day.at("00:00:01").do(send_photos)

    while True:
        schedule.run_pending()
        time.sleep(1) # wait one minute

if sys.argv[1] == 'sendnow':
    send_photos()
Thread(target=send_photos_each_day, daemon=True).start()
bot.infinity_polling()