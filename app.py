"""
SISTEM PAKAR REKOMENDASI LAPTOP - WEB UI (FLASK)
Modern & Clean Web Interface
"""

from flask import Flask, render_template, request, jsonify
import csv
import json
import os
import sys
from datetime import datetime

try:
    import gspread
    from google.oauth2.service_account import Credentials
except ImportError:
    gspread = None
    Credentials = None

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from sistem_pakar import (
    load_database, forward_chaining, KATEGORI_KEBUTUHAN, 
    KATEGORI_BUDGET
)

# ══════════════════════════════════════════════════════════════════
#  KONFIGURASI FLASK
# ══════════════════════════════════════════════════════════════════

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, "data_laptop.csv")
SEARCH_LOG_FILE = os.path.join(BASE_DIR, "search_log.csv")
SEARCH_LOG_FIELDS = [
    'timestamp', 'kebutuhan', 'budget_select', 'budget_manual',
    'budget_kategori', 'budget_min', 'budget_max', 'merk',
    'total_hasil', 'rule_ram_min', 'rule_gpu', 'rule_storage_min',
    'rule_catatan', 'hasil_detail'
]

GOOGLE_SHEETS_CREDENTIALS_JSON = os.getenv('GOOGLE_SHEETS_CREDENTIALS_JSON', '').strip()
GOOGLE_SHEETS_SPREADSHEET_ID = os.getenv('GOOGLE_SHEETS_SPREADSHEET_ID', '').strip()
GOOGLE_SHEETS_WORKSHEET_NAME = os.getenv('GOOGLE_SHEETS_WORKSHEET_NAME', 'SearchLog').strip()

google_sheets_client = None
google_sheets_worksheet = None
google_sheets_ready = False


def init_google_sheets():
    global google_sheets_client, google_sheets_worksheet, google_sheets_ready

    if not GOOGLE_SHEETS_CREDENTIALS_JSON or not GOOGLE_SHEETS_SPREADSHEET_ID:
        return

    if gspread is None or Credentials is None:
        print("[WARNING] Google Sheets integration tidak tersedia. Install 'gspread' dan 'google-auth'.")
        return

    try:
        # Try to load credentials from JSON string first, then from file path
        try:
            creds = Credentials.from_service_account_info(
                json.loads(GOOGLE_SHEETS_CREDENTIALS_JSON),
                scopes=[
                    'https://www.googleapis.com/auth/spreadsheets',
                    'https://www.googleapis.com/auth/drive'
                ]
            )
        except json.JSONDecodeError:
            # If not JSON, treat as file path
            creds = Credentials.from_service_account_file(
                GOOGLE_SHEETS_CREDENTIALS_JSON,
                scopes=[
                    'https://www.googleapis.com/auth/spreadsheets',
                    'https://www.googleapis.com/auth/drive'
                ]
            )

        google_sheets_client = gspread.authorize(creds)
        spreadsheet = google_sheets_client.open_by_key(GOOGLE_SHEETS_SPREADSHEET_ID)

        try:
            google_sheets_worksheet = spreadsheet.worksheet(GOOGLE_SHEETS_WORKSHEET_NAME)
        except gspread.WorksheetNotFound:
            google_sheets_worksheet = spreadsheet.add_worksheet(
                title=GOOGLE_SHEETS_WORKSHEET_NAME,
                rows="1000",
                cols=str(len(SEARCH_LOG_FIELDS) + 1)
            )

        header = google_sheets_worksheet.row_values(1)
        if header != SEARCH_LOG_FIELDS:
            google_sheets_worksheet.insert_row(SEARCH_LOG_FIELDS, index=1)

        google_sheets_ready = True
        print("[INFO] Google Sheets integration berhasil diinisialisasi.")
    except Exception as e:
        print(f"[WARNING] Gagal inisialisasi Google Sheets: {e}")


def ensure_search_log_exist():
    if not os.path.exists(SEARCH_LOG_FILE):
        with open(SEARCH_LOG_FILE, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=SEARCH_LOG_FIELDS)
            writer.writeheader()


