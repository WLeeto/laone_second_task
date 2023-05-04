from __future__ import print_function

from funcs import merge_stock
from gsheets_methods import GoogleSheetsApi


# Права для токена
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
# Id листа, с которым работаем
SAMPLE_SPREADSHEET_ID = ''


if __name__ == "__main__":
    # Создаем экземпляр класса для работы с таблицей
    gsheets = GoogleSheetsApi(SAMPLE_SPREADSHEET_ID=SAMPLE_SPREADSHEET_ID, SCOPES=SCOPES, token_path="token.json",
                              json_creds_path="creds.json")

    # Создаем список товаров, которые будем грузить в таблицу
    to_upload_dict = merge_stock("temp/assortment.json", "temp/stocks.json")

    # Заполняем прайс
    gsheets.add_price_list_records(price_dict=to_upload_dict)
