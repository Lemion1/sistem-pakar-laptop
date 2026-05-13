/* ═══════════════════════════════════════════════════════════
   SISTEM PAKAR REKOMENDASI LAPTOP - JAVASCRIPT
   ═══════════════════════════════════════════════════════════ */

// ─────────────────────────────────────────────────────────
// STATE MANAGEMENT
// ─────────────────────────────────────────────────────────

let appState = {
    kategori: null,
    hasil: [],
    currentRule: null
};

// ─────────────────────────────────────────────────────────
// INITIALIZATION
// ─────────────────────────────────────────────────────────

document.addEventListener('DOMContentLoaded', function() {
    loadKategori();
    setupEventListeners();
    showEmptyState();
});

// ─────────────────────────────────────────────────────────
// API CALLS
// ─────────────────────────────────────────────────────────

async function loadKategori() {
    try {
        const response = await fetch('/api/kategori');
        const data = await response.json();
        appState.kategori = data;
        
        populateKebutuhanSelect(data.kebutuhan);
        populateBudgetSelect(data.budget);
        populateMerkSelect(data.merks);
    } catch (error) {
        console.error('Error loading kategori:', error);
        showErrorState('Gagal memuat kategori');
    }
}

async function cariRekomendasi(kebutuhan, budgetSelect, budgetManual, merk) {
    showLoadingState();

    try {
        const response = await fetch('/api/cari', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                kebutuhan: kebutuhan,
                budget_select: budgetSelect,
                budget_manual: budgetManual,
                merk: merk
            })
        });

        const data = await response.json();

        if (data.success) {
            appState.hasil = data.hasil;
            appState.currentRule = data.rule;
            
            displayResults(data);
            displayRuleInfo(data);
        } else {
            showErrorState(data.message);
        }
    } catch (error) {
        console.error('Error:', error);
        showErrorState('Terjadi kesalahan pada server');
    }
}

async function getDetail(laptopId) {
    try {
        const response = await fetch(`/api/detail/${laptopId}`);
        const data = await response.json();
        
        if (data.success) {
            displayDetailModal(data.data);
        }
    } catch (error) {
        console.error('Error:', error);
    }
}

// ─────────────────────────────────────────────────────────
// EVENT LISTENERS
// ─────────────────────────────────────────────────────────

function setupEventListeners() {
    const form = document.getElementById('formCari');
    form.addEventListener('submit', handleFormSubmit);

    const budgetManualInput = document.getElementById('budgetManual');
    const budgetSelect = document.getElementById('budgetSelect');

    // Clear manual input when select is chosen
    budgetSelect.addEventListener('change', function() {
        if (this.value) {
            budgetManualInput.value = '';
        }
    });

    // Clear select when manual input is filled
    budgetManualInput.addEventListener('input', function() {
        if (this.value) {
            budgetSelect.value = '';
        }
    });
}

async function handleFormSubmit(e) {
    e.preventDefault();

    const kebutuhan = document.getElementById('kebutuhan').value;
    const budgetSelect = document.getElementById('budgetSelect').value;
    const budgetManual = document.getElementById('budgetManual').value;
    const merk = document.getElementById('merkSelect').value;

    if (!kebutuhan) {
        showErrorState('Pilih kategori kebutuhan terlebih dahulu');
        return;
    }

    await cariRekomendasi(kebutuhan, budgetSelect, budgetManual, merk);
}

// ─────────────────────────────────────────────────────────
// POPULATE SELECTS
// ─────────────────────────────────────────────────────────

function populateKebutuhanSelect(kebutuhan) {
    const select = document.getElementById('kebutuhan');
    
    for (const [key, value] of Object.entries(kebutuhan)) {
        const option = document.createElement('option');
        option.value = value;
        option.textContent = value;
        select.appendChild(option);
    }
}

function populateBudgetSelect(budget) {
    const select = document.getElementById('budgetSelect');
    
    for (const [key, item] of Object.entries(budget)) {
        const option = document.createElement('option');
        option.value = key;
        option.textContent = item.label;
        select.appendChild(option);
    }
}

function populateMerkSelect(merks) {
    const select = document.getElementById('merkSelect');
    
    if (merks) {
        merks.forEach(merk => {
            const option = document.createElement('option');
            option.value = merk;
            option.textContent = merk;
            select.appendChild(option);
        });
    }
}

// ─────────────────────────────────────────────────────────
// DISPLAY FUNCTIONS
// ─────────────────────────────────────────────────────────

function displayResults(data) {
    const container = document.getElementById('resultsContainer');
    const table = document.getElementById('resultsTable');
    const resultCount = document.getElementById('resultCount');
    const resultsInfo = document.getElementById('resultsInfo');

    // Clear table
    table.innerHTML = '';

    // Hide loading state
    document.getElementById('loadingState').classList.add('hidden');
    document.getElementById('emptyState').classList.add('hidden');
    document.getElementById('errorState').classList.add('hidden');

    // Show container
    container.classList.remove('hidden');

    // Update badge
    resultCount.textContent = `${data.total} hasil`;
    resultCount.classList.remove('hidden');

    // Populate table
    if (data.hasil.length === 0) {
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td colspan="8" style="text-align: center; padding: 40px; color: #999;">
                Tidak ada laptop yang memenuhi kriteria
            </td>
        `;
        table.appendChild(tr);
        resultsInfo.textContent = 'Saran: perluas budget atau kurangi spesifikasi';
    } else {
        data.hasil.forEach(laptop => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td class="table-no">${laptop.no}</td>
                <td class="table-merk">${laptop.merk} ${laptop.model}</td>
                <td>${laptop.cpu}</td>
                <td>${laptop.gpu}</td>
                <td>${laptop.ram}</td>
                <td>${laptop.storage}</td>
                <td class="table-harga">${laptop.harga}</td>
                <td class="table-actions">
                    <button class="btn-detail" onclick="getDetail(${laptop.id})">Detail</button>
                </td>
            `;
            table.appendChild(tr);
        });

        const displayCount = Math.min(data.hasil.length, 5);
        resultsInfo.innerHTML = `
            <strong>✔ Ditemukan ${data.total} laptop</strong><br>
            Menampilkan ${displayCount} laptop termurah
            ${data.total > 5 ? ` (+ ${data.total - 5} laptop lain)` : ''}
        `;
    }
}

