import logging
import os
import datetime

import pandas as pd

from src.utils import time_greetings, open_json_user_settings, valet_rub, api_sp_500, sorted_pd_df, process_card_data, \
    find_top_transactions

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


# def get_main_page(df_not_sorted, date_time_str):
#     try:
#         greeting = time_greetings()
#
#         card_data = process_card_data(df_not_sorted, date_time_str)
#         if 'error' in card_data:
#             return card_data
#
#         top_transactions = find_top_transactions(df_not_sorted, date_time_str)
#         if 'error' in top_transactions:
#             return top_transactions
#
#         settings_dict = open_json_user_settings(os.path.join(ABS_PATH, 'data', 'user_settings.json'))
#         currency_rates = valet_rub(settings_dict)
#
#         stock_prices = api_sp_500(settings_dict)
#
#         result = {
#             "greeting": greeting,
#             "cards": card_data,
#             "top_transactions": top_transactions,
#             "currency_rates": currency_rates,
#             "stock_prices": stock_prices
#         }
#         return result
#
#     except Exception as e:
#         return {"error": f"Произошла непредвиденная ошибка: {str(e)}"}


def get_main_page(df_not_sorted, date_time_str):
    try:
        greeting = time_greetings()

        card_data = process_card_data(df_not_sorted, date_time_str)
        if 'error' in card_data:
            return card_data

        top_transactions = find_top_transactions(df_not_sorted, date_time_str)
        if 'error' in top_transactions:
            return top_transactions

        settings_dict = open_json_user_settings(os.path.join(ABS_PATH, 'data', 'user_settings.json'))
        currency_rates = valet_rub(settings_dict)

        stock_prices = api_sp_500(settings_dict)

        result = {
            "greeting": greeting,
            "cards": card_data,
            "top_transactions": top_transactions,
            "currency_rates": currency_rates,
            "stock_prices": stock_prices
        }

        return result

    except Exception as e:
        return {"error": f"Произошла непредвиденная ошибка: {str(e)}"}




page_result = get_main_page(all_transactions_df, '31.12.2020 16:44:00')
print(page_result)
