import json
import os
from datetime import datetime
from io import StringIO
import requests_mock

import pytest
import pandas as pd
import requests

from src.reports import spending_by_weekday
from src.services import search_transaction
from src.utils import api_sp_500, valet_rub, open_excel_file_func, sorted_pd_df, process_card_data
SETTING_DICT = {
    "user_currencies": ["USD", "EUR"]
}
API_KEY = "fake_api_key"


def test_spending_by_weekday_empty_df():
    """Тест для пустого DataFrame."""
    data = {'Дата платежа': [], 'Сумма платежа': []}
    df = pd.DataFrame(data)
    result = spending_by_weekday(df)
    assert isinstance(result, pd.DataFrame)
    assert len(result) == 7
    assert all(day in result['День недели'].values for day in ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота', 'Воскресенье'])
    assert (result['Сумма платежа'] == 0.0).all()


def test_spending_by_weekday_valid_data():
    """Тест для валидных данных."""
    data = {'Дата платежа': ['01.01.2024', '02.01.2024'],
            'Сумма платежа': [100, 200]}
    df = pd.DataFrame(data)
    result = spending_by_weekday(df, "01.01.2024")
    assert isinstance(result, pd.DataFrame)


def test_spending_by_weekday_with_filename():
    """Тест с указанием имени файла."""
    data = {'Дата платежа': ['01.01.2024', '02.01.2024'],
            'Сумма платежа': [100, 200]}
    df = pd.DataFrame(data)
    result = spending_by_weekday(df, "01.01.2024", filename="test_report.txt")  # Corrected call
    assert isinstance(result, pd.DataFrame)

def test_file_creation():
    """Проверка создания файла."""
    data = {'Дата платежа': ['01.01.2024', '02.01.2024'],
            'Сумма платежа': [100, 200]}
    df = pd.DataFrame(data)
    spending_by_weekday(df, "01.01.2024", filename="test_report.txt")
    assert os.path.exists("test_report.txt")
    os.remove("test_report.txt")


def test_search_with_special_characters():
    """Тест для поиска с использованием специальных символов."""
    transactions = [{"Категория": "Еда!", "Описание": "Обед?"}, {"Категория": "Транспорт", "Описание": "Билет на автобус"}]
    result = search_transaction("еда!", transactions)
    assert len(result) == 1
    assert result[0]["Категория"] == "Еда!"


def test_search_by_description():
    """Тест для поиска по описанию."""
    transactions = [{"Категория": "Еда", "Описание": "Обед"}, {"Категория": "Транспорт", "Описание": "Билет на автобус"}]
    result = search_transaction("обед", transactions)
    assert len(result) == 1
    assert result[0]["Описание"] == "Обед"


def open_json_user_settings(filepath):
    """Развертка json файла с пользовательскими данными"""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data

    except Exception as e:
        return f"Error {e}"


def test_open_nonexistent_file():
    """Тест: Попытка открытия несуществующего файла."""
    result = open_json_user_settings("nonexistent.json")
    assert "Error" in result


def test_api_sp_500_empty_user_stocks(mock_requests_get):
    """Тест: Пустой список user_stocks."""
    setting_dict = {"user_stocks": []}
    result = api_sp_500(setting_dict)
    assert isinstance(result, list)
    assert len(result) == 0


def test_api_sp_500_success(mock_requests_get):
    """Тест: Успешный запрос к API."""
    setting_dict = {"user_stocks": ["AAPL", "MSFT"]}
    result = api_sp_500(setting_dict)
    assert isinstance(result, list)
    assert len(result) == 2
    assert result[0]["stock"] == "AAPL"
    assert result[0]["price"] == '199.20000'
    assert result[1]["stock"] == "MSFT"
    assert result[1]["price"] == '478.87000'


def test_valet_rub_success():
    with requests_mock.Mocker() as m:
        # Мокаем успешный ответ API
        api_response = [
            {"rate": 74.0},
            {"rate": 85.0}
        ]
        for i, currency in enumerate(SETTING_DICT["user_currencies"]):
            url = f"https://api.twelvedata.com/exchange_rate?symbol={currency}/RUB&apikey=fake_api_key"
            m.get(url, json=api_response[i])

        result = valet_rub(SETTING_DICT)
        expected = [
            {"currency": "USD", "rate": 74.0},
            {"currency": "EUR", "rate": 85.0}
        ]
        assert result == expected


def test_valet_rub_empty_list():
    # Тестирование с пустым списком валют
    empty_setting_dict = {
        "user_currencies": []
    }
    result = valet_rub(empty_setting_dict)
    assert result == []


def test_open_excel_file_func_success(mock_excel_data):
    """Тест: Успешное открытие Excel файла."""
    # Создаем фиктивный файл Excel в памяти из строки
    with StringIO(mock_excel_data) as file:
        result = open_excel_file_func(file)
    assert len(result) == 82


def test_sorted_pd_df_success():
    """Тест: Успешное выполнение sorted_pd_df."""
    data = {
        "Дата операции": ["01.01.2023 10:00:00", "15.01.2023 12:00:00", "01.02.2023 08:00:00"],
        "Сумма": [100, 200, 300],
    }
    pd_df = pd.DataFrame(data)

    analysis_date_str = "31.01.2023 23:59:59"

    filtered_df = sorted_pd_df(pd_df, analysis_date_str)

    assert isinstance(filtered_df, pd.DataFrame)
    assert len(filtered_df) == 2  # Ожидаем 2 строки (15.01 и 01.01)
    assert filtered_df["Дата операции"].iloc[0] == datetime(2023, 1, 1, 10, 0, 0)
    assert filtered_df["Дата операции"].iloc[1] == datetime(2023, 1, 15, 12, 0, 0)
    assert filtered_df["Сумма"].iloc[0] == 100
    assert filtered_df["Сумма"].iloc[1] == 200


def test_sorted_pd_df_same_dates():
    """Тест: Проверка сортировки при одинаковых датах."""
    data = {
        "Дата операции": ["01.01.2023 10:00:00", "01.01.2023 12:00:00"],
        "Сумма": [100, 200],
    }
    pd_df = pd.DataFrame(data)

    analysis_date_str = "01.01.2023 23:59:59"

    filtered_df = sorted_pd_df(pd_df, analysis_date_str)

    assert isinstance(filtered_df, pd.DataFrame)
    assert len(filtered_df) == 2
    assert filtered_df["Дата операции"].iloc[0] == datetime(2023, 1, 1, 10, 0, 0)
    assert filtered_df["Дата операции"].iloc[1] == datetime(2023, 1, 1, 12, 0, 0)


def test_process_card_data_success(sample_df):
    """Тест: Успешное выполнение process_card_data."""
    date_time_str = "31.01.2023 23:59:59"
    result = process_card_data(sample_df, date_time_str)

    assert isinstance(result, list)
    assert len(result) == 1
    assert result[0]["last_digits"] == "3456"
    assert abs(result[0]["total_spent"]) == 150.0
    assert result[0]["cashback"] == 1.5
