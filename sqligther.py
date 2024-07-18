import sqlite3


class SQLither:

    def __init__(self, database):
        """Подключаемся к БД и сохраняем курсор соединения"""
        self.connection = sqlite3.connect(database, check_same_thread=False)
        self.cursor = self.connection.cursor()
        self.is_processing = False

    def get_subscriber(self, user_id):
        """Проверяем, есть ли юзер в базе"""
        with self.connection:
            result = self.cursor.execute('SELECT * FROM `users` WHERE `user_id` = ?', (user_id,)).fetchall()
            return bool(len(result))

    def add_subscriber(self, user_id):
        """Добавляем юзера"""
        with self.connection:
            self.cursor.execute("INSERT INTO `users` (`user_id`) VALUES(?)", (user_id,))

    def get_userid(self, user_id):
        """Получаем id юзера"""
        with self.connection:
            return self.cursor.execute('SELECT `user_id` FROM `users` WHERE `user_id` = ?', (user_id,)).fetchone()[0]

    def update_username(self, user_id, user_name):
        """Добавляем имя в базу"""
        with self.connection:
            return self.cursor.execute('UPDATE `users` SET `user_name` = ? WHERE `user_id` = ?', (user_name, user_id,))

    def get_username(self, user_id):
        """Получаем  имя юзера"""
        with self.connection:
            return self.cursor.execute('SELECT `user_name` FROM `users` WHERE `user_id` = ?', (user_id,)).fetchone()[0]

    def get_adminstatus(self, user_id):
        """Проверяем является ли юзер админом"""
        with self.connection:
            return self.cursor.execute('SELECT `admin_status` FROM `users` WHERE `user_id` = ?',
                                       (user_id,)).fetchone()[0]

    def get_user_discount(self, user_id):
        """Получаем персональную скидку юзера"""
        with self.connection:
            return self.cursor.execute('SELECT `personal_discount` FROM `users` WHERE `user_id` = ?',
                                       (user_id,)).fetchone()[0]

    def get_user_total_amount(self, user_id):
        """Получаем сумму всех покупок юзера"""
        with self.connection:
            return self.cursor.execute('SELECT `total_amount_of_purchase` FROM `users` WHERE `user_id` = ?',
                                       (user_id,)).fetchone()[0]

    def update_adminstatus(self, user_id, admin_status):
        """Делаем юзера админом"""
        with self.connection:
            return self.cursor.execute('UPDATE `users` SET `admin_status` = ? WHERE `user_id` = ?',
                                       (admin_status, user_id,))

    def update_user_total_amount(self, user_id, amount):
        """Изменяем общую сумму покупок юзера"""
        with self.connection:
            return self.cursor.execute('UPDATE `users` SET `total_amount_of_purchase` = `total_amount_of_purchase` + ? '
                                       'WHERE `user_id` = ?', (amount, user_id,))

    def update_personal_discount(self, user_id, personal_discount):
        """Изменяем персональную скидку юзера"""
        with self.connection:
            return self.cursor.execute('UPDATE `users` SET `personal_discount` = ? WHERE `user_id` = ?',
                                       (personal_discount, user_id,))

    def get_items_names(self):
        """Получаем название всех товаров"""
        with self.connection:
            return self.cursor.execute('SELECT `item_name` FROM `catalog`').fetchall()

    def get_all_items_id(self):
        """Получаем id всех товаров в виде пронумерованного списка"""
        with self.connection:
            result = list(self.cursor.execute("SELECT DISTINCT `item_id` FROM `catalog`").fetchall())
            result_list = []
            for i, value in enumerate(result, start=1):
                result_list.append(value[0])  # добавляем значение в массив
            return result_list

    def get_items_types(self):
        """Получаем список доступных категорий товаров в виде пронумерованного списка и строки"""
        if self.is_processing:
            return None
        with self.connection:
            self.is_processing = True
            result = list(self.cursor.execute("SELECT DISTINCT `item_type` FROM `catalog`").fetchall())
            result_list = []
            result_str = f"\nСписок имеющихся категорий:"
            for i, value in enumerate(result, start=1):
                result_list.append(value[0])  # добавляем значение в массив
                result_str += f'\n{i}. {value[0]}'  # формируем строку для вывода
            self.is_processing = False
            return result_list, result_str

    def get_all_items_names(self, item_type, discount_status):
        """Получаем список доступных товаров в виде пронумерованного списка и строки"""
        if self.is_processing:
            return None
        with self.connection:
            self.is_processing = True
            if int(discount_status) == 0:
                result = list(self.cursor.execute("SELECT DISTINCT `item_name` FROM `catalog` WHERE `item_type` = ?",
                                                  (item_type,)).fetchall())
            elif int(discount_status) == 1:
                result = list(self.cursor.execute("SELECT DISTINCT `item_name` FROM `catalog` WHERE `item_type` = ? AND "
                                                  "`percentage_discount` > 0", (item_type,)).fetchall())
            result_list = []
            result_str = f"\nСписок числящихся товаров:"
            for i, value in enumerate(result, start=1):
                result_list.append(value[0])  # добавляем значение в массив
                result_str += f'\n{i}. {value[0]}'  # формируем строку для вывода
            self.is_processing = False
            return result_list, result_str

    def get_item_sizes(self, item_name, item_type, discount_status):
        """Получаем пронумерованный список доступных размеров товара"""
        if self.is_processing:
            return None
        with self.connection:
            self.is_processing = True
            # Получаем все значения из столбца `item_size`
            if int(discount_status) == 0:
                result = list(self.cursor.execute('SELECT `item_size` FROM `catalog` WHERE `item_name` = ? '
                                              'AND `item_type` = ?', (item_name, item_type,)).fetchall())
            elif int(discount_status) == 1:
                result = list(self.cursor.execute('SELECT `item_size` FROM `catalog` WHERE `item_name` = ? '
                                                  'AND `item_type` = ? AND `percentage_discount` > 0',
                                                  (item_name, item_type,)).fetchall())
            result_list = []
            result_str = f"\nСписок доступных размеров:"
            for i, value in enumerate(result, start=1):
                result_list.append(value[0])  # добавляем значение в массив
                result_str += f'\n{i}. {value[0]}'  # формируем строку для вывода
            self.is_processing = False
            return result_list, result_str

    def get_item_collections(self):
        """Получаем список доступных коллекций в виде пронумерованного списка и строки"""
        if self.is_processing:
            return None
        with self.connection:
            self.is_processing = True
            # Получаем все значения из столбца `item_name`
            result = list(self.cursor.execute("SELECT DISTINCT `collection` FROM `catalog`").fetchall())
            result_list = []
            result_str = f"\nСписок имеющихся коллекций:"
            for i, value in enumerate(result, start=1):
                result_list.append(value[0])  # добавляем значение в массив
                result_str += f'\n{i}. {value[0]}'  # формируем строку для вывода
            self.is_processing = False
            return result_list, result_str

    def get_item_id(self, item_name, item_type, item_size):
        """Получаем id товара после фильтров"""
        with self.connection:
            return self.cursor.execute('SELECT `item_id` FROM `catalog` WHERE `item_name` = ? AND `item_type` = ? '
                                       'AND `item_size` = ?', (item_name, item_type, item_size,)).fetchone()[0]

    def check_item_id(self, item_name, item_type, item_size):
        """Проверяем есть ли id товара после фильтров"""
        with self.connection:
            result = self.cursor.execute('SELECT `item_id` FROM `catalog` WHERE `item_name` = ? AND `item_type` = ? '
                                         'AND `item_size` = ?', (item_name, item_type, item_size,)).fetchone()
        if result is None:
            return 'empty'
        else:
            return 'full'

    def get_item_name(self, item_id):
        """Получаем название товара"""
        with self.connection:
            return self.cursor.execute('SELECT `item_name` FROM `catalog` WHERE `item_id` = ?', (item_id,)).fetchone()[0]

    def get_item_type(self, item_id):
        """Получаем тип товара"""
        with self.connection:
            return self.cursor.execute('SELECT `item_type` FROM `catalog` WHERE `item_id` = ?', (item_id,)).fetchone()[0]

    def get_item_count(self, item_id):
        """Получаем количество товара"""
        with self.connection:
            return self.cursor.execute('SELECT `count` FROM `catalog` WHERE `item_id` = ?', (item_id,)).fetchone()[0]

    def get_item_size(self, item_id):
        """Получаем размер товара"""
        with self.connection:
            return self.cursor.execute('SELECT `item_size` FROM `catalog` WHERE `item_id` = ?', (item_id,)).fetchone()[0]

    def get_item_price(self, item_id):
        """Получаем цену товара"""
        with self.connection:
            return self.cursor.execute('SELECT `price` FROM `catalog` WHERE `item_id` = ?', (item_id,)).fetchone()[0]

    def get_item_percentage_discount(self, item_id):
        """Получаем проценты скидки на товар"""
        with self.connection:
            return self.cursor.execute('SELECT `percentage_discount` FROM `catalog` WHERE `item_id` = ?',
                                       (item_id,)).fetchone()[0]

    def get_item_collection(self, item_id):
        """Получаем колекцию товара"""
        with self.connection:
            return self.cursor.execute('SELECT `collection` FROM `catalog` WHERE `item_id` = ?',(item_id,)).fetchone()[0]

    def update_item_price(self, item_id, price):
        """Меняем цену товара"""
        with self.connection:
            return self.cursor.execute('UPDATE `catalog` SET `price` = ? WHERE `item_id` = ?',(price, item_id,))

    def update_item_discount(self, percentage_discount, column, data):
        """Меняем скидку товара"""
        with self.connection:
            return self.cursor.execute('UPDATE `catalog` SET `percentage_discount` = ? '
                                       f'WHERE `{column}` = ?', (percentage_discount, data,))

    def update_item_count(self, item_id, count):
        """Меняем количество товара"""
        with self.connection:
            return self.cursor.execute('UPDATE `catalog` SET `count` = `count` + ? WHERE `item_id` = ?',
                                       (count, item_id,))

    def add_to_cart(self, user_id, item_id):
        """Добавляем новый товар в корзину"""
        with self.connection:
            self.cursor.execute('INSERT INTO `cart` (`user_id`, `item_id`) VALUES(?, ?)', (user_id, item_id,))

    def get_items_from_cart(self, user_id):
        """Получаем все id товаров из корзины для определенного юзера"""
        with self.connection:
            result = list(self.cursor.execute('SELECT `item_id` FROM `cart` WHERE `user_id` = ?', (user_id,)).fetchall())
            result_list = []
            for i, value in enumerate(result, start=1):
                result_list.append(value[0])  # добавляем значение в массив
            return result_list

    def get_item_quantity_cart(self, user_id, item_id):
        """Проверяем количество товара в корзине"""
        with self.connection:
            return self.cursor.execute('SELECT `quantity` FROM `cart` WHERE `user_id` = ? AND `item_id` = ?',
                                       (user_id, item_id,)).fetchone()[0]

    def check_item_quantity_cart(self, user_id, item_id):
        """Проверяем количество товара в корзине"""
        with self.connection:
            result = self.cursor.execute('SELECT `quantity` FROM `cart` WHERE `user_id` = ? AND `item_id` = ?',
                                         (user_id, item_id,)).fetchone()
        if result is None:
            return 0
        else:
            return self.get_item_quantity_cart(user_id, item_id)

    def delete_item_from_cart(self, user_id, item_id):
        """Удаляем все количество одного товара из корзины"""
        with self.connection:
            self.cursor.execute('DELETE FROM `cart` WHERE `user_id` = ? AND `item_id` = ?', (user_id, item_id,))

    def change_item_quantity_cart(self, quantity, user_id, item_id):
        """Удаляем единицу товара из корзины"""
        with self.connection:
            self.cursor.execute('UPDATE `cart` SET `quantity` = `quantity` + ?  WHERE `user_id` = ? AND `item_id` = ?',
                                (quantity, user_id, item_id,))

    def delete_items_from_cart_user(self, user_id):
        """Удаляем все товары из корзины для одного пользователя"""
        with self.connection:
            self.cursor.execute('DELETE FROM `cart` WHERE `user_id` = ?', (user_id,))

    def users_with_cart(self):
        """Получаем список пользователей, у которых есть товары в корзине"""
        with self.connection:
            result = list(self.cursor.execute('SELECT DISTINCT `user_id` FROM `cart`').fetchall())
            result_list = []
            for i, value in enumerate(result, start=1):
                result_list.append(value[0])  # добавляем значение в массив
            return result_list

    def items_in_carts(self):
        """Получаем список товаров, которые есть в чей-либо корзине"""
        with self.connection:
            result = list(self.cursor.execute('SELECT `item_id` FROM `cart`').fetchall())
            result_list = []
            for i, value in enumerate(result, start=1):
                result_list.append(value[0])  # добавляем значение в массив
            return result_list

    def set_item_quantity_cart(self, quantity, user_id, item_id):
        """Задаем кол-во товара в корзине"""
        with self.connection:
            self.cursor.execute('UPDATE `cart` SET `quantity` = ?  WHERE `user_id` = ? AND `item_id` = ?',
                                (quantity, user_id, item_id,))

    def users_with_certain_item_in_cart(self, item_id):
        """Получаем список пользователей, у которых есть определенные товары в корзине"""
        with self.connection:
            result = list(self.cursor.execute('SELECT `user_id` FROM `cart` WHERE `item_id` = ?',
                                              (item_id,)).fetchall())
            result_list = []
            for i, value in enumerate(result, start=1):
                result_list.append(value[0])  # добавляем значение в массив
            return result_list

    def add_new_item(self, item_type, item_name, item_size, item_collection, item_count, item_price):
        """Добавляем товар в бд"""
        with self.connection:
            self.cursor.execute('INSERT INTO `catalog`(`item_type`, `item_name`, `item_size`, `collection`, `count`,'
                                ' `price`) VALUES(?, ?, ?, ?, ?, ?)',
                                (item_type, item_name, item_size, item_collection, item_count, item_price,))
