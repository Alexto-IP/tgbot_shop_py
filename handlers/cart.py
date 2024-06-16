from config import bot, db, delete_message
from keyboard import *


def register_cart_handlers():
    # -----------------------regexp--------------------------
    bot.register_message_handler(show_cart, regexp="🛒 Корзина")
    # -----------------------inline--------------------------
    bot.register_callback_query_handler(add_to_cart, lambda x: x.data.startswith('add_to_cart'))
    bot.register_callback_query_handler(change_cart, lambda x: x.data.startswith('change_cart'))
    bot.register_callback_query_handler(delete_item_from_cart, lambda x: x.data.startswith('delete_item_from_cart'))
    bot.register_callback_query_handler(delete_all_from_cart, lambda x: x.data.startswith('delete_all_from_cart'))
    bot.register_callback_query_handler(back_to_cart, lambda x: x.data.startswith('back_to_cart'))
    bot.register_callback_query_handler(reduce_one_item_from_cart, lambda x: x.data.startswith('reduce_one_item_cart'))
    bot.register_callback_query_handler(delete_one_item_from_cart, lambda x: x.data.startswith('delete_one_item_cart'))
    bot.register_callback_query_handler(delete_message, lambda x: x.data.startswith('delete_message'))


def add_to_cart(call):
    callback_data_parts = call.data.split('|')
    item_id = callback_data_parts[1]
    if db.get_item_count(item_id) > 0:
        item_list = db.get_items_from_cart(call.from_user.id)
        if (item_id in item_list) and (db.get_item_count(item_id) > db.get_item_quantity_cart(call.from_user.id, item_id)):
            db.change_item_quantity_cart(1, call.from_user.id, item_id)
            bot.send_message(chat_id=call.message.chat.id, text='Товар добавлен в корзину')
        else:
            if db.get_item_count(item_id) > db.check_item_quantity_cart(call.from_user.id, item_id):
                db.add_to_cart(call.from_user.id, item_id)
                bot.send_message(chat_id=call.message.chat.id, text='Товар добавлен в корзину')
            else:
                bot.send_message(chat_id=call.message.chat.id, text='Товара на складе больше нет')
    else:
        bot.send_message(chat_id=call.message.chat.id, text='Приносим свои извинения, товара больше нет в наличии')


def cart_kb():
    kb = types.InlineKeyboardMarkup(row_width=2)
    kb.add(types.InlineKeyboardButton(text='Редактировать', callback_data="change_cart"),
           types.InlineKeyboardButton(text='🔙Назад', callback_data="delete_message"))
    return kb


def show_cart(message):
    id_list = db.get_items_from_cart(message.from_user.id)
    result = ''
    amount = 0
    if len(id_list) > 0:
        for item_id in id_list:
            price = round(db.get_item_price(item_id) * get_discount(message.from_user.id, item_id), 2)
            if db.get_item_quantity_cart(message.from_user.id, item_id) > 0:
                result += "{} - {} - {} руб x {} шт.\n".format(db.get_item_name(item_id), db.get_item_size(item_id),
                                                               price, db.get_item_quantity_cart
                                                               (message.from_user.id, item_id))
            else:
                result += "{} - {} - товар закончился.\n".format(db.get_item_name(item_id), db.get_item_size(item_id))
            amount += float(price) * int(db.get_item_quantity_cart(message.from_user.id, item_id))
        bot.send_message(message.from_user.id,
                         'Товары в твоей корзине:\n{} \nТвоя персональная скидка {}% \nСумма с учетом скидки: {} руб'
                         .format(result, str(db.get_user_discount(message.from_user.id)), str(amount)),
                         reply_markup=cart_kb())
    else:
        bot.send_message(message.from_user.id, 'Твоя корзина пуста. Ты можешь добавить товары в корзуну через каталог')


def delete_all_from_cart(call):
    db.delete_items_from_cart_user(call.from_user.id)
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                          text="Ты удалил все товары из корзины")


def delete_item_from_cart(call):
    callback_data_parts = call.data.split('|')
    item_id = callback_data_parts[1]
    if db.get_item_quantity_cart(call.from_user.id, item_id) == 1:
        db.delete_item_from_cart(call.from_user.id, item_id)
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text='Товар удален из корзины')
    else:
        kb = types.InlineKeyboardMarkup(row_width=2)
        kb.add(types.InlineKeyboardButton(text='Удалить 1 шт', callback_data=f"reduce_one_item_cart|{item_id}"))
        kb.add(types.InlineKeyboardButton(text='Удалить все', callback_data=f"delete_one_item_cart|{item_id}"))
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text=f'У тебя в корзине {db.get_item_quantity_cart(call.from_user.id, item_id)} '
                                   f'шт. этого товара. Сколько бы ты хотел удалить?', reply_markup=kb)


def delete_one_item_from_cart(call):
    callback_data_parts = call.data.split('|')
    item_id = callback_data_parts[1]
    db.delete_item_from_cart(call.from_user.id, item_id)
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                          text='Товар удален из корзины')


def reduce_one_item_from_cart(call):
    callback_data_parts = call.data.split('|')
    item_id = callback_data_parts[1]
    db.change_item_quantity_cart(-1, call.from_user.id, item_id)
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                          text='Товар удален из корзины')


def change_cart(call):
    id_list = db.get_items_from_cart(call.from_user.id)
    kb = types.InlineKeyboardMarkup(row_width=2)
    if len(id_list) > 0:
        for item_id in id_list:
            result = 'Удалить ' + db.get_item_name(item_id) + ' - ' + db.get_item_size(item_id)
            kb.add(types.InlineKeyboardButton(text=result, callback_data=f"delete_item_from_cart|{item_id}"))
        kb.add(types.InlineKeyboardButton(text='Удалить все', callback_data="delete_all_from_cart"),
               types.InlineKeyboardButton(text='🔙Назад', callback_data="back_to_cart"))
        bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=kb)


def back_to_cart(call):
    bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                  reply_markup=cart_kb())


def get_discount(user_id, item_id):
    if db.get_item_percentage_discount(item_id) > 0:
        discount = 1 - (db.get_item_percentage_discount(item_id) / 100)
    elif db.get_user_discount(user_id) > 0:
        discount = 1 - (db.get_user_discount(user_id) / 100)
    else:
        discount = 1
    return discount
