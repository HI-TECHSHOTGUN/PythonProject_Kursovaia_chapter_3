import logging
import os
import datetime

import pandas as pd


ABS_PATH = os.path.abspath(os.path.join(os.getcwd(), ".."))

all_transactions_df = pd.read_excel(os.path.join(ABS_PATH, 'data', 'operations.xlsx'))

# logger = logging.getLogger("views.log")
# file_handler = logging.FileHandler("views.log", "w")
# file_formatter = logging.Formatter("%(asctime)s %(levelname)s: %(message)s")
# file_handler.setFormatter(file_formatter)
# logger.addHandler(file_handler)
# logger.setLevel(logging.INFO)
#
# logger.info("Конец работы функции (filter_by_date)")
# logger.info("Начало работы функции (filter_by_date)")


def get_main_page(df, date_time_str):
    try:
        date_time_obj = datetime.datetime.strptime(date_time_str, "%Y-%m-%d %H:%M:%S")
        hour = date_time_obj.hour

        if 6 <= hour < 12:
            greeting = "Доброе утро"
        elif 12 <= hour < 18:
            greeting = "Добрый день"
        elif 18 <= hour < 23:
            greeting = "Добрый вечер"
        else:
            greeting = "Доброй ночи"
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

        currency_rates = [
            {"currency": "USD", "rate": 73.21},
            {"currency": "EUR", "rate": 87.08}
        ]

        stock_prices = [
            {"stock": "AAPL", "price": 150.12},
            {"stock": "AMZN", "price": 3173.18},
            {"stock": "GOOGL", "price": 2742.39},
            {"stock": "MSFT", "price": 296.71},
            {"stock": "TSLA", "price": 1007.08}
        ]

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



page_result = get_main_page(all_transactions_df, "2021-12-11 05:02:35")
print(page_result)
# for i in all_transactions_df:
#     if count > 10:
#         break
#     else:
#         print(i)