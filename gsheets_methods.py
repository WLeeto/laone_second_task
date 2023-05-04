import os.path
from pprint import pprint

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload


def change_height(sheet_id: int, start_index: int, end_index: int, height: int) -> dict:
    """
    Return dict to change height.
    """
    request = {
        'updateDimensionProperties': {
            'range': {
                'sheetId': sheet_id,
                'dimension': 'ROWS',
                'startIndex': start_index,  # начальный индекс столбца
                'endIndex': end_index  # конечный индекс столбца
            },
            "properties": {
                "pixelSize": height
            },
            "fields": "pixelSize"
        }
    }
    return request


def change_width(sheet_id: int, start_index: int, end_index: int, width: int) -> dict:
    """
    Return dict to change width.
    """
    request = {
        'updateDimensionProperties': {
            'range': {
                'sheetId': sheet_id,
                'dimension': 'COLUMNS',
                'startIndex': start_index,  # начальный индекс столбца
                'endIndex': end_index  # конечный индекс столбца
            },
            "properties": {
                "pixelSize": width
            },
            "fields": "pixelSize"
        }
    }
    return request


def create_spoiler(sheet_id: int, start_index: int, end_index: int) -> dict:
    """
    Create dict to create spoilers.
    """
    request = {
        "addDimensionGroup": {
            "range": {
                "sheetId": sheet_id,
                "dimension": "ROWS",
                "startIndex": start_index,
                "endIndex": end_index
            },
        }
    }
    return request


