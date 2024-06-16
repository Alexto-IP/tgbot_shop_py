from config import bot
from keyboard import *


def register_contacts_handlers():
    # -----------------------regexp--------------------------
    bot.register_message_handler(send_contacts, regexp="📧 Контакты")


def send_contacts(message):
    markup = types.InlineKeyboardMarkup(row_width=2)
    iteminline1 = types.InlineKeyboardButton("tg chanel", url='https://t.me/fndclothes')
    iteminline2 = types.InlineKeyboardButton("vk group", url='https://vk.com/fndclothes')
    iteminline3 = types.InlineKeyboardButton("yt chanel", url='https://www.youtube.com/@Fnd-clothes')
    iteminline4 = types.InlineKeyboardButton("inst", url='https://instagram.com/fnd.clothes?igshid=MzNlNGNkZWQ4Mg==')
    markup.add(iteminline1, iteminline2, iteminline3, iteminline4)
    bot.send_message(message.from_user.id, 'Наши контакты:', reply_markup=markup, parse_mode='html')