def log_search(
    kebutuhan: str,
    budget_select: str,
    budget_manual: str,
    merk_pilihan: str,
    nama_budget: str,
    budget_min: int,
    budget_max: int,
    hasil: list[dict],
    rule: dict,
    catatan: str
):
    hasil_detail = [
        {
            'no': lap['no'],
            'merk': lap['merk'],
            'model': lap['model'],
            'cpu': lap['cpu'],
            'gpu': lap['gpu'],
            'ram': lap['ram_raw'],
            'storage': lap['storage_raw'],
            'harga': lap['harga_raw']
        }
        for lap in hasil
    ]
    row = {
        'timestamp': datetime.utcnow().isoformat() + 'Z',
        'kebutuhan': kebutuhan,
        'budget_select': budget_select,
        'budget_manual': budget_manual,
        'budget_kategori': nama_budget,
        'budget_min': budget_min,
        'budget_max': budget_max,
        'merk': merk_pilihan,
        'total_hasil': len(hasil),
        'rule_ram_min': rule.get('ram_min', ''),
        'rule_gpu': rule.get('gpu', ''),
        'rule_storage_min': rule.get('storage_min', ''),
        'rule_catatan': catatan,
        'hasil_detail': json.dumps(hasil_detail, ensure_ascii=False)
    }

    if google_sheets_ready and google_sheets_worksheet is not None:
        try:
            google_sheets_worksheet.append_row(
                [row[field] for field in SEARCH_LOG_FIELDS],
                value_input_option='RAW'
            )
        except Exception as e:
            print(f"[WARNING] Gagal menulis log ke Google Sheets: {e}")

    try:
        with open(SEARCH_LOG_FILE, 'a', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=SEARCH_LOG_FIELDS)
            writer.writerow(row)
    except OSError as e:
        print(f"[WARNING] Gagal menulis log pencarian: {e}")

# ══════════════════════════════════════════════════════════
#  KONFIGURASI FLASK
# ══════════════════════════════════════════════════════════

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, "data_laptop.csv")

# Load database global
try:
    LAPTOPS = load_database(DATA_FILE)
    ensure_search_log_exist()
    init_google_sheets()
except Exception as e:
    print(f"[ERROR] Gagal memuat database: {e}")
    sys.exit(1)


# ══════════════════════════════════════════════════════════
#  ROUTES
# ══════════════════════════════════════════════════════════

@app.route('/')
def index():
    """Halaman utama."""
    return render_template('index.html')


@app.route('/api/kategori')
def api_kategori():
    """API: Ambil daftar kategori kebutuhan dan budget."""
    merks = sorted(list(set(lap['merk'] for lap in LAPTOPS)))
    return jsonify({
        'kebutuhan': KATEGORI_KEBUTUHAN,
        'budget': {
            k: {
                'nama': v[0],
                'min': v[1],
                'max': v[2],
                'label': f"{v[0]} (Rp {v[1]:,} - Rp {v[2]:,})".replace(",", ".")
            }
            for k, v in KATEGORI_BUDGET.items()
        },
        'merks': merks
    })


