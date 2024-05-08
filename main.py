import asyncio
import base64
import json
import os
from getpass import getpass
import logging
from datetime import datetime
import aiofiles
from icecream import ic
import re
from hashing_pass import verify_password, hash_passwords
from pagination import Paginator, TextPagination

flag_read = False

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')


async def current_date():
    current_datetime = datetime.now()
    formatted_date = current_datetime.strftime("%d.%m.%Y")
    return formatted_date

class ReadFile:
    @staticmethod
    async def read_file():
        async with aiofiles.open('balance_hystory.txt', mode='r+') as f:
            file_content = await f.read()
            ic(file_content)
            # Проверяем, не пустой ли файл
            if not file_content:
                # Возвращаем пустой словарь, если файл пуст
                return {}
            return json.loads(file_content)


class WriteFile:
    lock: asyncio.Lock = asyncio.Lock()
    @staticmethod
    async def write_file(data: dict):
        logging.debug("Попытка сохранения файла")
        try:
            async with WriteFile.lock:
                async with aiofiles.open('balance_hystory.txt', mode='w+', encoding='utf-8') as f:
                    await f.write(json.dumps(data))
                logging.debug("Файл успешно сохранен")
        except Exception as e:
            logging.error("Ошибка при сохранении файла:", exc_info=True)


class DescriptionUser:
    @staticmethod
    async def description_user():
        pass


class Balance:

    def __init__(self, user=None):
        self.user: str = user
        self._balance: float = 0.0

    @property
    def get_balance(self):
        return self._balance

    @get_balance.setter
    def get_balance(self, value):
        if value < 0:
            raise ValueError('Баланс не должен быть отрицательным')
        self._balance = value

    async def update_balance(self, value):
        self._balance += value

    async def subtract_balance(self, value):
        if value > self._balance:
            raise ValueError('Недостаточно средств для списания')
        self._balance -= value




async def balance_view(objects, data: dict):

    balance: float = objects.get_balance
    text: str = f'Ваш баланс:\n{balance}'
    print(text)
    input('Нажмите Enter для продолжения')


async def replesh_balance(objects, data: dict):
    user_input: str = input('Сколько вы хотите пополнить: ')
    if user_input.isdigit():
        await objects.update_balance(float(user_input))
        description: str = input('Описание пополнения: ')
        print(f'Баланс пополнен.\nВаш баланс: {objects.get_balance}')
        data[objects.user]['balance'] = objects.get_balance
        if not data[objects.user]['history'].get('incomes'):
            data[objects.user]['history']['incomes'] = []
        data[objects.user]['history']['incomes'].append({
            'date': await current_date(),
            'description': description,
            'amount': float(user_input)
        })
        await WriteFile.write_file(data)
        input('Нажмите Enter для продолжения')


async def expenses_balance(objects, data: dict):
    user_input: str = input('Сумма вычета: ')
    if user_input.isdigit():
        await objects.subtract_balance(float(user_input))
        description: str = input('Описание пополнения: ')
        print(f'Из баланса вычтена сумма {user_input}.\nТекущий баланс: {objects.get_balance}')
        data[objects.user]['balance'] = objects.get_balance
        if not data[objects.user]['history'].get('expenses'):
            data[objects.user]['history']['expenses'] = []
        data[objects.user]['history']['expenses'].append({
            'date': await current_date(),
            'description': description,
            'amount': float(user_input)
        })
        await WriteFile.write_file(data)
        input('Нажмите Enter для продолжения')


async def change_date(user: str, data: dict, number: int, category: str):
    data[user]['history'][category][number - 1]['date'] = input('Новая дата: ')


async def change_description(user: str, data: dict, number: int, category: str):
    data[user]['history'][category][number - 1]['description'] = input('Новое описание: ')


async def delete_history(objects: Balance, data: dict, number: int, category: str):
    data[objects.user]['balance'] -= data[objects.user]['history'][category][number - 1]['amount']
    data[objects.user]['history'][category].pop(number - 1)
    objects.get_balance = data[objects.user]['balance']


async def change_amount(objects: Balance, data: dict, number: int, category: str):
    new_amount = float(input('Новая сумма: '))
    old_amount = data[objects.user]['history'][category][number - 1]['amount']
    data[objects.user]['balance'] -= old_amount
    data[objects.user]['balance'] += new_amount
    objects.get_balance = data[objects.user]['balance']
    data[objects.user]['history'][category][number - 1]['amount'] = new_amount


async def edit_history(objects, data: dict, number: int, category: str):
    options = input('Что вы хотите изменить?\n(1 - дату, 2 - описание, 3 - сумму, 4 - удалить запись, 0 - выход): ')
    ic(options, category)
    user = objects.user
    actions = {
        '1': lambda: change_date(user, data, number, category),
        '2': lambda: change_description(user, data, number, category),
        '3': lambda: change_amount(objects, data, number, category),
        '4': lambda: delete_history(objects, data, number, category)
    }
    if options in actions:
        await actions[options]()
    else:
        print('Неверное значение')
    await WriteFile.write_file(data)

async def hystory_view(objects: Balance, data: dict, category: str, lst: list=None):
    try:
        for j, i in enumerate(data[objects.user]['history']['incomes'], start=1):
            lst.append(f'{j}. {i["date"]} - {i["description"]} - {i["amount"]}\n')
    except KeyError:
        print('Пополнения не были совершены')

