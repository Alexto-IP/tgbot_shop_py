from config import *
from keyboard import *
import emoji
from PIL import Image
from io import BytesIO
import requests
from handlers import user, cart


def register_admin_handlers():
    # -----------------------regexp--------------------------
    bot.register_message_handler(become_admin, regexp="↪Меню администратора")
    bot.register_message_handler(add_item, regexp="➕Добавить товар")
    bot.register_message_handler(add_item_discount, regexp="💯Установить скидку")
    bot.register_message_handler(check_carts, regexp="👁‍Просмотр корзин")
    bot.register_message_handler(back_to_user_menu, regexp="↩Обычное меню")
    # -----------------------commands--------------------------
    bot.register_message_handler(become_admin, commands=['getadminstatus'])
    bot.register_message_handler(back_to_user, commands=['unloginadmin'])
    # -----------------------inline--------------------------
    bot.register_callback_query_handler(back_to_check_carts, lambda x: x.data.startswith('back_to_check'))
    bot.register_callback_query_handler(show_users_cart, lambda x: x.data.startswith('show_users_cart'))
    bot.register_callback_query_handler(message_from_bot, lambda x: x.data.startswith('message_from_bot'))
    bot.register_callback_query_handler(new_type, lambda x: x.data.startswith('new_type'))
    bot.register_callback_query_handler(new_item_name, lambda x: x.data.startswith('new_item_name'))
    bot.register_callback_query_handler(add_item_count, lambda x: x.data.startswith('add_item_count'))
    bot.register_callback_query_handler(set_item_discount, lambda x: x.data.startswith('set_item_discount'))
    bot.register_callback_query_handler(change_item_price, lambda x: x.data.startswith('change_item_price'))
    bot.register_callback_query_handler(add_collection_discount, lambda x: x.data.startswith('add_collection_discount'))
    bot.register_callback_query_handler(add_type_discount, lambda x: x.data.startswith('add_type_discount'))
    bot.register_callback_query_handler(add_item_discount_type, lambda x: x.data.startswith('add_item_name_discount'))
    bot.register_callback_query_handler(choose_size_discount, lambda x: x.data.startswith('choose_size'))
    bot.register_callback_query_handler(add_new_item, lambda x: x.data.startswith('add_new_item'))
    bot.register_callback_query_handler(change_search_item_data, lambda x: x.data.startswith('change_item_data'))
    bot.register_callback_query_handler(changed_item_data, lambda x: x.data.startswith('change'))
    bot.register_callback_query_handler(cart_paid, lambda x: x.data.startswith('cart_paid'))
    bot.register_callback_query_handler(delete_message, lambda x: x.data.startswith('delete_message'))
    bot.register_callback_query_handler(delete_message_from_bot, lambda x: x.data.startswith('delete_mesg'))


def admin_kb():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(button5, button7)
    kb.add(button6, button8)
    return kb


def become_admin(message):
    if db.get_adminstatus(message.from_user.id) == 'true':
        bot.send_message(message.from_user.id, 'Вы уже являйтесь администратором', reply_markup=admin_kb())
    else:
        mesg = bot.send_message(message.from_user.id, "Введите пароль:")
        bot.register_next_step_handler(mesg, password_verification)


def password_verification(message):
    if message.text == pas:
        db.update_adminstatus(message.from_user.id, 'true')
        bot.send_message(message.from_user.id, 'Теперь у Вас есть статус администратора и доступ к специальному меню',
                         reply_markup=admin_kb())
    else:
        bot.send_message(message.from_user.id, 'В доступе отказано')


