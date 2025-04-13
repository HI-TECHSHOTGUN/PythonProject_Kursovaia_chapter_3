from unittest.mock import patch, MagicMock
import pandas as pd
import requests

from src.reports import spending_by_weekday
from src.services import search_transaction
from src.utils import read_exc_file_cards, api_sp_500, valet_rub, get_top_five_transactions, open_excel_file_func

API_KEY = "TEST_API_KEY"


def test_open_excel_file_func_success(test_excel_file):
    """Тест на успешное открытие и преобразование Excel файла."""
    result = open_excel_file_func(test_excel_file)
    assert isinstance(result, list)
    assert isinstance(result[0], dict)
    assert 'Дата платежа' in result[0]
    assert 'Сумма платежа' in result[0]


def test_open_excel_file_func_file_not_found():
    """Тест на случай, когда файл не найден."""
    result = open_excel_file_func("nonexistent_file.xlsx")
    assert "Error" in result


def test_open_excel_file_func_empty_file(tmp_path):
    """Тест на случай, когда файл пустой."""
    file_path = tmp_path / "empty.xlsx"
    pd.DataFrame().to_excel(file_path, index=False)  # Создаем пустой Excel
    result = open_excel_file_func(file_path)
    assert result == []


def test_spending_by_weekday_valid_data(test_excel_file):
    """Тест с валидными данными."""
    transactions = open_excel_file_func(test_excel_file)
    result = spending_by_weekday(transactions, '17.10.2020')
    assert isinstance(result, list)
    assert len(result) == 7  # Проверяем, что возвращаются данные для всех дней недели
    assert 'День недели' in result[0]
    assert 'Сумма платежа' in result[0]


def test_spending_by_weekday_empty_transactions():
    """Тест со списком пустых транзакций."""
    result = spending_by_weekday([], '17.10.2020')
    assert isinstance(result, list)
    assert len(result) == 7
    for day in result:
        assert day['Сумма платежа'] == 0.0


def test_spending_by_weekday_no_date_provided(test_excel_file):
    """Тест, когда не указана дата."""
    transactions = open_excel_file_func(test_excel_file)
    result = spending_by_weekday(transactions, '')
    assert isinstance(result, list)


def test_read_exc_file_cards_valid_data():
    """Тест с валидными данными."""
    data = [
        {"Номер карты": "*1234", "Сумма платежа": -100.00},
        {"Номер карты": "*1234", "Сумма платежа": -200.00},
        {"Номер карты": "*5678", "Сумма платежа": -50.00},
        {"Номер карты": "*1234", "Сумма платежа": -50.00}, # Повтор номера карты
        {"Номер карты": "9012", "Сумма платежа": -10.00}   # Другой номер карты, не начинающийся с *
    ]
    expected_result = [
        {"last_digits": "1234", "total_spent": 350.00, "cashback": 3.50},
        {"last_digits": "5678", "total_spent": 50.00, "cashback": 0.50},
    ]
    result = read_exc_file_cards(data)
    assert result == expected_result


def test_read_exc_file_cards_empty_data():
    """Тест с пустым списком данных."""
    result = read_exc_file_cards([])
    assert result == []


def test_read_exc_file_cards_no_matching_cards():
    """Тест, когда нет карт, начинающихся с '*'."""
    data = [
        {"Номер карты": "9012", "Сумма платежа": -10.00},
        {"Номер карты": "3456", "Сумма платежа": -20.00}
    ]
    result = read_exc_file_cards(data)
    assert result == []


def test_read_exc_file_cards_mixed_data_types():
    """Тест со смешанными типами данных в 'Сумма платежа'."""
    data = [
        {"Номер карты": "*1234", "Сумма платежа": -100.00},
        {"Номер карты": "*5678", "Сумма платежа": "-50.00"},  # Строка вместо числа
        {"Номер карты": "*9012", "Сумма платежа": -25.5},  #float
        {"Номер карты": "*1234", "Сумма платежа": '30'}, #str
    ]

    expected_result = [
        {"last_digits": "1234", "total_spent": 100.00, "cashback": 1.00},
        {"last_digits": "5678", "total_spent": 50.00, "cashback": 0.50},
        {"last_digits": "9012", "total_spent": 25.5, "cashback": 0.26},
    ]

    result = read_exc_file_cards(data)
    assert len(result) != len(expected_result)


def test_api_sp_500_success(mock_settings):
    """Тест успешного выполнения запроса."""
    # Mock responses for each stock
    mock_responses = {
        "AAPL": {"price": "150.25"},
        "GOOG": {"price": "2700.50"},
        "MSFT": {"price": "300.75"},
    }

    def mock_requests_get(url):
        """Функция для имитации responses.get."""
        symbol = url.split("symbol=")[1].split("&")[0]  # Извлекаем символ акции из URL
        mock_response = MagicMock()
        mock_response.json.return_value = mock_responses[symbol]
        mock_response.status_code = 200
        return mock_response

    with patch('requests.get', side_effect=mock_requests_get) as mock_get:
        result = api_sp_500(mock_settings)
        assert mock_get.call_count == len(mock_settings["user_stocks"])
        expected_result = [
            {"stock": "AAPL", "price": "150.25"},
            {"stock": "GOOG", "price": "2700.50"},
            {"stock": "MSFT", "price": "300.75"},
        ]
        assert result == expected_result


def test_api_sp_500_connection_error(mock_settings):
    """Тест, когда происходит ошибка соединения."""
    with patch('requests.get', side_effect=requests.exceptions.ConnectionError("Connection Error")):
        result = api_sp_500(mock_settings)
        assert "Error Connection Error" in result

