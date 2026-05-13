"""Helper script untuk mengkonversi credentials.json menjadi environment variable string.

Usage:
    python convert_credentials.py credentials.json
"""

import json
import sys
from pathlib import Path


def main():
    if len(sys.argv) != 2:
        print("Usage: python convert_credentials.py <credentials.json>")
        sys.exit(1)

    credentials_path = Path(sys.argv[1])

    if not credentials_path.exists():
        print(f"Error: File {credentials_path} tidak ditemukan")
        sys.exit(1)

    try:
        with open(credentials_path, 'r', encoding='utf-8') as f:
            credentials_data = json.load(f)

        # Convert to JSON string
        json_string = json.dumps(credentials_data, separators=(',', ':'))

        print("Copy paste baris berikut ke environment variable GOOGLE_SHEETS_CREDENTIALS_JSON:")
        print()
        print(f"set GOOGLE_SHEETS_CREDENTIALS_JSON={json_string}")
        print()
        print("Atau untuk Linux/macOS:")
        print(f"export GOOGLE_SHEETS_CREDENTIALS_JSON='{json_string}'")

    except json.JSONDecodeError as e:
        print(f"Error: File credentials.json tidak valid: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()