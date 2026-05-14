# 🎯 Sistem Pakar Rekomendasi Laptop - Web UI

UI berbasis web yang modern dan clean untuk Sistem Pakar Rekomendasi Laptop menggunakan metode **Forward Chaining**.

## ✨ Fitur

- 🎨 **Design Modern & Clean** - Antarmuka yang elegan dan user-friendly
- 📱 **Responsive Design** - Bekerja sempurna di desktop, tablet, dan mobile
- ⚡ **Real-time Search** - Pencarian rekomendasi laptop secara instan
- 📊 **Tabel Interaktif** - Menampilkan hasil dengan detail lengkap
- 📝 **Modal Detail** - Lihat spesifikasi lengkap setiap laptop
- 📋 **Transparansi Rule** - Menampilkan rule dan kriteria yang digunakan sistem
- 🔄 **Budget Fleksibel** - Pilih kategori budget atau input manual
- ✅ **Validasi Input** - Memastikan data valid sebelum mencari

## 🚀 Cara Menjalankan

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Jalankan Flask Server

```bash
python app.py
```

Output:
```
✔ Database dimuat: 40 laptop
✔ Flask server dimulai di http://localhost:5000
```

### 3. Mengaktifkan Google Sheets (Opsional)

Jika ingin mencatat pencarian secara online di Google Sheets, jalankan skrip setup berikut:

```bash
python setup_google_sheets.py --credentials credentials.json
```

Jika spreadsheet sudah ada, tambahkan `--spreadsheet-id`:

```bash
python setup_google_sheets.py --credentials credentials.json --spreadsheet-id YOUR_SHEET_ID
```

Skrip akan mencetak `SPREADSHEET_ID` dan perintah `set` untuk environment variables.

#### 3.2 Mengkonversi Credentials ke Environment Variable

Untuk keamanan, gunakan script helper untuk mengkonversi `credentials.json` menjadi string environment variable:

```bash
python convert_credentials.py credentials.json
```

Script akan mencetak command `set` yang bisa Anda copy-paste.

#### 3.3 Menggunakan Environment Variables

Copy `.env.example` menjadi `.env` dan isi dengan nilai yang sesuai:

```bash
cp .env.example .env
```

Isi file `.env` dengan:
- `GOOGLE_SHEETS_CREDENTIALS_JSON`: JSON string dari service account credentials
- `GOOGLE_SHEETS_SPREADSHEET_ID`: ID spreadsheet
- `GOOGLE_SHEETS_WORKSHEET_NAME`: Nama worksheet

Atau set environment variables secara manual:

```bash
set GOOGLE_SHEETS_SPREADSHEET_ID=YOUR_SHEET_ID
set GOOGLE_SHEETS_WORKSHEET_NAME=SearchLog
set GOOGLE_SHEETS_CREDENTIALS_JSON=<JSON string dari credentials.json>
```

Kemudian jalankan ulang server.

### 4. Buka Browser

Buka browser dan kunjungi: **http://localhost:5000**

## 📁 Struktur Project

```
ProjectSisdas/
├── app.py                      # Flask backend
├── sistem_pakar.py            # Core sistem pakar (knowledge base & inference)
├── data_laptop.csv            # Database laptop
├── requirements.txt           # Dependencies
├── templates/
│   └── index.html             # HTML template
└── static/
    ├── css/
    │   └── style.css          # CSS styling
    └── js/
        └── app.js             # JavaScript logic
```

## 🎯 Cara Menggunakan UI

1. **Pilih Kategori Kebutuhan**
   - Pelajar / Mahasiswa Umum
   - Profesional / Bisnis
   - Gaming
   - Desain Grafis / Konten Kreator
   - Pengembang / Programmer

2. **Pilih Budget**
   - Kategori: Ekonomis, Menengah, Tinggi, Premium
   - Atau input budget manual dalam Rupiah

3. **Klik "CARI"**
   - Sistem akan menjalankan Forward Chaining
   - Hasil ditampilkan dalam tabel

4. **Lihat Detail**
   - Klik tombol "Detail" untuk melihat spesifikasi lengkap laptop
   - Modal akan menampilkan informasi detail

5. **Lihat Rule Info**
   - Di panel kiri, informasi rule aktif ditampilkan
   - Menunjukkan kriteria minimum yang digunakan

## 🔧 Teknologi

### Backend
- **Python** - Bahasa pemrograman
- **Flask** - Web framework
- **CSV** - Database

### Frontend
- **HTML5** - Markup
- **CSS3** - Styling modern dengan gradient dan animation
- **JavaScript (Vanilla)** - Interaktivitas tanpa library eksternal

## 📊 API Endpoints

### GET `/`
Halaman utama (HTML)

### GET `/api/kategori`
Ambil daftar kategori kebutuhan dan budget
```json
{
  "kebutuhan": {...},
  "budget": {...}
}
```

### POST `/api/cari`
Jalankan forward chaining
```json
{
  "kebutuhan": "Pengembang / Programmer",
  "budget_select": "2",
  "budget_manual": ""
}
```

### GET `/api/detail/<id>`
Ambil detail laptop berdasarkan ID

## 💡 Informasi Rule

Sistem menampilkan informasi rule yang aktif setelah pencarian:

- **Kategori Kebutuhan** - Pilihan pengguna
- **Kategori Budget** - Range harga yang dipilih
- **RAM Minimum** - Kriteria minimum RAM
- **GPU Syarat** - Tipe GPU yang diperlukan
- **Storage Minimum** - Kapasitas storage minimal
- **Catatan** - Penjelasan dan rekomendasi rule

## 🎨 Desain UI

### Warna Tema
- **Primary**: #3b82f6 (Blue)
- **Secondary**: #1f2937 (Dark Gray)
- **Success**: #10b981 (Green)
- **Warning**: #f59e0b (Amber)
- **Background**: Linear gradient light gray

### Font
- Menggunakan system font yang tersedia di semua browser
- Font size responsif sesuai ukuran layar

### Layout
- **Left Panel**: Form input dengan width tetap (380px)
- **Right Panel**: Hasil rekomendasi dengan width fleksibel
- **Mobile**: Layout berubah menjadi single column di bawah 768px

## 📱 Responsive Design

- **Desktop** (1200px+): 2 kolom (form & results)
- **Tablet** (768px-1024px): 2 kolom dengan ukuran penyesuaian
- **Mobile** (<768px): 1 kolom (form di atas, results di bawah)

## ⚠️ Error Handling

Aplikasi menangani berbagai kondisi error:

- Input validasi (kebutuhan dan budget wajib dipilih)
- Database tidak ditemukan
- Hasil kosong (tidak ada laptop yang cocok)
- Server error

## 🔒 Keamanan

- Input validation di frontend dan backend
- JSON response dengan error handling
- CORS-ready untuk integrasi dengan service lain

## 📝 Catatan

- Database laptop dimuat saat server startup
- Semua kalkulasi dilakukan di backend (sistem_pakar.py)
- Frontend hanya menampilkan data dan handle interaksi user

## 🤝 Kontribusi

Untuk menambahkan fitur atau perbaikan, silakan modifikasi:
- Backend logic di `app.py` dan `sistem_pakar.py`
- UI di `templates/index.html`
- Style di `static/css/style.css`
- Interaktivitas di `static/js/app.js`

## 📄 Lisensi

Proyek akademik - Sistem Cerdas (PBL)

---

**Dibuat dengan ❤️ untuk Sistem Pakar Rekomendasi Laptop**