def back_to_user_menu(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(button1, button2)
    markup.row(button3, button4)
    markup.add(button9)
    bot.send_message(message.from_user.id, 'Смена на меню пользователя', reply_markup=markup)


def back_to_user(message):
    db.update_adminstatus(message.from_user.id, 'false')
    user.greetings(message)


def check_admin_status(message):
    if db.get_adminstatus(message.from_user.id) == 'true':
        return True
    else:
        bot.send_message(message.from_user.id, 'В доступе отказано')
        user.greetings(message)


def carts_kb():
    kb = types.InlineKeyboardMarkup(row_width=2)
    row = []
    users_carts = db.users_with_cart()
    if len(users_carts) > 0:
        for user_id in db.users_with_cart():
            user_name = str(db.get_username(user_id))
            row.append(types.InlineKeyboardButton(text=user_name, callback_data=f"show_users_cart|{user_id}"))
        kb.add(*row)
    kb.add(types.InlineKeyboardButton(text='🔙Назад', callback_data="delete_message"))
    return kb


def check_carts(call):
    if check_admin_status(call):
        users_carts = db.users_with_cart()
        if len(users_carts) > 0:
            bot.send_message(call.from_user.id, text='Чью корзину Вы бы хотели просмотреть?', reply_markup=carts_kb())
        else:
            bot.send_message(call.from_user.id, text='Ни один из пользователей пока не добавил ничего себе в корзину',
                             reply_markup=carts_kb())


def back_to_check_carts(call):
    users_carts = db.users_with_cart()
    if len(users_carts) > 0:
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text='Чью корзину Вы бы хотели просмотреть?', reply_markup=carts_kb())
    else:
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                         text='Ни один из пользователей пока не добавил ничего себе в корзину', reply_markup=carts_kb())


def show_users_cart(call):
    callback_data_parts = call.data.split('|')
    user_id = callback_data_parts[1]
    id_list = db.get_items_from_cart(user_id)
    result = ''
    amount = 0
    kb = types.InlineKeyboardMarkup(row_width=2)
    username = bot.get_chat(user_id).username
    if username != None:
        first_name = bot.get_chat(user_id).first_name
        user_link = f"https://t.me/{username}"
        kb.add(types.InlineKeyboardButton(text=first_name, url=user_link))
    kb.add(types.InlineKeyboardButton(text='🤖Написать от лица бота', callback_data=f"message_from_bot|{user_id}"))
    kb.add(types.InlineKeyboardButton(text='🔙Назад', callback_data="back_to_check"))
    if len(id_list) > 0:
        for item_id in id_list:
            price = round(db.get_item_price(item_id) * cart.get_discount(user_id, item_id), 2)
            result += "{} - {} - {} руб x {} шт.\n".format(db.get_item_name(item_id), db.get_item_size(item_id), price,
                                                           db.get_item_quantity_cart(user_id, item_id))
            amount += float(price) * int(db.get_item_quantity_cart(user_id, item_id))
        cart_result = 'Товары в корзине:\n' + result + '\nСумма: ' + str(amount) + ' руб'
        kb.add(types.InlineKeyboardButton(text='Корзина оплачена', callback_data=f'cart_paid|{user_id}|{amount}'))
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                         text=str(cart_result), reply_markup=kb)
    else:
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text='Что-то пошло не так', reply_markup=kb)


def cart_paid(call):
    callback_data_parts = call.data.split('|')
    user_id = callback_data_parts[1]
    amount = callback_data_parts[2]
    db.update_user_total_amount(user_id, amount)
    id_list = db.get_items_from_cart(user_id)
    user_discount = db.get_user_discount(user_id)
    for item_id in id_list:
        item_list = db.items_in_carts()
        if item_id in item_list:
            quantity = db.get_item_quantity_cart(user_id, item_id)
            db.update_item_count(item_id, -quantity)
            users = db.users_with_certain_item_in_cart(item_id)
            for other_user_id in users:
                quantity_item = db.get_item_count(item_id)
                if quantity_item < db.get_item_quantity_cart(other_user_id, item_id):
                    db.set_item_quantity_cart(quantity_item, other_user_id, item_id)
        db.delete_item_from_cart(user_id, item_id)
    if user_discount < 20:
        user_discount = db.get_user_total_amount(user_id) // 1000
        if user_discount > 20:
            user_discount = 20
        db.update_personal_discount(user_id, user_discount)
    bot.send_message(call.from_user.id, 'Корзина пользователя ' + str(db.get_username(user_id)) + ' оплачена')


def message_from_bot(call):
    callback_data_parts = call.data.split('|')
    user_id = callback_data_parts[1]
    mesg = bot.send_message(call.from_user.id, "Что бы вы хотели написать пользователю " + str(db.get_username(user_id)) + ":")
    bot.register_next_step_handler(mesg, send_bot_message, user_id)


