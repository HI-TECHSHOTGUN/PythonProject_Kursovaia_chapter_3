# import os
#
# from src.reports import spending_by_weekday
# from src.services import search_transaction
# from src.views import (api_sp_500, get_top_five_transactions,
#                        open_excel_file_func, open_json_user_settings,
#                        read_exc_file_cards, time_greetings, valet_rub)
#
# ABS_PATH = os.path.abspath(os.path.join(os.getcwd()))
#
#
# def main():
#     main_dict = {}
#     service_dict = {}
#     report_dict = {}
#     print("Главная")
#     main_dict["greeting"] = time_greetings()
#     open_excel = open_excel_file_func(os.path.join(ABS_PATH, "data", "operations.xlsx"))
#     main_dict["cards"] = read_exc_file_cards(open_excel)
#     main_dict["top_transactions"] = get_top_five_transactions(open_excel)
#     main_dict["currency_rates"] = valet_rub(
#         open_json_user_settings(os.path.join(ABS_PATH, "data", "user_settings.json"))
#     )
#     main_dict["stock_prices"] = api_sp_500(
#         open_json_user_settings(os.path.join(ABS_PATH, "data", "user_settings.json"))
#     )
#     print(main_dict)
#     print("Сервисы")
#     search_input = input("Введите желаемый запрос: ")
#     service_dict["all_search"] = search_transaction(search_input, open_excel)
#     print(service_dict)
#     print("Отчеты")
#     report_input = input("Введите дату в формате: ДД.ММ.ГГГГ ")
#     report_dict["report"] = spending_by_weekday(open_excel, report_input)
#     print(report_dict)
#     return "На этом все, памагите"
#
#
# if __name__ == "__main__":
#     result = main()

import os

import pandas as pd

from src.reports import spending_by_weekday
from src.services import search_transaction
from src.views import get_main_page

ROOT_DIR = os.path.dirname(__file__)

def main():
    # собираем данные, датафрейм для веб-страницы и отчёта, и делаем список словарей для сервиса
    transactions_file_path = os.path.join(ROOT_DIR, "data", "operations.xlsx")
    transactions_as_df = pd.read_excel(transactions_file_path)
    transactions_as_list_dicts = transactions_as_df.to_dict(orient='records')

    # Вызываем главную, отдаём ДАТАФРЕЙМ и дату, дату можно взять от пользователя инпутом
    print("Главная")
    user_input_page = input('Введите желаемую дату')
    page_result = get_main_page(transactions_as_df, "2021-12-11 05:02:35")
    print(page_result)

    # Вызываем сервис, отдаём список словарей и запрос возьмём от пользователя
    print("Сервисы")
    search_input = input("Введите желаемый запрос: ")
    service_result = search_transaction(search_input, transactions_as_list_dicts)
    print(service_result)

    # Вызываем отчёт, отдаём ДАТАФРЕЙМ и дату
    print("Отчеты")
    report_input = input("Введите дату в формате: ДД.ММ.ГГГГ ")
    report_result = spending_by_weekday(transactions_as_df, report_input)
    print(report_result)
    return "На этом все, памагите"

if __name__ == "__main__":
    result = main()
