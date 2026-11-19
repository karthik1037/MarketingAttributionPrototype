
import os
from pathlib import Path

import gspread
from dotenv import load_dotenv
from google.oauth2.service_account import Credentials

from database import get_connection

# Load environment variables from .env
BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets"
]


def get_worksheet():
    """Connect to the Google Sheets Touchpoints worksheet."""

    credentials_path = Path(
        os.environ["GOOGLE_CREDENTIALS_FILE"]
    ).expanduser()

    if not credentials_path.is_absolute():
        credentials_path = BASE_DIR / credentials_path

    credentials_path = credentials_path.resolve()

    credentials = Credentials.from_service_account_file(
        str(credentials_path),
        scopes=SCOPES
    )

    client = gspread.authorize(credentials)

    spreadsheet = client.open_by_key(
        os.environ["GOOGLE_SHEET_ID"]
    )

    return spreadsheet.worksheet("Touchpoints")


def sync_touchpoints():
    """Copy missing SQLite touchpoints to Google Sheets."""

    connection = get_connection()

    try:
        rows = connection.execute("""
            SELECT
                touchpoint_id,
                visitor_id,
                channel,
                visited_at
            FROM touchpoints
            ORDER BY touchpoint_id
        """).fetchall()
    finally:
        connection.close()

    worksheet = get_worksheet()

    # Read IDs already saved in Google Sheets
    existing_ids = {
        str(row[0])
        for row in worksheet.get_all_values()[1:]
        if row and row[0]
    }

    new_rows = []

    for row in rows:
        touchpoint_id = str(row[0])

        if touchpoint_id not in existing_ids:
            new_rows.append([
                touchpoint_id,
                str(row[1]),
                str(row[2]),
                str(row[3])
            ])

    if new_rows:
        worksheet.append_rows(
            new_rows,
            value_input_option="RAW"
        )

    return len(new_rows)


if __name__ == "__main__":
    count = sync_touchpoints()
    print(f"Successfully synced {count} touchpoints.")
