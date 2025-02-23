# from src.views import open_excel


def search_transaction(search_input, open_file_exc):
    try:
        if search_input == '':
            return 'Строка пустая'
        else:
            for i in open_file_exc:
                if search_input.lower() in str(i['Категория']).lower():
                    print(i)
                elif search_input.lower() in str(i['Описание']).lower():
                    print(i)
            return 'Вот все что удалось найти'
    except Exception as e:
        return f'{e}'

# print(search_transaction('+', open_excel))