@app.route('/api/cari', methods=['POST'])
def api_cari():
    """API: Jalankan forward chaining dan kembalikan hasil."""
    data = request.get_json()
    
    kebutuhan = data.get('kebutuhan', '').strip()
    budget_select = data.get('budget_select', '').strip()
    budget_manual = data.get('budget_manual', '').strip()
    merk_pilihan = data.get('merk', 'Semua').strip()
    
    # Validasi
    if not kebutuhan or kebutuhan == '':
        return jsonify({'success': False, 'message': 'Pilih kategori kebutuhan!'}), 400
    
    # Tentukan budget
    budget_min = 0
    budget_max = 0
    nama_budget = None
    
    if budget_manual:
        clean = budget_manual.replace(".", "").replace(",", "").replace(" ", "")
        try:
            budget_max = int(clean)
            if budget_max <= 0:
                raise ValueError
            # Cari kategori
            for idx, (nama, bmin, bmax) in KATEGORI_BUDGET.items():
                if budget_max <= bmax:
                    nama_budget = nama
                    budget_min = bmin
                    budget_max = min(budget_max, bmax)
                    break
            if not nama_budget:
                nama_budget = "Premium"
                budget_min = 25_000_000
        except ValueError:
            return jsonify({'success': False, 'message': 'Budget manual harus angka positif!'}), 400
    else:
        if not budget_select or budget_select == '':
            return jsonify({'success': False, 'message': 'Pilih kategori budget atau input manual!'}), 400
        
        # Cari kategori
        for k, v in KATEGORI_BUDGET.items():
            if k == budget_select:
                nama_budget = v[0]
                budget_min = v[1]
                budget_max = v[2]
                break
        
        if not nama_budget:
            return jsonify({'success': False, 'message': 'Budget tidak ditemukan!'}), 400
    
    # Jalankan forward chaining
    try:
        hasil, rule, catatan = forward_chaining(
            LAPTOPS, kebutuhan, nama_budget, budget_min, budget_max, merk_pilihan
        )
        
        # Format hasil
        hasil_format = []
        for i, lap in enumerate(hasil, 1):
            hasil_format.append({
                'no': i,
                'id': lap['no'],
                'merk': lap['merk'],
                'model': lap['model'],
                'cpu': lap['cpu'],
                'gpu': lap['gpu'],
                'ram': lap['ram_raw'],
                'ram_gb': lap['ram'],
                'storage': lap['storage_raw'],
                'storage_gb': lap['storage'],
                'harga': lap['harga_raw'],
                'harga_value': lap['harga'],
            })
        
        log_search(
            kebutuhan=kebutuhan,
            budget_select=budget_select,
            budget_manual=budget_manual,
            merk_pilihan=merk_pilihan,
            nama_budget=nama_budget,
            budget_min=budget_min,
            budget_max=budget_max,
            hasil=hasil,
            rule=rule,
            catatan=catatan
        )
        
        return jsonify({
            'success': True,
            'kebutuhan': kebutuhan,
            'budget': nama_budget,
            'budget_min': budget_min,
            'budget_max': budget_max,
            'merk': merk_pilihan,
            'rule': rule,
            'hasil': hasil_format,
            'total': len(hasil),
            'message': f"Ditemukan {len(hasil)} laptop yang sesuai"
        })
    
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500


@app.route('/api/detail/<int:laptop_id>')
def api_detail(laptop_id):
    """API: Ambil detail laptop berdasarkan ID."""
    for lap in LAPTOPS:
        if lap['no'] == laptop_id:
            return jsonify({
                'success': True,
                'data': {
                    'no': lap['no'],
                    'merk': lap['merk'],
                    'model': lap['model'],
                    'cpu': lap['cpu'],
                    'gpu': lap['gpu'],
                    'ram': lap['ram_raw'],
                    'storage': lap['storage_raw'],
                    'harga': lap['harga_raw'],
                    'harga_value': lap['harga'],
                }
            })
    
    return jsonify({'success': False, 'message': 'Laptop tidak ditemukan'}), 404


# ══════════════════════════════════════════════════════════
#  ERROR HANDLERS
# ══════════════════════════════════════════════════════════

@app.errorhandler(404)
def not_found(e):
    return jsonify({'success': False, 'message': 'Not found'}), 404


@app.errorhandler(500)
def server_error(e):
    return jsonify({'success': False, 'message': 'Server error'}), 500


# ══════════════════════════════════════════════════════════
#  MAIN
# ══════════════════════════════════════════════════════════

if __name__ == '__main__':
    # Production: gunakan gunicorn
    # Development: gunakan flask debug
    import os
    debug = os.getenv('FLASK_ENV') == 'development'
    port = int(os.getenv('PORT', 5000))
    app.run(debug=debug, host='0.0.0.0', port=port)
