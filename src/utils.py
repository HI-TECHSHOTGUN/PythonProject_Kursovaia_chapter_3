import datetime
import json

import os
import pandas as pd
import requests

# ABS_PATH = os.path.abspath(os.path.join(os.getcwd(), ".."))
# all_transactions_df = pd.read_excel(os.path.join(ABS_PATH, "data", "operations.xlsx"))
API_KEY = "2ba1e8f7be014ddabf64ab8d358d8fae"


def time_greetings():
    """Функция для отладки приветствия по реальному времени"""
    try:
        time_now = datetime.datetime.now()
        time_string = time_now.hour
        if 6 <= time_string < 12:
            greeting = "Доброе утро"
        elif 12 <= time_string < 18:
            greeting = "Добрый день"
        elif 18 <= time_string < 22:
            greeting = "Добрый вечер"
        else:
            greeting = "Доброй ночи"

        return greeting
    except Exception as e:
        return f"Error {e}"


def open_json_user_settings(filepath):
    """Развертка json файла с пользовательскими данными"""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data

    except Exception as e:
        return f"Error {e}"


# print(open_json_user_settings(os.path.join(ABS_PATH, 'data', 'user_settings.json')))
# test_dict = os.path.join(ABS_PATH, 'data', 'user_settings.json')


def api_sp_500(setting_dict):
    """Запрос на стоимость акций"""
    json_result = []
    try:
        for i in setting_dict["user_stocks"]:
            dict_result = {}
            url_sp = f"https://api.twelvedata.com/price?symbol={i}&apikey={API_KEY}"
            req_1 = requests.get(url_sp)
            data = req_1.json()
            dict_result["stock"], dict_result["price"] = i, data["price"]
            json_result.append(dict_result)

        return json_result
    except Exception as e:
        return f"Error {e}"


# print(api_sp_500(open_json_user_settings(test_dict)))


def valet_rub(setting_dict):
    """Запрос конвертации валюты в рубли"""
    json_result = []
    try:
        for i in setting_dict["user_currencies"]:
            dict_result = {}
            url_sp = f"https://api.twelvedata.com/exchange_rate?symbol={i}/RUB&apikey={API_KEY}"
            req_1 = requests.get(url_sp)
            data = req_1.json()
            dict_result["currency"], dict_result["rate"] = i, data["rate"]
            json_result.append(dict_result)
        return json_result
    except Exception as e:
        return f"Error {e}"


# print(valet_rub(open_json_user_settings(os.path.join(ABS_PATH, 'data', 'user_settings.json'))))


def open_excel_file_func(file_name_excel):
    """Функция для открытия excel файла"""
    try:
        excel_open = pd.read_excel(file_name_excel).fillna(0)
        excel_to_dict = excel_open.to_dict(orient="records")
        return excel_to_dict
    except Exception as e:
        return f"Error {e}"


# open_excel = open_excel_file_func(os.path.join(ABS_PATH, 'data', 'operations.xlsx'))
# print(open_excel)


def sorted_pd_df(pd_df, analysis_date_str):
    try:
        date_format = "%d.%m.%Y %H:%M:%S"
        analysis_date = pd.to_datetime(analysis_date_str, format=date_format)
        start_date = analysis_date.replace(day=1, hour=0, minute=0, second=0)
        pd_df["Дата операции"] = pd.to_datetime(pd_df["Дата операции"], format=date_format, errors="coerce")
        filtered_df = pd_df[(pd_df["Дата операции"] >= start_date) & (pd_df["Дата операции"] <= analysis_date)]
        filtered_df = filtered_df.sort_values(by="Дата операции", ascending=True)
        return filtered_df

    except Exception as e:
        return f"Error {e}"


# print(sorted_pd_df(all_transactions_df, '31.12.2020 16:44:00'))


def process_card_data(df_not_sorted, date_time_str):
    try:
        df = sorted_pd_df(df_not_sorted, date_time_str)
        required_columns = ["Дата операции", "Номер карты", "Сумма операции"]
        missing_columns = [col for col in required_columns if col not in df.columns]

        if missing_columns:
            return {"error": f"Отсутствуют необходимые столбцы в DataFrame: {', '.join(missing_columns)}"}

        cards = []
        for card_number in df['Номер карты'].unique():
            card_transactions = df[df['Номер карты'] == card_number]
            expenses = card_transactions[card_transactions['Сумма операции'].astype(str).str.startswith('-')]['Сумма операции']
            try:
                expenses = pd.to_numeric(expenses, errors='coerce')
                expenses = expenses.dropna()
                total_spent = abs(expenses.sum())

            except ValueError as e:
                return {"error": f"Ошибка при преобразовании 'Сумма операции' в число: {str(e)}"}

            last_digits = str(card_number)[-4:]
            cashback = round(total_spent * 0.01, 2)

            card_info = {
                "last_digits": last_digits,
                "total_spent": float(round(total_spent, 2)),
                "cashback": float(cashback)
            }
            cards.append(card_info)

        return cards

    except Exception as e:
        return {"error": f"Произошла непредвиденная ошибка: {str(e)}"}



def find_top_transactions(df_not_sorted, date_time_str):
    try:
        df = sorted_pd_df(df_not_sorted, date_time_str)
        required_columns = ["Дата операции", "Сумма операции", "Категория", "Описание"]
        missing_columns = [col for col in required_columns if col not in df.columns]

        if missing_columns:
            return {"error": f"Отсутствуют необходимые столбцы в DataFrame: {', '.join(missing_columns)}"}

        expenses_top = df["Сумма операции"].astype(str).str.startswith("-")
        top_transactions = df[expenses_top].sort_values(by="Сумма операции", ascending=True).head(5)
        top_transactions = top_transactions.rename(
            columns={
                "Дата операции": "date",
                "Сумма операции": "amount",
                "Категория": "category",
                "Описание": "description",
            }
        )

        try:
            top_transactions["amount"] = pd.to_numeric(top_transactions["amount"], errors="coerce")
            top_transactions = top_transactions.dropna(subset=["amount"])
            top_transactions["amount"] = abs(top_transactions["amount"]).round(2)

        except ValueError as e:
            return {"error": f"Ошибка при преобразовании 'Сумма операции' в число для топ транзакций: {str(e)}"}

        top_transactions["date"] = top_transactions["date"].astype(str)
        top_transactions = top_transactions[["date", "amount", "category", "description"]].to_dict("records")

        return top_transactions

    except Exception as e:
        return {"error": f"Произошла непредвиденная ошибка: {str(e)}"}


# print(process_card_data(all_transactions_df, "31.12.2020 16:44:00"))
# print(all_transactions_df["Сумма операции"])
