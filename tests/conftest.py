from unittest import mock

import pytest
import pandas as pd
import requests


@pytest.fixture
def test_excel_file(tmp_path):
    """Создает временный Excel файл для тестирования."""
    data = {'Дата платежа': ['16.10.2020', '17.10.2020', '18.10.2020', '19.10.2020', '20.10.2020', 'invalid_date'],
            'Сумма платежа': [100, 200, 150, 250, 120, 50]}  # Добавлена invalid_date
    df = pd.DataFrame(data)
    file_path = tmp_path / "test.xlsx"
    df.to_excel(file_path, index=False)
    return file_path


@pytest.fixture
def mock_settings():
    """Фикстура для предоставления настроек со списком акций."""
    return {"user_stocks": ["AAPL", "GOOG", "MSFT"]}


@pytest.fixture
def mock_requests_get():
    """Мокирует requests.get для тестирования."""
    class MockResponse:
        def __init__(self, json_data):
            self.json_data = json_data

        def json(self):
            return self.json_data

    mocked_response = MockResponse({"price": "199.200000"})

    yield mocked_response


@pytest.fixture
def mock_requests_get_rub():
    """Мокирует requests.get для тестирования."""
    def mock_response():
        return {"rate": "75"}

    yield mock_response


@pytest.fixture
def mock_excel_data():
    """Создает фиктивные данные Excel в формате строки для мокирования."""
    excel_string = """
    Name,Age,City
    Alice,30,New York
    Bob,25,London
    Charlie,40,Paris
    """
    return excel_string


@pytest.fixture
def sample_df():
    """Создает пример DataFrame для тестов."""
    data = {
        "Дата операции": ["01.01.2023 10:00:00", "15.01.2023 12:00:00", "01.02.2023 08:00:00", "10.01.2023 14:00:00"],
        "Номер карты": ["1234567890123456", "1234567890123456", "9876543210987654", "1234567890123456"],
        "Сумма операции": ["-100", "200", "-300", "-50"]
    }
    return pd.DataFrame(data)
