"""
SISTEM PAKAR REKOMENDASI LAPTOP - WEB UI (FLASK)
Modern & Clean Web Interface
"""

from flask import Flask, render_template, request, jsonify
import os
import sys
from sistem_pakar import (
    load_database, forward_chaining, KATEGORI_KEBUTUHAN, 
    KATEGORI_BUDGET
)

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
        
        return jsonify({
            'success': True,
            'kebutuhan': kebutuhan,
            'budget': nama_budget,
            'budget_min': budget_min,
            'budget_max': budget_max,
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