def send_bot_message(call, user_id):
    kb = types.InlineKeyboardMarkup(row_width=2)
    username = bot.get_chat(user_id).username
    sent_message = bot.send_message(user_id, call.text)
    message_id = sent_message.message_id
    if username != None:
        first_name = bot.get_chat(user_id).first_name
        user_link = f"https://t.me/{username}"
        kb.add(types.InlineKeyboardButton(text=first_name, url=user_link))
    kb.add(types.InlineKeyboardButton(text='Удалить сообщение', callback_data=f"delete_mesg|{message_id}|{user_id}"))
    kb.add(types.InlineKeyboardButton(text='🔙Назад', callback_data="delete_message"))
    bot.send_message(call.from_user.id, 'Вы отправили сообщение пользователю ' + str(db.get_username(user_id)) + ': ' +
                     call.text, reply_markup=kb)


def delete_message_from_bot(call):
    bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
    callback_data_parts = call.data.split('|')
    message_id = callback_data_parts[1]
    user_id = callback_data_parts[2]
    bot.delete_message(user_id, message_id)
    result = 'Сообщение для пользователя ' + str(db.get_username(user_id)) + ' было удалено.'
    bot.send_message(call.from_user.id, result)


@delay_handler
def add_item(message):
    if check_admin_status(message):
        bot.send_message(message.from_user.id, db.get_items_types()[1])
        mesg = bot.send_message(message.from_user.id, "Введите нужную категорию:")
        bot.register_next_step_handler(mesg, check_types)


def correct_register(lst, variable):
    for i in range(len(lst)):
        if lst[i].upper() == variable.upper():
            variable = lst[i]
    return variable


def correct_input(message, var):
    if (not isinstance(var, str)) or (any(char in emoji.unicode_codes.EMOJI_DATA for char in var)):
        bot.send_message(message.from_user.id, "Некорректный ввод")
        return False
    else:
        return True


def correct_input_int(message, var):
    if var.isdigit():
        return True
    else:
        bot.send_message(message.from_user.id, "Некорректный ввод. Введите только цифры")
        return False


def check_types(message):
    if correct_input(message, message.text):
        exsiting_types = db.get_items_types()[0]
        item_type = correct_register(exsiting_types, message.text)
        if item_type in exsiting_types:
            bot.send_message(message.from_user.id, db.get_all_items_names(item_type, 0)[1])
            mesg = bot.send_message(message.from_user.id, 'Введите нужный товар:')
            bot.register_next_step_handler(mesg, check_name, item_type)
        else:
            kb = types.InlineKeyboardMarkup(row_width=2)
            kb.add(types.InlineKeyboardButton(text='Да', callback_data=f"new_type|{item_type}"),
                   types.InlineKeyboardButton(text='Нет', callback_data="delete_message"))
            bot.send_message(message.from_user.id, 'Данной категории нет в списке. Создать новую категорию?', reply_markup=kb)
    else:
        add_item(message)


def new_type(message):
    callback_data_parts = message.data.split('|')
    item_type = callback_data_parts[1]
    mesg = bot.send_message(message.from_user.id, 'Введите наименование товара:')
    bot.register_next_step_handler(mesg, check_name, item_type)


def check_name(message, item_type):
    if correct_input(message, message.text):
        exsiting_names = db.get_all_items_names(item_type, 0)[0]
        item_name = correct_register(exsiting_names, message.text)
        if (item_name in exsiting_names) or (len(exsiting_names) == 0):
            mesg = bot.send_message(message.from_user.id, 'Введите размер:')
            bot.register_next_step_handler(mesg, check_size, item_type, item_name)
        else:
            kb = types.InlineKeyboardMarkup(row_width=2)
            kb.add(types.InlineKeyboardButton(text='Да', callback_data=f"new_item_name|{item_type}|{item_name}"),
                   types.InlineKeyboardButton(text='Нет', callback_data="delete_message"))
            bot.send_message(message.from_user.id, 'Данного товара нет в списке. Создать новый?', reply_markup=kb)
    else:
        mesg = bot.send_message(message.from_user.id, 'Введите нужный товар:')
        bot.register_next_step_handler(mesg, check_name, item_type)


def new_item_name(message):
    callback_data_parts = message.data.split('|')
    item_type = callback_data_parts[1]
    item_name = callback_data_parts[2]
    mesg = bot.send_message(message.from_user.id, 'Введите размер:')
    bot.register_next_step_handler(mesg, check_size, item_type, item_name)


