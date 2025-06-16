import os
from functools import wraps

import pandas as pd
import datetime


ABS_PATH = os.path.abspath(os.path.join(os.getcwd(), '..'))
all_transactions_df = pd.read_excel(os.path.join(ABS_PATH, 'data', 'operations.xlsx'))


def report_decorator(func):
    """Декоратор для функций-отчетов."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
            if isinstance(result, str):
                return result

            filename = kwargs.get('filename', f"report_{datetime.date.today().strftime('%Y-%m-%d')}.txt")
            with open(filename, "w", encoding="utf-8") as f:
                f.write(result.to_string())
            print(f"Результат записан в файл: {filename}")
            return result
        except Exception as e:
            return f"Error: {e}"
    return wrapper


@report_decorator
def spending_by_weekday(df, date=None):
    """Функция для поиска трат по дням недели."""
    try:
        days = {0: "Понедельник", 1: "Вторник", 2: "Среда", 3: "Четверг", 4: "Пятница", 5: "Суббота", 6: "Воскресенье"}
        if df.empty:
            return pd.DataFrame({
                'День недели': days.values(),
                'Сумма платежа': [0.0] * 7
            })

        if date == "":
            end_date = datetime.date.today()
        else:
            try:
                end_date = datetime.datetime.strptime(date, "%d.%m.%Y").date()
            except ValueError:
                return "Error: Invalid date format. Please use DD.MM.YYYY."

        start_date = end_date - datetime.timedelta(days=90)
        df["Дата платежа"] = pd.to_datetime(df["Дата платежа"], dayfirst=True, errors="coerce")
        df = df.dropna(subset=["Дата платежа"])
        date_range = pd.DataFrame({"Дата платежа": pd.date_range(start=start_date, end=end_date)})
        date_range["День недели"] = date_range["Дата платежа"].dt.weekday
        merged_df = pd.merge(date_range, df, on="Дата платежа", how="left")
        merged_df["Сумма платежа"] = merged_df["Сумма платежа"].fillna(0)
        merged_df["Сумма платежа"] = merged_df["Сумма платежа"].abs()

        average_spending = merged_df.groupby("День недели")["Сумма платежа"].mean().rename(index=days)
        result = average_spending.to_frame()
        return result
    except Exception as e:
        return f"Error: {e}"


page_result = spending_by_weekday(all_transactions_df, '31.12.2020')
print(page_result)

