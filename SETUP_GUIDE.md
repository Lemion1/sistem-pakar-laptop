# Setup Guide - ProjectSisdas Google Sheets Integration

## ✅ Status Setup

Integrasi Google Sheets **sudah selesai dikonfigurasi** dengan aman. Berikut adalah langkah-langkah untuk menjalankannya:

---

## 📋 Langkah 1: Verifikasi File-File

Pastikan file berikut sudah ada di project root:

- ✅ `.env` - Berisi credentials JSON dan konfigurasi Google Sheets
- ✅ `app.py` - Backend Flask dengan Google Sheets integration
- ✅ `setup_google_sheets.py` - Script setup spreadsheet
- ✅ `convert_credentials.py` - Helper untuk konversi credentials
- ✅ `requirements.txt` - Berisi dependencies `gspread` dan `google-auth`

---

## 📌 Langkah 2: Dapatkan Spreadsheet ID

### Opsi A: Otomatis (jika Google Drive quota masih ada)

Jalankan script setup untuk membuat spreadsheet baru:

```bash
python setup_google_sheets.py --credentials credentials.json
```

Script akan:
1. Membuat spreadsheet baru bernama "ProjectSisdas Search Log"
2. Membuat worksheet "SearchLog" dengan header columns
3. **Mencetak Spreadsheet ID**

Contoh output:
```
Google Sheets berhasil dikonfigurasi.
Spreadsheet title : ProjectSisdas Search Log
Spreadsheet ID    : 1abc123def456ghi789jkl
Worksheet name    : SearchLog
```

Salin `Spreadsheet ID` → update `.env`

### Opsi B: Manual (jika quota habis atau sudah punya spreadsheet)

1. Buka [Google Sheets](https://sheets.google.com)
2. Buat spreadsheet baru
3. Beri nama: "ProjectSisdas Search Log" (opsional)
4. Di URL: `https://docs.google.com/spreadsheets/d/YOUR_SPREADSHEET_ID/edit`
5. Salin `YOUR_SPREADSHEET_ID`

**Bagikan spreadsheet** dengan service account email:
- Email: `spreadsheet-bot@linen-totality-484904-u5.iam.gserviceaccount.com`
- Akses: **Editor**

Update `.env`:
```bash
GOOGLE_SHEETS_SPREADSHEET_ID=YOUR_SPREADSHEET_ID
```

---

## 🔧 Langkah 3: Setup Environment Variables

File `.env` sudah berisi:
- ✅ `GOOGLE_SHEETS_CREDENTIALS_JSON` - JSON dari service account
- ❌ `GOOGLE_SHEETS_SPREADSHEET_ID` - **Perlu diisi**
- ✅ `GOOGLE_SHEETS_WORKSHEET_NAME` - Sudah diisi: `SearchLog`

Edit `.env` dan isi `GOOGLE_SHEETS_SPREADSHEET_ID`:

```bash
# .env
GOOGLE_SHEETS_SPREADSHEET_ID=1abc123def456ghi789jkl
```

---

## 🚀 Langkah 4: Jalankan Aplikasi

```bash
# Install dependencies
pip install -r requirements.txt

# Jalankan server
python app.py
```

Cek output:
```
[INFO] Google Sheets integration berhasil diinisialisasi.
✔ Database dimuat: 40 laptop
✔ Flask server dimulai di http://localhost:5000
```

---

## 🧪 Langkah 5: Test Integrasi

1. Buka browser: `http://localhost:5000`
2. Pilih kategori kebutuhan dan budget
3. Klik **CARI**
4. Lihat hasil rekomendasi
5. Buka Google Sheets → worksheet `SearchLog`
6. Cek apakah baris baru muncul dengan data pencarian

Expected columns:
- `timestamp` - Waktu pencarian
- `kebutuhan` - Kategori yang dipilih
- `budget_kategori` - Budget yang digunakan
- `total_hasil` - Jumlah laptop yang ditemukan
- `hasil_detail` - Detail laptop dalam JSON
- Dan columns lainnya

---

## 🔐 Keamanan

### File `.env`

- ✅ **Sudah di-gitignore** - Tidak akan ter-commit ke GitHub
- ✅ **Berisi credentials JSON** - Aman karena private, tidak pernah di-share
- ✅ **Lokal only** - Hanya ada di mesin development

### Credentials JSON

- Disimpan di `.env` sebagai environment variable
- Tidak ada di-commit ke Git
- Hanya dibaca saat runtime

### Spreadsheet

- Hanya bisa diakses dengan service account yang memiliki email:
  - `spreadsheet-bot@linen-totality-484904-u5.iam.gserviceaccount.com`
- Anda harus memberi akses manual di Google Sheets

---

## 📊 Struktur Data di Google Sheets

Setiap row di spreadsheet berisi:

```json
{
  "timestamp": "2026-05-13T20:30:45Z",
  "kebutuhan": "Pengembang / Programmer",
  "budget_select": "2",
  "budget_manual": "",
  "budget_kategori": "Menengah",
  "budget_min": 8000000,
  "budget_max": 15000000,
  "merk": "Semua",
  "total_hasil": 5,
  "rule_ram_min": 16,
  "rule_gpu": "Integrated",
  "rule_storage_min": 512,
  "rule_catatan": "Nyaman untuk multi-IDE, Docker, dan proyek web.",
  "hasil_detail": "[{\"no\": 1, \"merk\": \"Dell\", ...}]"
}
```

---

## ⚠️ Troubleshooting

### Error: "Insufficient authentication scopes"

**Penyebab:** Service account tidak punya akses Drive API

**Solusi:**
- Update scope di `app.py` dan `setup_google_sheets.py` ✅ (sudah dilakukan)
- Restart server

### Error: "The user's Drive storage quota has been exceeded"

**Penyebab:** Google Drive storage penuh

**Solusi:**
- Gunakan spreadsheet yang sudah ada (Opsi B di Langkah 2)
- Atau bersihkan file di Google Drive

### Pencarian tidak ter-record di spreadsheet

**Troubleshoot:**
1. Pastikan `.env` sudah terisi `GOOGLE_SHEETS_SPREADSHEET_ID`
2. Lihat log server (cek [INFO] atau [WARNING])
3. Verifikasi spreadsheet ID di URL
4. Pastikan service account sudah diberi akses Editor

---

## 📝 File-File Penting

| File | Fungsi |
|------|--------|
| `.env` | Konfigurasi environment variables (jangan commit) |
| `.env.example` | Template `.env` untuk reference |
| `credentials.json` | Service account key (jangan commit) |
| `app.py` | Backend Flask dengan logging ke Google Sheets |
| `setup_google_sheets.py` | Script untuk setup spreadsheet otomatis |
| `convert_credentials.py` | Helper konversi credentials ke env var |

---

## 🎉 Selesai!

Aplikasi Anda sudah siap dengan integrasi Google Sheets yang aman. Setiap pencarian akan tercatat otomatis di spreadsheet online.

Untuk questions atau issues, cek README.md atau hubungi developer.

---

**Last Updated:** May 13, 2026