def check_size(message, item_type, item_name):
    if correct_input(message, message.text):
        exsiting_sizes = db.get_item_sizes(item_name, item_type, 0)[0]
        item_size = correct_register(exsiting_sizes, message.text)
        kb = types.InlineKeyboardMarkup(row_width=2)
        if item_size in exsiting_sizes:
            item_id = db.get_item_id(item_name, item_type, item_size)
            send_item_info(message, item_id)
        else:
            kb.add(types.InlineKeyboardButton(text='Да', callback_data=f'add_new_item|{item_type}|{item_name}|{item_size}'),
                   types.InlineKeyboardButton(text='Нет', callback_data='delete_message'))
            kb.add(types.InlineKeyboardButton(text='Редактировать', callback_data=f'change_item_data|{item_type}|{item_name}|{item_size}'))
            bot.send_message(message.from_user.id, 'Товара {} категории {} размера {} нет в каталоге. Добавить его?'
                             .format(item_name, item_type, item_size), reply_markup=kb)
    else:
        mesg = bot.send_message(message.from_user.id, 'Введите размер:')
        bot.register_next_step_handler(mesg, check_size, item_type, item_name)


def add_item_count(message):
    callback_data_parts = message.data.split('|')
    item_id = callback_data_parts[1]
    mesg = bot.send_message(message.from_user.id, 'Введите количество товара в поставке:')
    bot.register_next_step_handler(mesg, add_item_count_result, item_id)


def add_item_count_result(message, item_id):
    if correct_input_int(message, message.text):
        item_count = message.text
        db.update_item_count(item_id, item_count)
        bot.send_message(message.from_user.id, 'Данные о поставке внесены успешно')
        send_item_info(message, item_id)
    else:
        mesg = bot.send_message(message.from_user.id, 'Введите количество товара в поставке:')
        bot.register_next_step_handler(mesg, add_item_count_result, item_id)


def set_item_discount(message):
    callback_data_parts = message.data.split('|')
    data = callback_data_parts[1]
    column = callback_data_parts[2]
    mesg = bot.send_message(message.from_user.id, 'Введите скидку в %:')
    bot.register_next_step_handler(mesg, set_item_discount_result, column, data)


def set_item_discount_result(message, column, data):
    if correct_input_int(message, message.text):
        discount = message.text
        db.update_item_discount(discount, column, data)
        bot.send_message(message.from_user.id, 'Данные о скидке внесены успешно')
        if data in db.get_all_items_id():
            send_item_info(message, data)
    else:
        mesg = bot.send_message(message.from_user.id, 'Введите скидку в %:')
        bot.register_next_step_handler(mesg, set_item_discount_result, column, data)


def change_item_price(message):
    callback_data_parts = message.data.split('|')
    item_id = callback_data_parts[1]
    mesg = bot.send_message(message.from_user.id, 'Введите новую цену в рублях:')
    bot.register_next_step_handler(mesg, change_item_count_result, item_id)


def change_item_count_result(message, item_id):
    if correct_input_int(message, message.text):
        item_price = message.text
        db.update_item_price(item_id, item_price)
        bot.send_message(message.from_user.id, 'Цена товара изменена успешно')
        send_item_info(message, item_id)
    else:
        mesg = bot.send_message(message.from_user.id, 'Введите новую цену в рублях:')
        bot.register_next_step_handler(mesg, change_item_count_result, item_id)


def send_item_info(message, item_id):
    item_type = db.get_item_type(item_id)
    item_name = db.get_item_name(item_id)
    item_size = db.get_item_size(item_id)
    price = db.get_item_price(item_id)
    discount = db.get_item_percentage_discount(item_id)
    collection = db.get_item_collection(item_id)
    img = open("img/drop1_gr.jpg", 'rb')
    count = db.get_item_count(item_id)
    kb = types.InlineKeyboardMarkup(row_width=2)
    kb.add(types.InlineKeyboardButton(text='Поставка товара', callback_data=f'add_item_count|{item_id}'))
    kb.add(types.InlineKeyboardButton(text='Редактировать цену', callback_data=f'change_item_price|{item_id}'))
    kb.add(types.InlineKeyboardButton(text='Редактировать скидку', callback_data=f'set_item_discount|{item_id}|item_id'))
    kb.add(types.InlineKeyboardButton(text='🔙Назад', callback_data='delete_message'))
    result = "{} {} \nРазмер: {} \nСтоимость: {} руб \nКоличество: {} шт \nСкидка: {}% " \
             "\nЦена с учетом скидки: {} руб \nКоллекция: {}" \
        .format(item_type, item_name, item_size, price, count, discount, price * (1 - (discount/100)), collection)
    bot.send_photo(chat_id=message.chat.id, photo=img, caption=result, reply_markup=kb, parse_mode='html')


