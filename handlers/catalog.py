from config import bot, db, delete_message
from keyboard import *


def register_catalog_handlers():
    # -----------------------regexp--------------------------
    bot.register_message_handler(send_catalog, regexp="📋 Каталог")
    bot.register_message_handler(send_promotions, regexp="🎰 Акции")
    # -----------------------inline--------------------------
    bot.register_callback_query_handler(show_item_info, lambda x: x.data.startswith('show_item_info'))
    bot.register_callback_query_handler(show_item_sizes, lambda x: x.data.startswith('show_item_sizes'))
    bot.register_callback_query_handler(show_item_names, lambda x: x.data.startswith('show_item_names'))
    bot.register_callback_query_handler(back_to_catalog, lambda x: x.data.startswith('back_to_catalog'))
    bot.register_callback_query_handler(back_to_promotions, lambda x: x.data.startswith('back_to_promotions'))
    bot.register_callback_query_handler(delete_message, lambda x: x.data.startswith('delete_message'))


def keyboard_catalog(discount_status):
    available_types = db.get_items_types()[0]
    kb = types.InlineKeyboardMarkup(row_width=2)
    row = []
    if len(available_types) > 0:
        for item_type in available_types:
            row.append(types.InlineKeyboardButton(text=item_type, callback_data=f"show_item_names|{item_type}|{discount_status}"))
        kb.add(*row)
    kb.add(types.InlineKeyboardButton(text='🔙Назад', callback_data="delete_message"))
    return kb


def send_promotions(call):
    bot.send_message(chat_id=call.from_user.id, text='Здесь ты можешь ознакомиться с актуальными акциями',
                     reply_markup=keyboard_catalog(1))


def back_to_promotions(call):
    bot.edit_message_text(chat_id=call.message.chat.id,  message_id=call.message.message_id,
                          text='Здесь ты можешь ознакомиться с актуальными акциями', reply_markup=keyboard_catalog(1))


def send_catalog(call):
    bot.send_message(chat_id=call.from_user.id, text='Доступные категории товаров:', reply_markup=keyboard_catalog(0))


def back_to_catalog(call):
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                          text='Доступные категории товаров:', reply_markup=keyboard_catalog(0))


def show_item_names(call):
    callback_data_parts = call.data.split('|')
    item_type = callback_data_parts[1]
    discount_status = callback_data_parts[2]
    available_items = db.get_all_items_names(item_type, discount_status)[0]
    kb = types.InlineKeyboardMarkup(row_width=2)
    row = []
    if len(available_items) > 0:
        for item_name in available_items:
            row.append(types.InlineKeyboardButton(text=item_name,
                                              callback_data=f"show_item_sizes|{item_name}|{item_type}|{discount_status}"))
        kb.add(*row)
        if discount_status == '1':
            go_back = "back_to_promotions"
        else:
            go_back = "back_to_catalog"
        kb.add(types.InlineKeyboardButton(text='🔙Назад', callback_data=go_back))
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text=f'Доступные товары:', reply_markup=kb)
    else:
        bot.send_message(chat_id=call.message.chat.id, text=f'Приносим извинения, товаров данной категории не осталось')


def show_item_sizes(call):
    callback_data_parts = call.data.split('|')
    item_name = callback_data_parts[1]
    item_type = callback_data_parts[2]
    discount_status = callback_data_parts[3]
    available_sizes = db.get_item_sizes(item_name, item_type, discount_status)[0]
    kb = types.InlineKeyboardMarkup(row_width=4)
    row = []
    if len(available_sizes) > 0:
        for item_size in available_sizes:
            row.append(types.InlineKeyboardButton(text=item_size,
                                              callback_data=f"show_item_info|{item_name}|{item_type}|{item_size}|{discount_status}"))
        kb.add(*row)
        kb.add(
            types.InlineKeyboardButton(text='🔙Назад', callback_data=f"show_item_names|{item_type}|{discount_status}"))
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text=f'Доступные размеры:', reply_markup=kb)
    else:
        bot.send_message(chat_id=call.message.chat.id, text='Приносим извинения, размеров не осталось')


def show_item_info(call):
    callback_data_parts = call.data.split('|')
    item_name = callback_data_parts[1]
    item_type = callback_data_parts[2]
    item_size = callback_data_parts[3]
    item_id = db.get_item_id(item_name, item_type, item_size)
    price = db.get_item_price(item_id)
    img = open(f"img/{item_id}_{item_name}_{item_type}.jpg", 'rb')
    kb = types.InlineKeyboardMarkup(row_width=2)
    if db.get_item_count(item_id) > 0:
        kb.add(types.InlineKeyboardButton(text='Добавить в корзину', callback_data=f"add_to_cart|{item_id}"))
        if db.get_item_percentage_discount(item_id) > 0:
            result = "{} {} \nРазмер: {} \nСтоимость: <s>{}</s> {} руб".format(item_type, item_name, item_size, price, price *
                                                                               (1 - (db.get_item_percentage_discount(item_id)/100)))
        else:
            result = "{} {} \nРазмер: {} \nСтоимость: {} руб".format(item_type, item_name, item_size, price)
    else:
        result = '{} {} \nРазмер: {}\nСтоимость: {}\n\n<b>Товара нет в наличии</b>'.format(item_type, item_name,
                                                                                           item_size, price)
    kb.add(types.InlineKeyboardButton(text='🔙Назад', callback_data="delete_message"))
    bot.send_photo(chat_id=call.message.chat.id, photo=img, caption=result, reply_markup=kb, parse_mode='html')

