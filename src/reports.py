import datetime

import pandas as pd

# from src.views import open_excel


def spending_by_weekday(transactions, date):
    """Функция для поиска трат по дням недели, входные данные date=DD.MM.YYYY"""
    try:
        days = {0: "Понедельник", 1: "Вторник", 2: "Среда", 3: "Четверг", 4: "Пятница", 5: "Суббота", 6: "Воскресенье"}
        df = pd.DataFrame(transactions)
        if not transactions:  # Проверяем, что список транзакций не пуст
            return [{'День недели': days[i], 'Сумма платежа': 0.0} for i in range(7)]
        if date == "":
            end_date = datetime.date.today()
        else:
            end_date = datetime.datetime.strptime(date, "%d.%m.%Y").date()
        start_date = end_date - datetime.timedelta(days=90)  # Приблизительно 3 месяца
        df["Дата платежа"] = pd.to_datetime(df["Дата платежа"], dayfirst=True, errors="coerce")
        df = df.dropna(subset=["Дата платежа"])
        date_range = pd.DataFrame({"Дата платежа": pd.date_range(start=start_date, end=end_date)})
        date_range["День недели"] = date_range["Дата платежа"].dt.weekday
        merged_df = pd.merge(date_range, df, on="Дата платежа", how="left")
        merged_df["Сумма платежа"] = merged_df["Сумма платежа"].fillna(0)
        average_spending = merged_df.groupby("День недели")["Сумма платежа"].mean()
        average_spending = average_spending.rename(index=days)
        result = [{"День недели": day, "Сумма платежа": spending} for day, spending in average_spending.items()]
        return result
    except Exception as e:
        return f"Error {e}"


# print(spending_by_weekday(open_excel, '17.10.2020'))