async def app_history(objects, data: dict):
    while True:
        user_input: str = input('История пополнения или вычетов?\n(1 - пополнения, 2 - вычеты, 0 - выход): ')
        text: list = []
        category = 'incomes' if user_input == '1' else 'expenses'
        ic(user_input, category)
        actions = {
            '1': lambda: hystory_view(objects, data, 'incomes', text),
            '2': lambda: hystory_view(objects, data, 'expenses', text)
        }
        if user_input in actions:
            await actions[user_input]()
        else:
            break
        paginator = Paginator(text, 50)
        await paginator.pagination()
        textPagination = TextPagination(paginator.sublists)
        await textPagination.mains()
        print()
        user_input = input('Укажите номер записи для редактирования, удаления или\nНажмите Enter чтобы выйти: ')
        if user_input.isdigit():
            number = int(user_input)
            await edit_history(objects, data, number, category)
        else:
            break


async def app_search(objects, data: dict):
    user_input = input(
        'Поиск по дате категории или сумме?\n(Введите запрос в формате дата, категория(Пополнение/Вычет) или сумма, 0 - выход): ').strip().lower()
    date_regex = r"^(0[1-9]|[12][0-9]|3[01])\.(0[1-9]|1[012])\.(\d{4})$"
    amount_regex = r"^[0-9]+([.,][0-9]{1,2})?$"
    ic(data[objects.user]['history'])
    def search_by_date():
        # Получаем список пополнений и вычетов, если они есть, иначе возвращаем пустой список
        incomes = data[objects.user]['history'].get('incomes', [])
        expenses = data[objects.user]['history'].get('expenses', [])

        list_search = [
            f'Пополнение: {item["date"]} - {item["description"]} - {item["amount"]}\n'
            for item in incomes
            if item['date'] == user_input
        ]
        list_search.extend(
            f'Вычет: {item["date"]} - {item["description"]} - {item["amount"]}\n'
            for item in expenses
            if item['date'] == user_input
        )
        return list_search

    def search_by_amount():
        user_input_corrected = user_input.replace(',', '.')
        list_search = [
            f'{t}: {item["date"]} - {item["description"]} - {item["amount"]}\n'
            for t in ['Пополнение', 'Вычет']
            for item in data[objects.user]['history'].get(f'incomes' if t == 'Пополнение' else 'expenses', [])
            if item['amount'] == float(user_input_corrected)
        ]
        return list_search

    def search_by_category():
        category = 'incomes' if user_input == 'пополнение' else 'expenses'
        list_search = [
            f'{user_input.capitalize()}: {item["date"]} - {item["description"]} - {item["amount"]}\n'
            for item in data[objects.user]['history'][category]
        ]
        return list_search

    search_options = {
        'date': search_by_date,
        'amount': search_by_amount,
        'пополнение': search_by_category,
        'вычет': search_by_category
    }

    result_type = 'date' if re.match(date_regex, user_input) else 'amount' if re.match(amount_regex,
                                                                                       user_input) else user_input
    ic(result_type)
    list_search = search_options[result_type]() if result_type in search_options else []

    if not list_search:
        print('Ничего не найдено')
    else:
        print('Результат поиска:')
        paginator = Paginator(list_search, 50)
        await paginator.pagination()
        text_pagination = TextPagination(paginator.sublists)
        await text_pagination.mains()



async def app_run(objects, data: dict):
    commands = {
        '2': balance_view,
        '3': replesh_balance,
        '4': expenses_balance,
        '5': app_history,
        '6': app_search
    }
    ic(objects.user)
    while (user_input := input("Выберете команду из списка:\n(введите '1' для выхода, '2' для проверка баланса,\n"
                               "'3' для добавления дохода, '4' для добавления расхода\n"
                               "'5' для вывода истории, '6' поиск записей): ")) != '1':
        ic(flag_read)
        if user_input in commands:
            try:
                await commands[user_input](objects, data)
            except ValueError as e:
                print('Такого действия нет', e)
        else:
            print('Такой команды нет')
    else:
        print('Программа завершена')


async def start():
    data = {}
    if not os.path.exists('balance_hystory.txt'):
        await WriteFile.write_file({
            'balance': 0
        })
    data = await ReadFile.read_file()
    ic(data)
    user = input('Ваш логин: ')
    flag = False
    while flag is False:
        if data.get(user):
            balance = Balance(user=user)
            password = getpass('Ваш пароль: ')
            passw = base64.b64decode(data[user]['password'].encode('utf-8'))
            if await verify_password(password, passw):
                balance.get_balance = data[user]['balance']
                flag = True
                await app_run(balance, data)
                # await asyncio.gather(*asyncio.all_tasks())
            else:
                print('Неверный пароль')
        else:
            print('Для регистрации укажите пароль')
            password = getpass('Ваш пароль: ')
            ic(password)
            hash_pass = await hash_passwords(password)
            hash_pass = base64.b64encode(hash_pass).decode('utf-8')
            data[user] = {
                'balance': 0,
                'password': hash_pass,
                'history': {},
            }
            await WriteFile.write_file(data)


if __name__ == '__main__':
    asyncio.run(start())
