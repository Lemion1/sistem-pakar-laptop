"""
==========================================================
SISTEM PAKAR REKOMENDASI LAPTOP - FORWARD CHAINING
==========================================================
Judul Proyek : Penerapan Sistem Pakar Menggunakan Metode
               Forward Chaining untuk Rekomendasi Pemilihan
               Laptop Sesuai Kebutuhan Pengguna
Mata Kuliah  : Sistem Cerdas (PBL)
==========================================================
"""

import csv
import os
import sys

# ──────────────────────────────────────────────────────────
#  KONFIGURASI PATH DATA
# ──────────────────────────────────────────────────────────
BASE_DIR  = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, "data_laptop.csv")


# ══════════════════════════════════════════════════════════
#  MODUL 1 : KNOWLEDGE BASE (BASIS PENGETAHUAN)
#  Berisi rule-rule yang digunakan Forward Chaining
# ══════════════════════════════════════════════════════════

# Kategori kebutuhan pengguna
KATEGORI_KEBUTUHAN = {
    "1": "Pelajar / Mahasiswa Umum",
    "2": "Profesional / Bisnis",
    "3": "Gaming",
    "4": "Desain Grafis / Konten Kreator",
    "5": "Pengembang / Programmer",
}

# Kategori budget
KATEGORI_BUDGET = {
    "1": ("Ekonomis",        0,         8_000_000),
    "2": ("Menengah",  8_000_000,    15_000_000),
    "3": ("Tinggi",   15_000_000,    25_000_000),
    "4": ("Premium",  25_000_000, 999_999_999),
}

# Rule base: mapping (kebutuhan, budget) → kriteria minimum laptop
# Format nilai: (ram_min_gb, gpu_jenis, storage_min_gb, catatan)
RULES = {
    # ── Pelajar / Mahasiswa Umum ──────────────────────────
    ("Pelajar / Mahasiswa Umum", "Ekonomis"):
        dict(ram_min=4,  gpu="Integrated", storage_min=128,
             catatan="Cocok untuk tugas ringan, browsing, dan dokumen."),
    ("Pelajar / Mahasiswa Umum", "Menengah"):
        dict(ram_min=8,  gpu="Integrated", storage_min=256,
             catatan="Nyaman untuk multitasking, presentasi, dan e-learning."),
    ("Pelajar / Mahasiswa Umum", "Tinggi"):
        dict(ram_min=16, gpu="Integrated", storage_min=512,
             catatan="Performa lebih lapang untuk riset dan proyek kampus."),
    ("Pelajar / Mahasiswa Umum", "Premium"):
        dict(ram_min=16, gpu="any",        storage_min=512,
             catatan="Fleksibel, bisa digunakan juga untuk proyek berat ke depannya."),

    # ── Profesional / Bisnis ─────────────────────────────
    ("Profesional / Bisnis", "Ekonomis"):
        dict(ram_min=8,  gpu="Integrated", storage_min=256,
             catatan="Cukup untuk office, email, dan video call."),
    ("Profesional / Bisnis", "Menengah"):
        dict(ram_min=16, gpu="Integrated", storage_min=512,
             catatan="Ideal untuk produktivitas harian dan meeting online."),
    ("Profesional / Bisnis", "Tinggi"):
        dict(ram_min=16, gpu="Integrated", storage_min=512,
             catatan="Performa stabil untuk kerja hybrid dan analisis data ringan."),
    ("Profesional / Bisnis", "Premium"):
        dict(ram_min=32, gpu="Integrated", storage_min=512,
             catatan="Untuk eksekutif atau profesional yang butuh performa maksimal."),

    # ── Gaming ────────────────────────────────────────────
    ("Gaming", "Ekonomis"):
        dict(ram_min=8,  gpu="dedicated",  storage_min=512,
             catatan="Gaming entry-level, bisa main game ringan hingga menengah."),
    ("Gaming", "Menengah"):
        dict(ram_min=16, gpu="dedicated",  storage_min=512,
             catatan="Gaming 1080p lancar, cocok untuk gamer kasual."),
    ("Gaming", "Tinggi"):
        dict(ram_min=16, gpu="dedicated",  storage_min=512,
             catatan="Gaming 1080p–1440p, performa tinggi dan stabil."),
    ("Gaming", "Premium"):
        dict(ram_min=16, gpu="dedicated",  storage_min=1024,
             catatan="Gaming enthusiast, 1440p–4K, frame rate tinggi."),

    # ── Desain Grafis / Konten Kreator ───────────────────
    ("Desain Grafis / Konten Kreator", "Ekonomis"):
        dict(ram_min=8,  gpu="Integrated", storage_min=256,
             catatan="Desain sederhana, editing foto resolusi standar."),
    ("Desain Grafis / Konten Kreator", "Menengah"):
        dict(ram_min=16, gpu="any",        storage_min=512,
             catatan="Editing video 1080p, desain vektor, ilustrasi digital."),
    ("Desain Grafis / Konten Kreator", "Tinggi"):
        dict(ram_min=16, gpu="dedicated",  storage_min=512,
             catatan="Editing video 4K, rendering 3D menengah."),
    ("Desain Grafis / Konten Kreator", "Premium"):
        dict(ram_min=32, gpu="dedicated",  storage_min=1024,
             catatan="Produksi konten profesional, rendering cepat."),

    # ── Pengembang / Programmer ───────────────────────────
    ("Pengembang / Programmer", "Ekonomis"):
        dict(ram_min=8,  gpu="Integrated", storage_min=256,
             catatan="Coding teks, web dasar, skrip ringan."),
    ("Pengembang / Programmer", "Menengah"):
        dict(ram_min=16, gpu="Integrated", storage_min=512,
             catatan="Nyaman untuk multi-IDE, Docker, dan proyek web."),
    ("Pengembang / Programmer", "Tinggi"):
        dict(ram_min=16, gpu="Integrated", storage_min=512,
             catatan="Virtualisasi, machine learning ringan, compile cepat."),
    ("Pengembang / Programmer", "Premium"):
        dict(ram_min=32, gpu="any",        storage_min=512,
             catatan="ML/AI workload, banyak VM, proyek skala besar."),
}


