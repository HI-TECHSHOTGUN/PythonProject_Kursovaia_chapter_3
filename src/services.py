# from src.views import open_excel


def search_transaction(search_input, open_file_exc):
    """Функция поиска транзакций по запросу"""
    try:
        list_search = []
        if search_input == "":
            return "Строка пустая"
        else:
            for i in open_file_exc:
                if search_input.lower() in str(i["Категория"]).lower():
                    list_search.append(i)
                elif search_input.lower() in str(i["Описание"]).lower():
                    list_search.append(i)
            return list_search
    except Exception as e:
        return f"{e}"


# print(search_transaction('+', open_excel))
