from config import bot, db
from keyboard import *

def register_user_handlers():
    # -----------------------commands--------------------------
    bot.register_message_handler(greetings, commands=['start'])
    bot.register_message_handler(change_name, commands=['name'])
    # -----------------------inline--------------------------
    bot.register_callback_query_handler(change_name_yes, lambda x: x.data.startswith('change_name_yes'))
    bot.register_callback_query_handler(change_name_no, lambda x: x.data.startswith('change_name_no'))


def greetings(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(button1, button2)
    markup.row(button3, button4)
    if not db.get_subscriber(message.from_user.id):
        db.add_subscriber(message.from_user.id)
        bot.send_message(message.from_user.id, 'kon ni chi ha, дорогой user! 🙋')
        bot.send_message(message.from_user.id,
                         'Я бот бренда FND 🔖 Здесь ты можешь посмотреть каталог наших товаров, узнать об актуальных '
                         'акциях и найти информацию о наших соц сетях.\n\nКстати, как мне к тебе обращаться?')
        bot.send_message(message.from_user.id, '/name')
    else:
        bot.send_message(message.from_user.id, 'С возвращением, ' + str(db.get_username(message.from_user.id)) + '!',
                         reply_markup=markup)


def change_name(message):
    mesg = bot.send_message(message.from_user.id, 'Задай имя:')
    bot.register_next_step_handler(mesg, name)


def name(message):
    if db.get_username(message.from_user.id) == 'user':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.row(button1, button2)
        markup.row(button3, button4)
        db.update_username(message.from_user.id, message.text)
        bot.send_message(message.from_user.id, 'Приятно познакомиться, ' + str(db.get_username(message.from_user.id))
                         + '. Для навигации по боту пользуйся системными кнопками телеграмма', reply_markup=markup)
    else:
        markup = types.InlineKeyboardMarkup(row_width=2)
        iteminline1 = types.InlineKeyboardButton("Да", callback_data="change_name_yes" + message.text)
        iteminline2 = types.InlineKeyboardButton("Нет", callback_data='change_name_no')
        markup.add(iteminline1, iteminline2)
        bot.send_message(message.from_user.id, 'Ты уже выбрал себе имя. Хочешь его сменить?', reply_markup=markup,
                         parse_mode='html')


def change_name_yes(call):
    new_name = call.data[15:]
    db.update_username(call.from_user.id, new_name)
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                          text='Ты успешно сменил имя.')


def change_name_no(call):
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Отмена принята.")