def add_item_discount(message):
    if check_admin_status(message):
        kb = types.InlineKeyboardMarkup(row_width=2)
        kb.add(types.InlineKeyboardButton(text='Коллекция', callback_data='add_collection_discount'),
               types.InlineKeyboardButton(text='Категория', callback_data='add_type_discount'),
               types.InlineKeyboardButton(text='Товар', callback_data='add_item_name_discount'),
               types.InlineKeyboardButton(text='🔙Назад', callback_data='delete_message'))
        bot.send_message(message.from_user.id, 'На что вы бы хотели установить скидку?', reply_markup=kb)


def add_collection_discount(message):
    bot.send_message(message.from_user.id, db.get_item_collections()[1])
    mesg = bot.send_message(message.from_user.id, "Введите нужную коллекцию:")
    bot.register_next_step_handler(mesg, check_collection)


def check_collection(message):
    if correct_input(message, message.text):
        exsiting_collections = db.get_item_collections()[0]
        item_collection = correct_register(exsiting_collections, message.text)
        if item_collection in exsiting_collections:
            mesg = bot.send_message(message.from_user.id, 'Введите скидку в %:')
            bot.register_next_step_handler(mesg, set_item_discount_result, 'collection', item_collection)
        else:
            bot.send_message(message.from_user.id, 'Ошибка в вводе. Данной коллекции нет в списке. Попробуйте еще раз')
            add_collection_discount(message)
    else:
        add_collection_discount(message)


def add_type_discount(message):
    bot.send_message(message.from_user.id, db.get_items_types()[1])
    mesg = bot.send_message(message.from_user.id, "Введите нужную категорию:")
    bot.register_next_step_handler(mesg, check_type_discount)


def check_type_discount(message):
    if correct_input(message, message.text):
        exsiting_types = db.get_items_types()[0]
        item_type = correct_register(exsiting_types, message.text)
        if item_type in exsiting_types:
            mesg = bot.send_message(message.from_user.id, 'Введите скидку в %:')
            bot.register_next_step_handler(mesg, set_item_discount_result, 'item_type', item_type)
        else:
            bot.send_message(message.from_user.id, 'Ошибка в вводе. Данной категории нет в списке. Попробуйте еще раз')
            add_type_discount(message)
    else:
        add_type_discount(message)


def add_item_discount_type(message):
    bot.send_message(message.from_user.id, db.get_items_types()[1])
    mesg = bot.send_message(message.from_user.id, "Введите категорию товара:")
    bot.register_next_step_handler(mesg, check_item_types_discount)


def check_item_types_discount(message):
    if correct_input(message, message.text):
        exsiting_types = db.get_items_types()[0]
        item_type = correct_register(exsiting_types, message.text)
        if item_type in exsiting_types:
            bot.send_message(message.from_user.id, db.get_all_items_names(item_type, 0)[1])
            mesg = bot.send_message(message.from_user.id, 'Введите нужный товар:')
            bot.register_next_step_handler(mesg, check_item_name_discount, item_type)
        else:
            bot.send_message(message.from_user.id, 'Ошибка в вводе. Данной категории нет в списке. Попробуйте еще раз')
            add_item_discount_type(message)
    else:
        add_item_discount_type(message)


def check_item_name_discount(message, item_type):
    if correct_input(message, message.text):
        exsiting_names = db.get_all_items_names(item_type, 0)[0]
        item_name = correct_register(exsiting_names, message.text)
        if item_name in exsiting_names:
            kb = types.InlineKeyboardMarkup(row_width=1)
            kb.add(types.InlineKeyboardButton(text='Все размеры', callback_data=f'set_item_discount|{item_name}|item_name'),
                   types.InlineKeyboardButton(text='Выбрать размер', callback_data=f'choose_size|{item_type}|{item_name}'))
            bot.send_message(message.from_user.id, 'Вы бы хотели установить скидку на все размеры данного товара, либо'
                                                   'на один конкретный?', reply_markup=kb)
        else:
            bot.send_message(message.from_user.id, 'Ошибка в вводе. Данного товара нет в списке. Попробуйте еще раз')
            bot.send_message(message.from_user.id, db.get_all_items_names(item_type, 0)[1])
            mesg = bot.send_message(message.from_user.id, 'Введите нужный товар:')
            bot.register_next_step_handler(mesg, check_item_name_discount, item_type)
    else:
        bot.send_message(message.from_user.id, db.get_all_items_names(item_type, 0)[1])
        mesg = bot.send_message(message.from_user.id, 'Введите нужный товар:')
        bot.register_next_step_handler(mesg, check_item_name_discount, item_type)


