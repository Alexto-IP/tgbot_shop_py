from sqligther import SQLither
import telebot
import time

TOKEN = 'TOKEN'  # bot token

db = SQLither('newdb.db')  # соединение с бд
bot = telebot.TeleBot(TOKEN)  # токен бота
pas = 'pas'  # пароль для получения статуса администратора
last_click_time = {}
delay_time = 1.5


def delete_message(call):
    bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)


def delay_handler(func):
    def wrapper(call):
        user_id = call.from_user.id
        # Проверяем, прошло ли достаточно времени с момента последнего нажатия
        if user_id in last_click_time and time.time() - last_click_time[user_id] < delay_time:
            bot.delete_message(call.chat.id, call.message_id)
        else:
            # Вызываем оригинальную функцию
            func(call)
            # Запоминаем время последнего нажатия
            last_click_time[user_id] = time.time()
    return wrapper
