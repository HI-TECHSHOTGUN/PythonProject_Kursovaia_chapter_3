import pytest
import pandas as pd


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





