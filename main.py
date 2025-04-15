import os

import pandas as pd

from src.reports import spending_by_weekday
from src.services import search_transaction
from src.views import get_main_page

ROOT_DIR = os.path.abspath(os.path.join(__file__, '..'))

def main():
    # собираем данные, датафрейм для веб-страницы и отчёта, и делаем список словарей для сервиса
    transactions_file_path = os.path.join(ROOT_DIR, "data", "operations.xlsx")
    transactions_as_df = pd.read_excel(transactions_file_path)
    transactions_as_list_dicts = transactions_as_df.to_dict(orient='records')

    # Вызываем главную, отдаём ДАТАФРЕЙМ и дату, дату можно взять от пользователя инпутом
    print("Главная")
    user_input_page = input('Введите желаемую дату, (Пример ввода: 31.12.2020 16:44:00): ')
    page_result = get_main_page(transactions_as_df, user_input_page)
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
    print(result)

