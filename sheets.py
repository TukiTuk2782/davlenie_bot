from pathlib import Path

import gspread
from google.oauth2.service_account import Credentials


def append_to_sheet(data: list, spreadsheet_id: str, service_account_file: str | Path):
    scopes = ["https://www.googleapis.com/auth/spreadsheets"]
    creds = Credentials.from_service_account_file(str(service_account_file), scopes=scopes)
    client = gspread.authorize(creds)
    sheet = client.open_by_key(spreadsheet_id).sheet1
    sheet.append_row(data)