def choose_size_discount(message):
    callback_data_parts = message.data.split('|')
    item_type = callback_data_parts[1]
    item_name = callback_data_parts[2]
    bot.send_message(message.from_user.id, db.get_item_sizes(item_name, item_type, 0)[1])
    mesg = bot.send_message(message.from_user.id, 'Введите размер:')
    bot.register_next_step_handler(mesg, check_size_discount, item_type, item_name)


def check_size_discount(message, item_type, item_name):
    if correct_input(message, message.text):
        exsiting_sizes = db.get_item_sizes(item_name, item_type, 0)[0]
        item_size = correct_register(exsiting_sizes, message.text)
        if item_size in exsiting_sizes:
            item_id = db.get_item_id(item_name, item_type, item_size)
            send_item_info(message, item_id)
        else:
            bot.send_message(message.from_user.id, 'Ошибка в вводе. Данного размера нет в списке. Попробуйте еще раз')
            bot.send_message(message.from_user.id, db.get_item_sizes(item_name, item_type, 0)[1])
            mesg = bot.send_message(message.from_user.id, 'Введите размер:')
            bot.register_next_step_handler(mesg, check_size_discount, item_type, item_name)
    else:
        bot.send_message(message.from_user.id, db.get_item_sizes(item_name, item_type, 0)[1])
        mesg = bot.send_message(message.from_user.id, 'Введите размер:')
        bot.register_next_step_handler(mesg, check_size_discount, item_type, item_name)


def add_new_item(message):
    callback_data_parts = message.data.split('|')
    item_type = callback_data_parts[1]
    item_name = callback_data_parts[2]
    item_size = callback_data_parts[3]
    bot.send_message(message.from_user.id, 'Введите одну из созданных коллекций или введите название новой'
                     + db.get_item_collections()[1])
    mesg = bot.send_message(message.from_user.id, 'Введите коллекцию, к которой относится товар:')
    bot.register_next_step_handler(mesg, add_new_item_collection, item_type, item_name, item_size)


def add_new_item_collection(message, item_type, item_name, item_size):
    if correct_input(message, message.text):
        exsiting_collections = db.get_item_collections()[0]
        item_collection = correct_register(exsiting_collections, message.text)
        mesg = bot.send_message(message.from_user.id, 'Введите количество товара:')
        bot.register_next_step_handler(mesg, add_new_item_count, item_type, item_name, item_size, item_collection)
    else:
        bot.send_message(message.from_user.id, 'Введите одну из созданных коллекций или введите название новой'
                         + db.get_item_collections()[1])
        mesg = bot.send_message(message.from_user.id, 'Введите коллекцию, к которой относится товар:')
        bot.register_next_step_handler(mesg, add_new_item_collection, item_type, item_name, item_size)


def add_new_item_count(message, item_type, item_name, item_size, item_collection):
    if correct_input_int(message, message.text):
        item_count = message.text
        mesg = bot.send_message(message.from_user.id, 'Введите цену товара:')
        bot.register_next_step_handler(mesg, add_new_item_price, item_type, item_name, item_size, item_collection, item_count)
    else:
        mesg = bot.send_message(message.from_user.id, 'Введите количество товара:')
        bot.register_next_step_handler(mesg, add_new_item_count, item_type, item_name, item_size, item_collection)


def add_new_item_price(message, item_type, item_name, item_size, item_collection, item_count):
    if correct_input_int(message, message.text):
        item_price = message.text
        db.add_new_item(item_type, item_name, item_size, item_collection, item_count, item_price)
        mesg = bot.send_message(message.from_user.id, 'Отправьте фотографию товара:')
        item_id = db.get_item_id(item_name, item_type, item_size)
        bot.register_next_step_handler(mesg, add_new_item_phot, item_id, item_name, item_type)
    else:
        mesg = bot.send_message(message.from_user.id, 'Введите цену товара:')
        bot.register_next_step_handler(mesg, add_new_item_price, item_type, item_name, item_size, item_collection,
                                       item_count)