class GoogleSheetsApi:
    """
    To fast api with google.
    """
    def __init__(self, SAMPLE_SPREADSHEET_ID: str, SCOPES: str, token_path: str, json_creds_path: str):
        self.spreadsheetid = SAMPLE_SPREADSHEET_ID
        self.scopes = SCOPES
        self.token_path = token_path
        self.json_creds_path = json_creds_path

        creds = None
        if os.path.exists(self.token_path):
            creds = Credentials.from_authorized_user_file(self.token_path, self.scopes)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.json_creds_path, SCOPES)
                creds = flow.run_local_server(port=0)
            with open(self.token_path, 'w') as token:
                token.write(creds.to_json())

        try:
            service = build('sheets', 'v4', credentials=creds)
            self.servise = service
        except HttpError as err:
            print(err)

        self.sheet = self.servise.spreadsheets()

    def read(self, sheet_name: str, cell_range: str) -> list:
        result = self.sheet.values().get(spreadsheetId=self.spreadsheetid, range=f"{sheet_name}!{cell_range}").execute()
        return result.get('values', [])

    def add_list(self, list_names: list) -> dict:
        requests = []
        for i in list_names:
            requests.append({
                "addSheet": {
                    "properties": {
                        "title": i
                    }
                }
            })
        body = {
            "requests": requests
        }
        resp = self.sheet.batchUpdate(spreadsheetId=SAMPLE_SPREADSHEET_ID, body=body).execute()
        return resp

        # Вариант для проверки запроса
        # try:
        #     resp = self.sheet.batchUpdate(spreadsheetId=SAMPLE_SPREADSHEET_ID, body=body).execute()
        #     return resp
        # except HttpError as ex:
        #     print(ex)

    def add_record(self, records: list, sheet_name: str, cell_range: str) -> dict:
        result = self.sheet.values().update(spreadsheetId=self.spreadsheetid, range=f"{sheet_name}!{cell_range}",
                                            valueInputOption="USER_ENTERED",
                                            body={"values": records}).execute()
        return result

    def add_price_list_records(self, price_dict: dict) -> None:
        """
        Create price list records according with "merge_stock" dict
        :param price_dict: "merge_stock" dict
        :return:
        """
        sheet_names = list(price_dict.keys())
        records = []
        header = ["Наименование",
                  "Изображение",
                  "Цена: Розница",
                  "Цена: от 5 т.р.",
                  "Цена: от 15 т.р.",
                  "Цена: от 100 т.р."]
        for i in sheet_names:
            create_list = self.add_list([i])
            list_id = create_list['replies'][0]['addSheet']['properties']['sheetId']
            print(f"Создан лист {i} c id {list_id}")
            # Для всего стока без распределения
            if i != "Расходные материалы" and not i.startswith("Ресницы"):
                cell_range = f"A1:F{len(price_dict[i]) + 1}"
                records.append(header)
                for record in price_dict[i]:
                    records.append([
                        record["Наименование"],
                        f'=IMAGE("{record["Изображение"]}")',
                        record["Розница"],
                        record["от 5 т.р."],
                        record["от 15 т.р."],
                        record["от 100 т.р."],
                    ])

                result = self.sheet.values().update(spreadsheetId=self.spreadsheetid, range=f"{i}!{cell_range}",
                                                    valueInputOption="USER_ENTERED",
                                                    body={"values": records}).execute()

                pprint(f"Лист {i} заполнен. Колличество записей {len(records)}")
                records.clear()

                body = {"requests": []}
                req1 = change_width(sheet_id=list_id, start_index=0, end_index=1, width=100)
                body["requests"].append(req1)

                req2 = change_width(sheet_id=list_id, start_index=1, end_index=2, width=200)
                body["requests"].append(req2)

                req3 = change_height(sheet_id=list_id, start_index=1, end_index=len(price_dict[i]) + 1, height=200)
                body["requests"].append(req3)

                self.sheet.batchUpdate(spreadsheetId=SAMPLE_SPREADSHEET_ID, body=body).execute()

            # Для ресниц распределение по брендам
            elif i.startswith("Ресницы"):
                cell_range = f"A1:F{len(price_dict[i]) + 1}"
                records.append(header)
                for record in price_dict[i]:
                    records.append([
                        record["Наименование"],
                        f'=IMAGE("{record["Изображение"]}")',
                        record["Розница"],
                        record["от 5 т.р."],
                        record["от 15 т.р."],
                        record["от 100 т.р."],
                    ])
                result = self.sheet.values().update(spreadsheetId=self.spreadsheetid, range=f"{i}!{cell_range}",
                                                    valueInputOption="USER_ENTERED",
                                                    body={"values": records}).execute()
                pprint(f"Лист {i} заполнен. Колличество записей {len(records)}")
                records.clear()

                body = {"requests": []}
                req1 = change_width(sheet_id=list_id, start_index=0, end_index=1, width=100)
                body["requests"].append(req1)

                req2 = change_width(sheet_id=list_id, start_index=1, end_index=2, width=200)
                body["requests"].append(req2)

                req3 = change_height(sheet_id=list_id, start_index=1, end_index=len(price_dict[i]) + 1, height=200)
                body["requests"].append(req3)

                self.sheet.batchUpdate(spreadsheetId=SAMPLE_SPREADSHEET_ID, body=body).execute()

            # Для расходных материалов с группами
            elif i == "Расходные материалы":
                count = 1
                spoiler_list = []
                spoiler_item = []
                item_keys = price_dict[i].keys()
                end_row = len(list(price_dict[i].values()))
                for l in item_keys:
                    end_row += len(price_dict[i][l])
                cell_range = f"A1:F{end_row + 1}"
                records.append(header)

                for item in item_keys:
                    records.append([f"{item}", "", "", "", "", ""])
                    count += 1
                    spoiler_item.append(count)
                    for j in price_dict[i][item]:
                        records.append([
                            j["Наименование"],
                            f'=IMAGE("{j["Изображение"]}")',
                            j["Розница"],
                            j["от 5 т.р."],
                            j["от 15 т.р."],
                            j["от 100 т.р."],
                        ])
                        count += 1
                    spoiler_item.append(count)
                    spoiler_list.append(spoiler_item)
                    spoiler_item = []

                result = self.sheet.values().update(spreadsheetId=self.spreadsheetid, range=f"{i}!{cell_range}",
                                                    valueInputOption="USER_ENTERED",
                                                    body={"values": records}).execute()
                pprint(f"Лист {i} заполнен. Колличество записей {len(records)}")
                records.clear()

                spoiler_body = {"requests": []}
                for s in spoiler_list:
                    spoiler_body["requests"].append(create_spoiler(sheet_id=list_id, start_index=s[0], end_index=s[1]))
                self.sheet.batchUpdate(spreadsheetId=SAMPLE_SPREADSHEET_ID, body=spoiler_body).execute()

                body = {"requests": []}
                req1 = change_width(sheet_id=list_id, start_index=0, end_index=1, width=100)
                body["requests"].append(req1)

                req2 = change_width(sheet_id=list_id, start_index=1, end_index=2, width=200)
                body["requests"].append(req2)

                req3 = change_height(sheet_id=list_id, start_index=1, end_index=end_row + 1, height=200)
                body["requests"].append(req3)

                self.sheet.batchUpdate(spreadsheetId=SAMPLE_SPREADSHEET_ID, body=body).execute()