function displayRuleInfo(data) {
    const ruleInfo = document.getElementById('ruleInfo');
    const ruleContent = document.getElementById('ruleContent');

    const gpuLabel = {
        'Integrated': 'Integrated / Tanpa GPU Diskrit',
        'dedicated': 'GPU Diskrit (NVIDIA RTX/GTX)',
        'any': 'Bebas (Integrated atau Diskrit)'
    }[data.rule.gpu] || data.rule.gpu;

    const budgetLabel = `${data.budget} (Rp ${data.budget_min.toLocaleString('id-ID')} - Rp ${data.budget_max.toLocaleString('id-ID')})`;

    const html = `
        <div class="rule-item">
            <div class="rule-label">Kategori Kebutuhan</div>
            <div class="detail-value">${data.kebutuhan}</div>
        </div>
        <div class="rule-item">
            <div class="rule-label">Kategori Budget</div>
            <div class="detail-value">${budgetLabel}</div>
        </div>
        <div class="rule-item">
            <div class="rule-label">RAM Minimum</div>
            <div class="detail-value">${data.rule.ram_min} GB</div>
        </div>
        <div class="rule-item">
            <div class="rule-label">GPU Syarat</div>
            <div class="detail-value">${gpuLabel}</div>
        </div>
        <div class="rule-item">
            <div class="rule-label">Storage Minimum</div>
            <div class="detail-value">${data.rule.storage_min} GB</div>
        </div>
        <div class="rule-item">
            <div class="rule-label">Catatan</div>
            <div class="detail-value">${data.rule.catatan}</div>
        </div>
    `;

    ruleContent.innerHTML = html;
    ruleInfo.classList.remove('hidden');
}

function displayDetailModal(laptop) {
    const modal = document.getElementById('detailModal');
    const content = document.getElementById('detailContent');

    content.innerHTML = `
        <div class="detail-item">
            <div class="rule-label">Merk & Model</div>
            <div class="detail-value large">${laptop.merk} ${laptop.model}</div>
        </div>
        <div class="detail-item">
            <div class="rule-label">Processor (CPU)</div>
            <div class="detail-value">${laptop.cpu}</div>
        </div>
        <div class="detail-item">
            <div class="rule-label">GPU</div>
            <div class="detail-value">${laptop.gpu}</div>
        </div>
        <div class="detail-item">
            <div class="rule-label">RAM</div>
            <div class="detail-value">${laptop.ram}</div>
        </div>
        <div class="detail-item">
            <div class="rule-label">Storage</div>
            <div class="detail-value">${laptop.storage}</div>
        </div>
        <div class="detail-item">
            <div class="rule-label">Harga</div>
            <div class="detail-value large" style="color: #10b981;">${laptop.harga}</div>
        </div>
    `;

    modal.classList.remove('hidden');
}

// ─────────────────────────────────────────────────────────
// STATE DISPLAY FUNCTIONS
// ─────────────────────────────────────────────────────────

function showLoadingState() {
    document.getElementById('loadingState').classList.remove('hidden');
    document.getElementById('emptyState').classList.add('hidden');
    document.getElementById('errorState').classList.add('hidden');
    document.getElementById('resultsContainer').classList.add('hidden');
}

function showEmptyState() {
    document.getElementById('emptyState').classList.remove('hidden');
    document.getElementById('loadingState').classList.add('hidden');
    document.getElementById('errorState').classList.add('hidden');
    document.getElementById('resultsContainer').classList.add('hidden');
}

function showErrorState(message) {
    document.getElementById('errorMessage').textContent = message;
    document.getElementById('errorState').classList.remove('hidden');
    document.getElementById('loadingState').classList.add('hidden');
    document.getElementById('emptyState').classList.add('hidden');
    document.getElementById('resultsContainer').classList.add('hidden');
}

function closeModal() {
    document.getElementById('detailModal').classList.add('hidden');
}

// Close modal when clicking outside
document.addEventListener('click', function(event) {
    const modal = document.getElementById('detailModal');
    if (event.target === modal) {
        closeModal();
    }
});

// ─────────────────────────────────────────────────────────
// UTILITY FUNCTIONS
// ─────────────────────────────────────────────────────────

function formatCurrency(value) {
    return new Intl.NumberFormat('id-ID', {
        style: 'currency',
        currency: 'IDR',
        minimumFractionDigits: 0,
        maximumFractionDigits: 0
    }).format(value);
}

function parseNumber(str) {
    return parseInt(str.replace(/\D/g, ''), 10);
}
