import logging
import os
import datetime

import pandas as pd

from src.utils import time_greetings, open_json_user_settings, valet_rub, api_sp_500, sorted_pd_df

ABS_PATH = os.path.abspath(os.path.join(os.getcwd(), ".."))
#
# all_transactions_df = pd.read_excel(os.path.join(ABS_PATH, 'data', 'operations.xlsx'))

# logger = logging.getLogger("views.log")
# file_handler = logging.FileHandler("views.log", "w")
# file_formatter = logging.Formatter("%(asctime)s %(levelname)s: %(message)s")
# file_handler.setFormatter(file_formatter)
# logger.addHandler(file_handler)
# logger.setLevel(logging.INFO)
#
# logger.info("Конец работы функции (filter_by_date)")
# logger.info("Начало работы функции (filter_by_date)")


def get_main_page(df_not_sorted: pd.DataFrame, date_time_str):
    try:
        df = sorted_pd_df(df_not_sorted, date_time_str)
        greeting = time_greetings()
        required_columns = ["Дата операции", "Номер карты", "Сумма операции", "Категория", "Описание"]
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
        expenses_top = df['Сумма операции'].astype(str).str.startswith('-')
        top_transactions = df[expenses_top].sort_values(by='Сумма операции', ascending=True).head(5)
        top_transactions = top_transactions.rename(columns={
            'Дата операции': 'date',
            'Сумма операции': 'amount',
            'Категория': 'category',
            'Описание': 'description'
        })
        try:
            top_transactions['amount'] = pd.to_numeric(top_transactions['amount'], errors='coerce')
            top_transactions = top_transactions.dropna(subset=['amount'])
            top_transactions['amount'] = abs(top_transactions['amount']).round(2)

        except ValueError as e:
            return {"error": f"Ошибка при преобразовании 'Сумма операции' в число для топ транзакций: {str(e)}"}

        top_transactions['date'] = top_transactions['date'].astype(str)

        top_transactions = top_transactions[['date', 'amount', 'category', 'description']].to_dict('records')

        settings_dict = open_json_user_settings(os.path.join(ABS_PATH, 'data', 'user_settings.json'))
        currency_rates = valet_rub(settings_dict)

        stock_prices = api_sp_500(settings_dict)

        result = {
            "greeting": greeting,
            "cards": cards,
            "top_transactions": top_transactions,
            "currency_rates": currency_rates,
            "stock_prices": stock_prices
        }

        return result

    except Exception as e:
        return {"error": f"Произошла непредвиденная ошибка: {str(e)}"}



# page_result = get_main_page(all_transactions_df, '31.12.2020 16:44:00')
# print(ABS_PATH)
