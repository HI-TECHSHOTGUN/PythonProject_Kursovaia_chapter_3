from src.views import open_excel
import pandas as pd
import datetime


def spending_by_weekday(transactions, date):
    """Функция для поиска трат по дням недели, входные данные date=DD.MM.YYYY"""
    try:
        days = {
            0: 'Понедельник',
            1: 'Вторник',
            2: 'Среда',
            3: 'Четверг',
            4: 'Пятница',
            5: 'Суббота',
            6: 'Воскресенье'
        }
        df = pd.DataFrame(transactions)
        if date == '':
            end_date = datetime.date.today()
        else:
            end_date = datetime.datetime.strptime(date, '%d.%m.%Y').date()

        start_date = end_date - datetime.timedelta(days=90)  # Приблизительно 3 месяца
        # Преобразование столбца 'Дата платежа' в datetime
        df['Дата платежа'] = pd.to_datetime(df['Дата платежа'], dayfirst=True)
        # Создаем DataFrame со всеми датами за последние три месяца
        date_range = pd.DataFrame({'Дата платежа': pd.date_range(start=start_date, end=end_date)})
        date_range['День недели'] = date_range['Дата платежа'].dt.weekday
        # Объединяем исходный DataFrame с DataFrame, содержащим все даты
        merged_df = pd.merge(date_range, df, on='Дата платежа', how='left')
        # Заменяем отсутствующие значения в столбце 'Сумма платежа' на 0
        merged_df['Сумма платежа'] = merged_df['Сумма платежа'].fillna(0)
        # Группируем по дню недели и вычисляем средние траты
        average_spending = merged_df.groupby('День недели')['Сумма платежа'].mean()
        # print(type(average_spending))
        average_spending = average_spending.rename(index=days)
        result = [{'День недели': day, 'Сумма платежа': spending} for day, spending in average_spending.items()]
        return result

    except Exception as e:
        return f'Error {e}'

print(spending_by_weekday(open_excel, '17.10.2020'))