def add_new_item_phot(message, item_id, item_name, item_type):
    if message.photo:
        photo = message.photo[-1]
        file_id = photo.file_id
        file_info = bot.get_file(file_id)
        file_path = file_info.file_path
        photo_url = f"https://api.telegram.org/file/bot{TOKEN}/{file_path}"

        # Сохранение фотографии в формате .jpg в папку img
        image = Image.open(BytesIO(requests.get(photo_url).content))
        img_path = f"img/{item_id}_{item_name}_{item_type}.jpg"
        image.save(img_path, "JPEG")
        bot.send_message(message.from_user.id, 'Новый товар внесен в каталог')
        send_item_info(message, item_id)
    else:
        mesg = bot.send_message(message.from_user.id, 'Вы не отправили фотографию. '
                                                      'Пожалуйста, отправьте фотографию товара:')
        bot.register_next_step_handler(mesg, add_new_item_phot, item_id, item_name)




def change_search_item_data(message):
    callback_data_parts = message.data.split('|')
    item_type = callback_data_parts[1]
    item_name = callback_data_parts[2]
    item_size = callback_data_parts[3]
    kb = types.InlineKeyboardMarkup(row_width=2)
    kb.add(types.InlineKeyboardButton(text='Категорию', callback_data=f'change|item_type|{item_name}|{item_size}'),
           types.InlineKeyboardButton(text='Размер', callback_data=f'change|item_size|{item_type}|{item_name}'),
           types.InlineKeyboardButton(text='Наименование', callback_data=f'change|item_name|{item_type}|{item_size}'),
           types.InlineKeyboardButton(text='🔙Назад', callback_data='delete_message'))
    bot.send_message(message.from_user.id, 'Какой из параметров вы бы хотели изменить? \nКатегория: {} \nНазвание {} '
                                           '\nРазмер {}'.format(item_type, item_name, item_size), reply_markup=kb)


def changed_item_data(message):
    callback_data_parts = message.data.split('|')
    changed_data = callback_data_parts[1]
    var1 = callback_data_parts[2]
    var2 = callback_data_parts[3]
    if changed_data == 'item_type':
        mesg = bot.send_message(message.from_user.id, "Введите нужную категорию:")
    elif changed_data == 'item_name':
        mesg = bot.send_message(message.from_user.id, "Введите название:")
    else:
        mesg = bot.send_message(message.from_user.id, "Введите размер:")
    bot.register_next_step_handler(mesg, edited_check, changed_data, var1, var2)


def edited_check(message, changed_data, var1, var2):
    if correct_input(message, message.text):
        if changed_data == 'item_type':
            item_name = var1
            item_size = var2
            exsiting_types = db.get_items_types()[0]
            item_type = correct_register(exsiting_types, message.text)
        elif changed_data == 'item_name':
            item_type = var1
            item_size = var2
            exsiting_names = db.get_all_items_names(item_type, 0)[0]
            item_name = correct_register(exsiting_names, message.text)
        else:
            item_name = var2
            item_type = var1
            exsiting_sizes = db.get_item_sizes(item_name, item_type, 0)[0]
            item_size = correct_register(exsiting_sizes, message.text)
        kb = types.InlineKeyboardMarkup(row_width=2)
        if db.check_item_id(item_name, item_type, item_size) == 'empty':
            kb.add(types.InlineKeyboardButton(text='Да', callback_data=f'add_new_item|{item_type}|{item_name}|{item_size}'),
                   types.InlineKeyboardButton(text='Нет', callback_data='delete_message'))
            kb.add(types.InlineKeyboardButton(text='Редактировать', callback_data=f'change_item_data|{item_type}|{item_name}|{item_size}'))
            bot.send_message(message.from_user.id, 'Товара {} категории {} размера {} нет в каталоге. Добавить его?'
                             .format(item_name, item_type, item_size), reply_markup=kb)
        else:
            item_id = db.get_item_id(item_name, item_type, item_size)
            send_item_info(message, item_id)
    else:
        if changed_data == 'item_type':
            mesg = bot.send_message(message.from_user.id, "Введите нужную категорию:")
        elif changed_data == 'item_name':
            mesg = bot.send_message(message.from_user.id, "Введите название:")
        else:
            mesg = bot.send_message(message.from_user.id, "Введите размер:")
        bot.register_next_step_handler(mesg, edited_check, changed_data, var1, var2)