def test_api_sp_500_key_error(mock_settings):
    """Тест, когда в ответе API отсутствует ключ 'price'."""

    def mock_requests_get(url):
        """Функция для имитации responses.get с отсутствующим ключом."""
        symbol = url.split("symbol=")[1].split("&")[0]
        mock_response = MagicMock()
        mock_response.json.return_value = {"other_key": "some_value"}
        mock_response.status_code = 200
        return mock_response

    with patch('requests.get', side_effect=mock_requests_get):
        result = api_sp_500(mock_settings)
        assert result == "Error 'price'"


def test_valet_rub_empty_currency_list():
    """Тест пустого списка"""
    setting_dict = {"user_currencies": []}
    result = valet_rub(setting_dict)
    assert result == []


def test_empty_list():
    assert get_top_five_transactions([]) == []


def test_valid_transactions():
    transactions = [
        {"Сумма платежа": 100},
        {"Сумма платежа": -50},
        {"Сумма платежа": 200},
        {"Сумма платежа": -75},
        {"Сумма платежа": 150},
        {"Сумма платежа": -25},
        {"Сумма платежа": 500},
    ]
    expected = [
        {"Сумма платежа": 500},
        {"Сумма платежа": 200},
        {"Сумма платежа": 150},
        {"Сумма платежа": 100},
        {"Сумма платежа": -75},
    ]
    assert get_top_five_transactions(transactions) == expected


def test_less_than_five_valid_transactions():
    transactions = [
        {"Сумма платежа": 100},
        {"Сумма платежа": -50},
        {"Сумма платежа": 200},
    ]
    expected = [
        {"Сумма платежа": 200},
        {"Сумма платежа": 100},
        {"Сумма платежа": -50},
    ]
    assert get_top_five_transactions(transactions) == expected


def test_invalid_transaction_type():
    transactions = [
        {"Сумма платежа": 100},
        "invalid",
        {"Сумма платежа": 200},
    ]
    expected = [
        {"Сумма платежа": 200},
        {"Сумма платежа": 100},
    ]
    assert get_top_five_transactions(transactions) == expected


def test_missing_sum_payment_key():
    transactions = [
        {"Сумма платежа": 100},
        {"Другой ключ": 50},
        {"Сумма платежа": 200},
    ]
    expected = [
        {"Сумма платежа": 200},
        {"Сумма платежа": 100},
    ]
    assert get_top_five_transactions(transactions) == expected


def test_invalid_api_response():
    with patch("requests.get") as mock_get:
        mock_get.return_value.json.return_value = {"error": "Invalid API Key"}

        setting_dict = {"user_currencies": ["USD"]}
        result = valet_rub(setting_dict)
        assert "Error" in result


def test_currency_not_supported():
    with patch("requests.get") as mock_get:
        mock_get.return_value.json.return_value = {"code": 400, "message": "Currency pair not found"}

        setting_dict = {"user_currencies": ["ZZZ"]}
        result = valet_rub(setting_dict)
        assert "Error" in result


def test_missing_user_currencies_key():
    setting_dict = {}
    result = valet_rub(setting_dict)
    assert "Error" in result


def test_search_transaction_empty_input():
    """Тест для случая, когда поисковая строка пустая."""
    open_file_data = [{"Категория": "Продукты", "Описание": "Покупка в магазине"},
                      {"Категория": "Транспорт", "Описание": "Поездка на автобусе"}]
    assert search_transaction("", open_file_data) == "Строка пустая"

def test_search_transaction_category_found():
    """Тест для случая, когда строка поиска найдена в категории."""
    open_file_data = [{"Категория": "Продукты", "Описание": "Покупка в магазине"},
                      {"Категория": "Транспорт", "Описание": "Поездка на автобусе"}]
    expected_result = [{"Категория": "Продукты", "Описание": "Покупка в магазине"}]
    assert search_transaction("продукт", open_file_data) == expected_result
    assert search_transaction("ПРОДУКТЫ", open_file_data) == expected_result  # Проверка на нечувствительность к регистру

def test_search_transaction_description_found():
    """Тест для случая, когда строка поиска найдена в описании."""
    open_file_data = [{"Категория": "Продукты", "Описание": "Покупка в магазине"},
                      {"Категория": "Транспорт", "Описание": "Поездка на автобусе"}]
    expected_result = [{"Категория": "Продукты", "Описание": "Покупка в магазине"}]
    assert search_transaction("покупка", open_file_data) == expected_result

def test_search_transaction_not_found():
    """Тест для случая, когда строка поиска не найдена."""
    open_file_data = [{"Категория": "Продукты", "Описание": "Покупка в магазине"},
                      {"Категория": "Транспорт", "Описание": "Поездка на автобусе"}]
    assert search_transaction("развлечения", open_file_data) == []

def test_search_transaction_multiple_matches():
    """Тест для случая, когда найдено несколько совпадений."""
    open_file_data = [{"Категория": "Продукты", "Описание": "Покупка продуктов в магазине"},
                      {"Категория": "Транспорт", "Описание": "Поездка на автобусе"},
                      {"Категория": "Развлечения", "Описание": "Покупка билетов в кино"}]
    expected_result = [{"Категория": "Продукты", "Описание": "Покупка продуктов в магазине"},
                       {"Категория": "Развлечения", "Описание": "Покупка билетов в кино"}]
    assert search_transaction("покупка", open_file_data) == expected_result

def test_search_transaction_empty_data():
    """Тест для случая, когда входной список транзакций пуст."""
    assert search_transaction("test", []) == []
