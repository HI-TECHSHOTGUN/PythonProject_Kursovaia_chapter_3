import os
import pytest
from unittest.mock import patch, MagicMock
import pandas as pd
import requests

from src.reports import spending_by_weekday
from src.services import search_transaction
from src.utils import api_sp_500, valet_rub, open_excel_file_func

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



