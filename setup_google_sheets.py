"""Setup Google Sheets spreadsheet for ProjectSisdas search logs.

This script creates or opens a spreadsheet, ensures the worksheet exists,
sets the header row, and prints the spreadsheet ID for environment configuration.

Usage:
    python setup_google_sheets.py --credentials credentials.json

If the spreadsheet already exists, pass --spreadsheet-id to use it.
"""

import argparse
import json
import os
from pathlib import Path

import gspread
from google.oauth2.service_account import Credentials

SEARCH_LOG_FIELDS = [
    'timestamp', 'kebutuhan', 'budget_select', 'budget_manual',
    'budget_kategori', 'budget_min', 'budget_max', 'merk',
    'total_hasil', 'rule_ram_min', 'rule_gpu', 'rule_storage_min',
    'rule_catatan', 'hasil_detail'
]

DEFAULT_WORKSHEET_NAME = 'SearchLog'
DEFAULT_SPREADSHEET_TITLE = 'ProjectSisdas Search Log'
SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]


def load_credentials(credentials_path: Path) -> Credentials:
    # First try to load from environment variable
    env_credentials = os.getenv('GOOGLE_SHEETS_CREDENTIALS_JSON', '').strip()
    if env_credentials:
        try:
            return Credentials.from_service_account_info(
                json.loads(env_credentials),
                scopes=SCOPES
            )
        except json.JSONDecodeError:
            pass  # Fall back to file loading

    # Fall back to file loading
    if not credentials_path.exists():
        raise FileNotFoundError(f"File credentials tidak ditemukan: {credentials_path}")

    return Credentials.from_service_account_file(
        filename=str(credentials_path),
        scopes=SCOPES
    )

def get_spreadsheet(client: gspread.Client, spreadsheet_id: str, title: str):
    if spreadsheet_id:
        return client.open_by_key(spreadsheet_id)
    return client.create(title)


def ensure_worksheet(spreadsheet: gspread.Spreadsheet, worksheet_name: str):
    try:
        worksheet = spreadsheet.worksheet(worksheet_name)
    except gspread.WorksheetNotFound:
        worksheet = spreadsheet.add_worksheet(
            title=worksheet_name,
            rows='1000',
            cols=str(len(SEARCH_LOG_FIELDS))
        )

    header = worksheet.row_values(1)
    if header != SEARCH_LOG_FIELDS:
        worksheet.update('A1', [SEARCH_LOG_FIELDS])
    return worksheet


def parse_args():
    parser = argparse.ArgumentParser(
        description='Buat atau konfigurasi Google Sheets untuk log pencarian ProjectSisdas.'
    )
    parser.add_argument(
        '--credentials', '-c',
        required=True,
        help='Path ke service account credentials JSON'
    )
    parser.add_argument(
        '--spreadsheet-id', '-s',
        default='',
        help='Jika sudah ada spreadsheet, gunakan ID ini. Bila kosong, script akan membuat spreadsheet baru.'
    )
    parser.add_argument(
        '--spreadsheet-title', '-t',
        default=DEFAULT_SPREADSHEET_TITLE,
        help='Judul spreadsheet baru jika membuat spreadsheet baru.'
    )
    parser.add_argument(
        '--worksheet-name', '-w',
        default=DEFAULT_WORKSHEET_NAME,
        help='Nama worksheet untuk menyimpan log.'
    )
    return parser.parse_args()


def main():
    args = parse_args()
    credentials_path = Path(args.credentials)

    credentials = load_credentials(credentials_path)
    client = gspread.authorize(credentials)

    spreadsheet = get_spreadsheet(client, args.spreadsheet_id, args.spreadsheet_title)
    worksheet = ensure_worksheet(spreadsheet, args.worksheet_name)

    print('\nGoogle Sheets berhasil dikonfigurasi.')
    print(f'Spreadsheet title : {spreadsheet.title}')
    print(f'Spreadsheet ID    : {spreadsheet.id}')
    print(f'Worksheet name    : {worksheet.title}')
    print('\nGunakan nilai berikut di environment variables application:')
    print(f'  set GOOGLE_SHEETS_SPREADSHEET_ID={spreadsheet.id}')
    print(f'  set GOOGLE_SHEETS_WORKSHEET_NAME={worksheet.title}')
    print('\nUntuk credentials, Anda bisa menggunakan:')
    print('1. File path (saat ini):')
    print(f'   set GOOGLE_SHEETS_CREDENTIALS_JSON={credentials_path.resolve()}')
    print('2. JSON string langsung (lebih aman untuk production):')
    print('   set GOOGLE_SHEETS_CREDENTIALS_JSON=<isi file credentials.json sebagai string>')
    print('\nJika menggunakan Linux / macOS, ganti `set` dengan `export`.')


if __name__ == '__main__':
    main()
