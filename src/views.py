import datetime
import json
import os

import pandas as pd
import requests


ABS_PATH = os.path.abspath(os.path.join(os.getcwd(), ".."))
API_KEY = '2ba1e8f7be014ddabf64ab8d358d8fae'


def time_greetings():
    """Функция для отладки приветствия по реальному времени"""
    try:
        time_now = datetime.datetime.now()
        time_string = time_now.hour
        if 6 <= time_string < 12:
            greeting = 'Доброе утро'
        elif 12 <= time_string < 18:
            greeting = 'Добрый день'
        elif 18 <= time_string < 22:
            greeting = 'Добрый вечер'
        else:
            greeting = 'Доброй ночи'

        return greeting
    except Exception as e:
        return f'Error {e}'


# print(time_greetings())


# def clear_json_file(filename):
#     """Очищает JSON-файл, записывая в него пустой словарь."""
#     try:
#         with open(filename, "w", encoding="utf-8") as f:
#             json.dump({}, f, indent=4, ensure_ascii=False)
#         return f'Файл {filename} успешно очищен (записан пустой словарь)'
#
#     except Exception as e:
#         return f'Ошибка при очистке файла: {e}'
#
# print(clear_json_file(os.path.join(ABS_PATH, 'data', 'user_settings.json')))


def open_excel_file_func(file_name_excel):
    """Функция для открытия excel файла"""
    try:
        excel_open = pd.read_excel(file_name_excel)
        excel_to_dict = excel_open.to_dict(orient="records")
        return excel_to_dict
    except Exception as e:
        return f'Error {e}'


open_excel = open_excel_file_func(os.path.join(ABS_PATH, 'data', 'operations.xlsx'))
# print(open_excel)


def read_exc_file_cards(file_name_excel):
    """Функция для сортировки данных по картам"""
    list_all_info = []
    list_cashback = []
    list_card_number = []
    total_spent_list = []
    try:
        for i in file_name_excel:
            if str(i['Номер карты']).startswith('*'):
                str_reload = str(i['Номер карты'])[1:]
                if str_reload in list_card_number:
                    continue

                else:
                    list_card_number.append(str_reload)
        for j in list_card_number:
            total_spent = 0
            j = '*' + j
            for k in file_name_excel:
                if k['Номер карты'] == j:
                    str_total_spent = f"{k['Сумма платежа']:.2f}"
                    if str_total_spent.startswith('-'):
                        str_total_spent = str_total_spent[1:]
                        total_spent += float(str_total_spent)
                else:
                    continue
            total_spent = float(f"{total_spent:.2f}")
            total_spent_list.append(total_spent)

        for l in total_spent_list:
            cash_back = l/100
            cash_back = float(f"{cash_back:.2f}")
            list_cashback.append(cash_back)

        for p in range(len(list_card_number)):
            _dict = {"last_digits": list_card_number[p], "total_spent": total_spent_list[p],
                     "cashback": list_cashback[p]}
            list_all_info.append(_dict)
        return list_all_info

    except Exception as e:
        return f'Error {e}'

# print(read_exc_file_cards(open_excel))


def open_json_user_settings(filepath):
    """Развертка json файла с пользовательскими данными"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data

    except Exception as e:
        return f'Error {e}'

# print(open_json_user_settings(os.path.join(ABS_PATH, 'data', 'user_settings.json')))
test_dict = os.path.join(ABS_PATH, 'data', 'user_settings.json')

def api_sp_500(setting_dict):
    """Запрос на стоимость акций"""
    json_result = []
    try:
        for i in setting_dict['user_stocks']:
            dict_result = {}
            url_sp = f'https://api.twelvedata.com/price?symbol={i}&apikey={API_KEY}'
            req_1 = requests.get(url_sp)
            data = req_1.json()
            dict_result['stock'], dict_result['price'] = i, data['price']
            json_result.append(dict_result)

        return json_result
    except Exception as e:
        return f'Error {e}'

# print(api_sp_500(open_json_user_settings(test_dict)))


def valet_rub(setting_dict):
    """Запрос конвертации валюты в рубли"""
    json_result = []
    try:
        for i in setting_dict['user_currencies']:
            dict_result = {}
            url_sp = f'https://api.twelvedata.com/exchange_rate?symbol={i}/RUB&apikey={API_KEY}'
            req_1 = requests.get(url_sp)
            data = req_1.json()
            dict_result['currency'], dict_result['rate'] = i, data['rate']
            json_result.append(dict_result)
        return json_result
    except Exception as e:
        return f'Error {e}'

# print(valet_rub(open_json_user_settings(test_dict)))


def search_transaction(search_input, open_file_exc):
    try:
        if search_input == '':
            return 'Строка пустая'
        else:
            for i in open_file_exc:
                if search_input.lower() in str(i['Категория']).lower():
                    print(i)
                elif search_input.lower() in str(i['Описание']).lower():
                    print(i)
            return 'Вот все что удалось найти'
    except Exception as e:
        return f'{e}'

# print(search_transaction('+', open_excel))