# ══════════════════════════════════════════════════════════
#  MODUL 2 : DATABASE LAPTOP
# ══════════════════════════════════════════════════════════

def parse_harga(harga_str: str) -> int:
    """Konversi 'Rp 16.199.000' → 16199000 (int)."""
    clean = harga_str.replace("Rp", "").replace(".", "").replace(",", "").strip()
    try:
        return int(clean)
    except ValueError:
        return 0


def parse_ram(ram_str: str) -> int:
    """Ambil angka RAM terbesar, misal '16GB/32GB' → 32, '16GB' → 16."""
    parts = ram_str.upper().replace("GB", "").split("/")
    try:
        return max(int(p.strip()) for p in parts)
    except ValueError:
        return 0


def parse_storage(storage_str: str) -> int:
    """Konversi storage ke GB: '1TB'→1024, '512GB'→512."""
    s = storage_str.upper().strip()
    if "TB" in s:
        return int(s.replace("TB", "").strip()) * 1024
    return int(s.replace("GB", "").strip())


def load_database(filepath: str) -> list[dict]:
    """Muat CSV laptop ke list of dict."""
    laptops = []
    with open(filepath, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            laptops.append({
                "no":      int(row["No"]),
                "merk":    row["Merk"].strip(),
                "model":   row["Model"].strip(),
                "cpu":     row["CPU"].strip(),
                "gpu":     row["GPU"].strip(),
                "ram":     parse_ram(row["RAM"]),
                "ram_raw": row["RAM"].strip(),
                "storage": parse_storage(row["Storage"]),
                "storage_raw": row["Storage"].strip(),
                "harga":   parse_harga(row["Harga"]),
                "harga_raw": row["Harga"].strip(),
            })
    return laptops


# ══════════════════════════════════════════════════════════
#  MODUL 3 : MESIN INFERENSI FORWARD CHAINING
# ══════════════════════════════════════════════════════════

def klasifikasi_gpu(gpu_str: str) -> str:
    """
    Klasifikasikan GPU ke 3 kelompok:
    - 'Integrated' : GPU terintegrasi / Apple Silicon
    - 'dedicated'  : GPU diskrit (RTX / GTX)
    - 'apple'      : Apple GPU (8C GPU, 10C GPU)
    """
    g = gpu_str.strip().upper()
    if "RTX" in g or "GTX" in g:
        return "dedicated"
    if "GPU" in g:               # 8C GPU, 10C GPU (Apple)
        return "apple"
    return "Integrated"


def is_gpu_memenuhi(gpu_laptop: str, gpu_syarat: str) -> bool:
    """
    Cek apakah GPU laptop memenuhi syarat rule.
    - "Integrated" : harus Integrated (termasuk Apple Silicon dianggap integrated)
    - "dedicated"  : harus GPU diskrit
    - "any"        : apapun diterima
    """
    kelas = klasifikasi_gpu(gpu_laptop)
    if gpu_syarat == "any":
        return True
    if gpu_syarat == "Integrated":
        return kelas in ("Integrated", "apple")
    if gpu_syarat == "dedicated":
        return kelas == "dedicated"
    return False


def forward_chaining(
    laptops: list[dict],
    kebutuhan: str,
    nama_budget: str,
    budget_min: int,
    budget_max: int
) -> tuple[list[dict], dict, str]:
    """
    Mesin inferensi Forward Chaining.

    Alur:
    1. Tentukan FAKTA awal dari input pengguna.
    2. Cocokkan fakta dengan RULE BASE → dapatkan kriteria minimum.
    3. FILTER database laptop berdasarkan kriteria.
    4. URUTKAN hasil dari harga termurah.

    Return: (hasil_rekomendasi, rule_yang_aktif, catatan_rule)
    """

    # ── LANGKAH 1: Fakta Awal ─────────────────────────────
    fakta = {
        "kebutuhan": kebutuhan,
        "budget_kategori": nama_budget,
        "budget_min": budget_min,
        "budget_max": budget_max,
    }

    # ── LANGKAH 2: Rule Firing ────────────────────────────
    kunci_rule = (kebutuhan, nama_budget)
    if kunci_rule not in RULES:
        return [], {}, "Rule tidak ditemukan untuk kombinasi ini."

    rule = RULES[kunci_rule]
    catatan = rule["catatan"]

    # ── LANGKAH 3: Filter / Working Memory ───────────────
    hasil = []
    for lap in laptops:
        # Cek budget
        if not (budget_min <= lap["harga"] <= budget_max):
            continue
        # Cek RAM minimum
        if lap["ram"] < rule["ram_min"]:
            continue
        # Cek Storage minimum
        if lap["storage"] < rule["storage_min"]:
            continue
        # Cek GPU
        if not is_gpu_memenuhi(lap["gpu"], rule["gpu"]):
            continue
        hasil.append(lap)

    # ── LANGKAH 4: Urutkan harga termurah ─────────────────
    hasil.sort(key=lambda x: x["harga"])

    return hasil, rule, catatan


# ══════════════════════════════════════════════════════════
#  MODUL 4 : ANTARMUKA CLI
# ══════════════════════════════════════════════════════════

SEP_TEBAL = "=" * 60
SEP_TIPIS = "-" * 60


def cetak_header():
    print()
    print(SEP_TEBAL)
    print("  SISTEM PAKAR REKOMENDASI LAPTOP")
    print("  Metode : Forward Chaining")
    print(SEP_TEBAL)
    print()


def cetak_menu(judul: str, pilihan: dict, dengan_keluar: bool = True) -> str:
    """Tampilkan menu dan terima input valid."""
    print(f"\n{judul}")
    print(SEP_TIPIS)
    for k, v in pilihan.items():
        print(f"  [{k}] {v}")
    if dengan_keluar:
        print("  [0] Keluar")
    print(SEP_TIPIS)

    while True:
        pilih = input("  Pilihan Anda : ").strip()
        if dengan_keluar and pilih == "0":
            return "0"
        if pilih in pilihan:
            return pilih
        print("  [!] Input tidak valid. Silakan coba lagi.")


def tanya_budget_manual() -> int:
    """Minta input budget angka dari pengguna."""
    while True:
        raw = input("  Masukkan budget maksimal (contoh: 12000000) : ").strip()
        raw = raw.replace(".", "").replace(",", "").replace(" ", "")
        try:
            nilai = int(raw)
            if nilai <= 0:
                raise ValueError
            return nilai
        except ValueError:
            print("  [!] Masukkan angka yang valid.")


def tampilkan_fakta_rule(kebutuhan: str, budget_label: str, rule: dict):
    """Cetak fakta dan rule yang sedang aktif (transparansi inferensi)."""
    gpu_label = {
        "Integrated": "Integrated / Tanpa GPU Diskrit",
        "dedicated":  "GPU Diskrit (NVIDIA RTX/GTX)",
        "any":        "Bebas (Integrated atau Diskrit)",
    }.get(rule["gpu"], rule["gpu"])

    print()
    print("  ┌─ FAKTA & RULE AKTIF ───────────────────────────────")
    print(f"  │  Kebutuhan    : {kebutuhan}")
    print(f"  │  Budget       : {budget_label}")
    print(f"  │  RAM Minimum  : {rule['ram_min']} GB")
    print(f"  │  GPU Syarat   : {gpu_label}")
    print(f"  │  Storage Min  : {rule['storage_min']} GB")
    print(f"  │  Catatan Rule : {rule['catatan']}")
    print("  └────────────────────────────────────────────────────")


def tampilkan_hasil(hasil: list[dict], rule: dict, max_tampil: int = 5):
    """Tampilkan daftar laptop yang direkomendasikan."""
    print()
    if not hasil:
        print("  ⚠  Tidak ada laptop yang memenuhi semua kriteria.")
        print("     Saran: perluas budget atau kurangi spesifikasi.")
        return

    tampil = hasil[:max_tampil]
    print(f"  ✔  Ditemukan {len(hasil)} laptop. Menampilkan {len(tampil)} terbaik (termurah):")
    print()

    for i, lap in enumerate(tampil, 1):
        print(f"  {'─'*54}")
        print(f"  #{i}  {lap['merk']} {lap['model']}")
        print(f"       CPU     : {lap['cpu']}")
        print(f"       GPU     : {lap['gpu']}")
        print(f"       RAM     : {lap['ram_raw']}")
        print(f"       Storage : {lap['storage_raw']}")
        print(f"       Harga   : {lap['harga_raw']}")
    print(f"  {'─'*54}")

    if len(hasil) > max_tampil:
        print(f"\n  (+ {len(hasil) - max_tampil} laptop lain memenuhi kriteria)")


def tanya_detail(hasil: list[dict]):
    """Izinkan pengguna melihat laptop tertentu lebih detail."""
    if not hasil:
        return
    while True:
        pilih = input("\n  Lihat detail laptop #? (Enter untuk lewati) : ").strip()
        if pilih == "":
            break
        try:
            idx = int(pilih) - 1
            if 0 <= idx < len(hasil):
                lap = hasil[idx]
                print()
                print(f"  {'═'*54}")
                print(f"  DETAIL LAPTOP #{idx+1}")
                print(f"  {'═'*54}")
                print(f"  Merk    : {lap['merk']}")
                print(f"  Model   : {lap['model']}")
                print(f"  CPU     : {lap['cpu']}")
                print(f"  GPU     : {lap['gpu']}")
                print(f"  RAM     : {lap['ram_raw']}")
                print(f"  Storage : {lap['storage_raw']}")
                print(f"  Harga   : {lap['harga_raw']}")
                print(f"  {'═'*54}")
            else:
                print("  [!] Nomor tidak ada dalam daftar.")
        except ValueError:
            print("  [!] Masukkan nomor saja.")


# ══════════════════════════════════════════════════════════
#  MODUL 5 : MAIN LOOP
# ══════════════════════════════════════════════════════════

def main():
    # Muat database
    if not os.path.exists(DATA_FILE):
        print(f"[ERROR] File data tidak ditemukan: {DATA_FILE}")
        sys.exit(1)

    laptops = load_database(DATA_FILE)

    cetak_header()
    print(f"  Database   : {len(laptops)} laptop dimuat")
    print(f"  Knowledge  : {len(RULES)} rule aktif")

    while True:
        # ── Pilih Kebutuhan ───────────────────────────────
        pilih_kebutuhan = cetak_menu(
            "LANGKAH 1 : Pilih Kategori Kebutuhan",
            KATEGORI_KEBUTUHAN
        )
        if pilih_kebutuhan == "0":
            print("\n  Terima kasih telah menggunakan Sistem Pakar Laptop.\n")
            break

        kebutuhan = KATEGORI_KEBUTUHAN[pilih_kebutuhan]

        # ── Pilih Budget ──────────────────────────────────
        label_budget = {k: f"{v[0]}  (Rp {v[1]:,.0f} – Rp {v[2]:,.0f})"
                           .replace(",", ".")
                        for k, v in KATEGORI_BUDGET.items()}
        label_budget["5"] = "Input manual"

        pilih_budget = cetak_menu(
            "LANGKAH 2 : Pilih Kategori Budget",
            label_budget
        )
        if pilih_budget == "0":
            continue

        if pilih_budget == "5":
            budget_max = tanya_budget_manual()
            budget_min = 0
            nama_budget = None
            # Cari kategori yang sesuai dengan budget manual
            for _, (nama, bmin, bmax) in KATEGORI_BUDGET.items():
                if budget_max <= bmax:
                    nama_budget = nama
                    budget_min  = bmin
                    budget_max  = min(budget_max, bmax)
                    break
            if not nama_budget:
                nama_budget = "Premium"
                budget_min  = 25_000_000
        else:
            nama_budget, budget_min, budget_max = KATEGORI_BUDGET[pilih_budget]

        # ── Forward Chaining ──────────────────────────────
        print()
        print(SEP_TIPIS)
        print("  ⚙  Menjalankan mesin inferensi Forward Chaining ...")
        print(SEP_TIPIS)

        hasil, rule, catatan = forward_chaining(
            laptops, kebutuhan, nama_budget, budget_min, budget_max
        )

        budget_label = (
            f"{nama_budget}  "
            f"(Rp {budget_min:,.0f} – Rp {budget_max:,.0f})".replace(",", ".")
        )

        tampilkan_fakta_rule(kebutuhan, budget_label, rule)
        tampilkan_hasil(hasil, rule)
        tanya_detail(hasil[:5] if len(hasil) >= 5 else hasil)

        # ── Lanjut? ───────────────────────────────────────
        print()
        lagi = input("  Konsultasi lagi? (y/n) : ").strip().lower()
        if lagi != "y":
            print("\n  Terima kasih telah menggunakan Sistem Pakar Laptop.\n")
            break


if __name__ == "__main__":
    main()
