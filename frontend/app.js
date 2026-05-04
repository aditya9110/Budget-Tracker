// ── CONSTANTS ──────────────────────────────────────────────────────────────

const PURPLE       = "#7030A0";
const PURPLE_LIGHT = "#9B59B6";
const BG_CARD      = "#16161d";
const TEXT_SEC     = "#8b87a0";
const GREEN        = "#27ae60";
const RED          = "#e74c3c";

const PLOTLY_BASE = {
    paper_bgcolor: "rgba(0,0,0,0)",
    plot_bgcolor:  "rgba(0,0,0,0)",
    font:          { family: "Consolas, monospace", color: "#8b87a0", size: 11 },
    margin:        { t: 10, b: 10, l: 10, r: 10 },
    showlegend:    false,
};

const MONTHS = [
    "January","February","March","April","May","June",
    "July","August","September","October","November","December"
];

// ── BRIDGE (PyQt6 QWebChannel) ───────────────────────────────────────────────

let _bridge = null;
let _callId = 0;
const _pending = {};

window.__resolveCall = function(callId, jsonResult) {
    const resolve = _pending[callId];
    if (resolve) {
        delete _pending[callId];
        resolve(JSON.parse(jsonResult));
    }
};

function callPython(method, ...args) {
    return new Promise((resolve) => {
        const id = String(_callId++);
        _pending[id] = resolve;
        _bridge.call(id, method, JSON.stringify(args));
    });
}

// ── STATE ────────────────────────────────────────────────────────────────────

let currentView    = "dashboard";
let selectedFile   = null;
let currentYear    = null;
let currentMonth   = null;
let pendingConfirm = null;  // function to call on modal confirm

// ── DOM REFS ─────────────────────────────────────────────────────────────────

// Custom dropdowns
const monthDropdown   = document.getElementById("month-dropdown");
const monthLabel      = document.getElementById("month-label");
const monthOptions    = document.getElementById("month-options");
const yearDropdown    = document.getElementById("year-dropdown");
const yearLabel       = document.getElementById("year-label");
const yearOptions     = document.getElementById("year-options");
const btnLoad         = document.getElementById("btn-load");
const periodControls  = document.getElementById("period-controls");
const toast           = document.getElementById("toast");
const modalOverlay    = document.getElementById("modal-overlay");
const modalTitle      = document.getElementById("modal-title");
const modalBody       = document.getElementById("modal-body");
const modalConfirm    = document.getElementById("modal-confirm");
const modalCancel     = document.getElementById("modal-cancel");
const txModalOverlay  = document.getElementById("tx-modal-overlay");
const txModalTitle    = document.getElementById("tx-modal-title");
const txModalCancel   = document.getElementById("tx-modal-cancel");
const txModalSave     = document.getElementById("tx-modal-save");
const dropZone        = document.getElementById("drop-zone");
const fileInput       = document.getElementById("file-input");
const btnBrowse       = document.getElementById("btn-browse");
const fileInfo        = document.getElementById("file-info");
const fileName        = document.getElementById("file-name");
const btnClear        = document.getElementById("btn-clear");
const btnImport       = document.getElementById("btn-import");
const importProgress  = document.getElementById("import-progress");
const progressFill    = document.getElementById("progress-fill");
const progressLabel   = document.getElementById("progress-label");
const btnAddTx        = document.getElementById("btn-add-transaction");

// ── INIT ─────────────────────────────────────────────────────────────────────

function init() {
    populatePeriodDropdowns();
    setupNavigation();
    setupPeriodControls();
    setupImport();
    setupModals();
    setupTransactionForm();
}

// ── CUSTOM DROPDOWN LOGIC ────────────────────────────────────────────────────

let selectedMonth = null;
let selectedYear  = null;

function buildDropdown(dropdown, optionsList, items, onSelect) {
    // Toggle open/close
    dropdown.querySelector(".custom-select-trigger").addEventListener("click", (e) => {
        e.stopPropagation();
        const isOpen = dropdown.classList.contains("open");
        closeAllDropdowns();
        if (!isOpen) dropdown.classList.add("open");
    });

    // Build options
    items.forEach(item => {
        const el = document.createElement("div");
        el.className   = "custom-option";
        el.textContent = item;
        el.dataset.value = item;
        el.addEventListener("click", (e) => {
            e.stopPropagation();
            dropdown.querySelectorAll(".custom-option").forEach(o => o.classList.remove("selected"));
            el.classList.add("selected");
            onSelect(item);
            dropdown.classList.remove("open");
        });
        optionsList.appendChild(el);
    });
}

function closeAllDropdowns() {
    document.querySelectorAll(".custom-select.open").forEach(d => d.classList.remove("open"));
}

// Close dropdowns when clicking outside
document.addEventListener("click", closeAllDropdowns);

function populatePeriodDropdowns() {
    const currentYear = new Date().getFullYear();
    const years = [];
    for (let y = currentYear; y >= 2026; y--) years.push(String(y));

    buildDropdown(monthDropdown, monthOptions, MONTHS, (val) => {
        selectedMonth    = val;
        monthLabel.textContent = val;
    });

    buildDropdown(yearDropdown, yearOptions, years, (val) => {
        selectedYear    = val;
        yearLabel.textContent = val;
    });

    // Default to current month/year
    const defaultMonth = MONTHS[new Date().getMonth()];
    const defaultYear  = String(currentYear);

    selectedMonth = defaultMonth;
    selectedYear  = defaultYear;
    monthLabel.textContent = defaultMonth;
    yearLabel.textContent  = defaultYear;

    // Mark defaults as selected
    setTimeout(() => {
        monthOptions.querySelectorAll(".custom-option").forEach(o => {
            if (o.dataset.value === defaultMonth) o.classList.add("selected");
        });
        yearOptions.querySelectorAll(".custom-option").forEach(o => {
            if (o.dataset.value === defaultYear) o.classList.add("selected");
        });
    }, 0);
}


// ── NAVIGATION ───────────────────────────────────────────────────────────────

const VIEWS_WITH_PERIOD = new Set(["dashboard", "transactions"]);

function setupNavigation() {
    document.querySelectorAll(".nav-item").forEach(btn => {
        btn.addEventListener("click", () => switchView(btn.dataset.view));
    });
}

function switchView(view) {
    currentView = view;

    document.querySelectorAll(".nav-item").forEach(btn => {
        btn.classList.toggle("active", btn.dataset.view === view);
    });

    document.querySelectorAll(".view").forEach(v => {
        v.classList.toggle("active", v.id === `view-${view}`);
    });

    const titles = {
        dashboard:    "📊 Dashboard",
        import:       "📂 Import Statement",
        transactions: "📋 Transactions",
        settings:     "⚙️ Settings"
    };
    document.getElementById("page-title").textContent = titles[view] || view;

    // Show/hide period controls
    if (VIEWS_WITH_PERIOD.has(view)) {
        periodControls.classList.remove("hidden");
    } else {
        periodControls.classList.add("hidden");
    }
}

// ── PERIOD CONTROLS ───────────────────────────────────────────────────────────

function setupPeriodControls() {
    btnLoad.addEventListener("click", handleLoad);
}

async function handleLoad() {
    const year  = selectedYear;
    const month = selectedMonth;
    if (!year || !month) { showToast("Select a month and year", "info"); return; }

    currentYear  = year;
    currentMonth = month;

    if (currentView === "dashboard") await loadDashboard(year, month);
    if (currentView === "transactions") await loadTransactions(year, month);
}

// ── DASHBOARD ────────────────────────────────────────────────────────────────

async function loadDashboard(year, month) {
    btnLoad.disabled = true;
    btnLoad.textContent = "Loading...";

    try {
        const result = await callPython("get_dashboard_data", year, month);
        if (!result.ok) { showToast(result.error, "error"); return; }

        const { transactions, categories, daily_spend, budget_status, top_transactions, source_breakdown } = result.data;

        if (!transactions.length) {
            showToast("No data found for this period. Import first.", "info");
            return;
        }

        // Show content, hide empty state
        document.getElementById("dashboard-empty").classList.add("hidden");
        document.getElementById("dashboard-content").classList.remove("hidden");

        renderKPIs(transactions, categories, budget_status);
        renderTopTransactions(top_transactions);

        setTimeout(() => {
            renderBarChart(categories);
            renderSourceDonutChart(source_breakdown);
            renderDailyChart(daily_spend);
            renderCumulativeChart(daily_spend);
            renderFamilyDonutChart(categories);
            renderTreemap(transactions);
        }, 100);

        showToast(`${month} ${year} loaded`, "success");

    } catch (e) {
        showToast("Error loading dashboard", "error");
    } finally {
        btnLoad.disabled = false;
        btnLoad.textContent = "Load";
    }
}

// ── KPIs ─────────────────────────────────────────────────────────────────────

function renderKPIs(transactions, categories, budgetStatus) {
    const total  = transactions.reduce((s, t) => s + t.spend, 0);
    const topCat = categories.length ? categories[0].type : "—";
    const days   = [...new Set(transactions.map(t => t.date))].length || 1;
    const avgDay = total / days;
    const count  = transactions.length;

    document.querySelector("#kpi-total .kpi-value").textContent = fmt(total);
    document.querySelector("#kpi-top .kpi-value").textContent   = topCat || "—";
    document.querySelector("#kpi-avg .kpi-value").textContent   = fmt(avgDay);
    document.querySelector("#kpi-count .kpi-value").textContent = count;

    const budgetEl = document.querySelector("#kpi-budget .kpi-value");
    if (budgetStatus) {
        const sign = budgetStatus.status === "surplus" ? "▲" : "▼";
        budgetEl.textContent = `${sign} ${fmt(Math.abs(budgetStatus.diff))}`;
        budgetEl.className   = `kpi-value ${budgetStatus.status}`;
    } else {
        budgetEl.textContent = "—";
        budgetEl.className   = "kpi-value";
    }
}

// ── CHARTS ───────────────────────────────────────────────────────────────────

function renderBarChart(categories) {
    const sorted = [...categories].sort((a, b) => a.total_spend - b.total_spend);
    Plotly.newPlot("chart-bar", [{
        type: "bar", orientation: "h",
        x: sorted.map(c => c.total_spend),
        y: sorted.map(c => c.type),
        text: sorted.map(c => fmt(c.total_spend)),
        textposition: "outside",
        textfont: { color: TEXT_SEC, size: 10 },
        marker: {
            color: sorted.map(c => c.total_spend),
            colorscale: [[0, "#2a1a3e"], [1, PURPLE]],
            line: { width: 0 }
        },
        hovertemplate: "<b>%{y}</b><br>%{x:,.0f}<extra></extra>"
    }], {
        ...PLOTLY_BASE,
        margin: { t: 10, b: 30, l: 110, r: 80 },
        xaxis: { visible: false, showgrid: false },
        yaxis: { showgrid: false, tickfont: { size: 10, color: TEXT_SEC } },
        height: 280,
    }, { displayModeBar: false, responsive: true });
}

function renderSourceDonutChart(sourceBreakdown) {
    Plotly.newPlot("chart-source-donut", [{
        type: "pie",
        labels: sourceBreakdown.map(s => s.source),
        values: sourceBreakdown.map(s => s.spend),
        hole: 0.55,
        marker: { colors: ["#7030A0", "#9B59B6", "#C39BD3"], line: { color: BG_CARD, width: 2 } },
        textinfo: "label+percent",
        textfont: { size: 11 },
        hovertemplate: "<b>%{label}</b><br>%{value:,.0f}<br>%{percent}<extra></extra>"
    }], {
        ...PLOTLY_BASE,
        margin: { t: 10, b: 10, l: 10, r: 10 },
        height: 280,
    }, { displayModeBar: false, responsive: true });
}

function renderDailyChart(dailySpend) {
    const dates  = dailySpend.map(d => d.date);
    const spends = dailySpend.map(d => d.total_spend);
    const avg7   = spends.map((_, i) => {
        const slice = spends.slice(Math.max(0, i - 6), i + 1);
        return slice.reduce((a, b) => a + b, 0) / slice.length;
    });

    Plotly.newPlot("chart-daily", [
        {
            type: "bar", x: dates, y: spends, name: "Daily",
            marker: { color: "rgba(112,48,160,0.4)" },
            hovertemplate: "%{x}<br>%{y:,.0f}<extra></extra>"
        },
        {
            type: "scatter", x: dates, y: avg7, name: "7-day Avg",
            line: { color: PURPLE_LIGHT, width: 2 },
            hovertemplate: "%{x}<br>Avg %{y:,.0f}<extra></extra>"
        }
    ], {
        ...PLOTLY_BASE,
        margin: { t: 20, b: 40, l: 50, r: 10 },
        xaxis: { showgrid: false, tickfont: { size: 9 } },
        yaxis: { showgrid: true, gridcolor: "rgba(255,255,255,0.04)", tickfont: { size: 9 } },
        barmode: "overlay", height: 280,
        showlegend: true,
        legend: { orientation: "h", y: 1.1, font: { size: 10 } }
    }, { displayModeBar: false, responsive: true });
}

function renderCumulativeChart(dailySpend) {
    const sorted = [...dailySpend].sort((a, b) => a.date.localeCompare(b.date));
    let cum = 0;
    const dates  = sorted.map(d => d.date);
    const cumArr = sorted.map(d => { cum += d.total_spend; return cum; });

    Plotly.newPlot("chart-cumulative", [{
        type: "scatter", x: dates, y: cumArr,
        fill: "tozeroy", fillcolor: "rgba(112,48,160,0.12)",
        line: { color: PURPLE, width: 2 },
        hovertemplate: "%{x}<br>Total: %{y:,.0f}<extra></extra>"
    }], {
        ...PLOTLY_BASE,
        margin: { t: 10, b: 40, l: 60, r: 10 },
        xaxis: { showgrid: false, tickfont: { size: 9 } },
        yaxis: { showgrid: true, gridcolor: "rgba(255,255,255,0.04)", tickfont: { size: 9 } },
        height: 280,
    }, { displayModeBar: false, responsive: true });
}

function renderFamilyDonutChart(categories) {
    const PARENTS_CATS = new Set(["Bills (P)", "Parents", "Medicines (P)"]);
    const FAMILY_CATS  = new Set([
        "Cash Withdrawal","EMI","Rent","Food","Entertainment",
        "Groceries","Bills","Personal","Shopping","Investment",
        "Insurance","Fuel","Travel","Medicines"
    ]);

    let parentsTotal = 0, familyTotal = 0;
    categories.forEach(c => {
        if (PARENTS_CATS.has(c.type))     parentsTotal += c.total_spend;
        else if (FAMILY_CATS.has(c.type)) familyTotal  += c.total_spend;
    });

    Plotly.newPlot("chart-family-donut", [{
        type: "pie",
        labels: ["Family", "Parents"],
        values: [familyTotal, parentsTotal],
        hole: 0.55,
        marker: { colors: [PURPLE, "#C39BD3"], line: { color: BG_CARD, width: 2 } },
        textinfo: "label+percent",
        textfont: { size: 11 },
        hovertemplate: "<b>%{label}</b><br>%{value:,.0f}<br>%{percent}<extra></extra>"
    }], {
        ...PLOTLY_BASE,
        margin: { t: 10, b: 10, l: 10, r: 10 },
        height: 280,
    }, { displayModeBar: false, responsive: true });
}

function renderTreemap(transactions) {
    const filtered  = transactions.filter(t => t.spend > 0);
    const ids       = filtered.map((_, i) => `tx_${i}`);
    const labels    = filtered.map(t => t.description ? t.description.slice(0, 35) : "Unknown");
    const parents   = filtered.map(t => t.type || "Others");
    const values    = filtered.map(t => t.spend);
    const catSet    = [...new Set(parents)];
    const allIds     = [...catSet, ...ids];
    const allLabels  = [...catSet, ...labels];
    const allParents = [...catSet.map(() => ""), ...parents];
    const catTotals = catSet.map(cat =>
        values.reduce((sum, v, i) => parents[i] === cat ? sum + v : sum, 0)
    );
    const allValues = [...catTotals, ...values];

    Plotly.newPlot("chart-treemap", [{
        type: "treemap",
        ids: allIds, labels: allLabels, parents: allParents, values: allValues,
        branchvalues: "total",
        texttemplate: "<b>%{label}</b><br>₹%{value:,.0f}",
        hovertemplate: "<b>%{label}</b><br>₹%{value:,.0f}<extra></extra>",
        marker: {
            colorscale: [[0, "#1e0a2e"], [1, PURPLE]],
            colors: allValues,
            line: { color: BG_CARD, width: 1 }
        }
    }], {
        ...PLOTLY_BASE,
        margin: { t: 10, b: 10, l: 10, r: 10 },
        height: 420,
    }, { displayModeBar: false, responsive: true });
}

// ── TOP TRANSACTIONS ─────────────────────────────────────────────────────────

function renderTopTransactions(transactions) {
    document.getElementById("top-transactions").innerHTML =
        buildTable(transactions, ["date","description","type","source","spend"], false);
}

// ── IMPORT ───────────────────────────────────────────────────────────────────

function setupImport() {
    // Browse button
    btnBrowse.addEventListener("click", () => fileInput.click());
    fileInput.addEventListener("change", () => {
        if (fileInput.files[0]) setSelectedFile(fileInput.files[0]);
    });

    // Drag and drop
    dropZone.addEventListener("dragover", (e) => {
        e.preventDefault();
        dropZone.classList.add("dragover");
    });
    dropZone.addEventListener("dragleave", () => dropZone.classList.remove("dragover"));
    dropZone.addEventListener("drop", (e) => {
        e.preventDefault();
        dropZone.classList.remove("dragover");
        const file = e.dataTransfer.files[0];
        if (file && (file.name.endsWith(".xlsx") || file.name.endsWith(".xls"))) {
            setSelectedFile(file);
        } else {
            showToast("Only .xlsx or .xls files supported", "error");
        }
    });

    // Clear selection
    btnClear.addEventListener("click", clearSelectedFile);

    // Import
    btnImport.addEventListener("click", handleImport);
}

function setSelectedFile(file) {
    selectedFile = file;
    fileName.textContent = file.name;
    fileInfo.classList.remove("hidden");
    btnImport.classList.remove("hidden");
    dropZone.style.opacity = "0.5";
}

function clearSelectedFile() {
    selectedFile = null;
    fileInput.value = "";
    fileInfo.classList.add("hidden");
    btnImport.classList.add("hidden");
    dropZone.style.opacity = "1";
}

async function handleImport() {
    if (!selectedFile) return;

    const base64 = await fileToBase64(selectedFile);
    const fname  = selectedFile.name;

    setImportLoading(true);

    try {
        const result = await callPython("import_statement", fname, base64);

        if (!result.ok) {
            // Data already exists — show overwrite confirmation
            if (result.error.startsWith("DATA_EXISTS:")) {
                const [, year, month] = result.error.split(":");
                setImportLoading(false);
                showConfirmModal(
                    "Data Already Exists",
                    `Data for ${month} ${year} already exists. Overwrite?`,
                    () => runImportForce(fname, base64)
                );
                return;
            }
            showToast(result.error, "error");
            return;
        }

        finishImport(result.data);

    } catch (e) {
        showToast("Unexpected error during import", "error");
    } finally {
        setImportLoading(false);
    }
}

async function runImportForce(fname, base64) {
    setImportLoading(true);
    try {
        const result = await callPython("import_statement_force", fname, base64);
        if (result.ok) finishImport(result.data);
        else showToast(result.error, "error");
    } catch (e) {
        showToast("Unexpected error during import", "error");
    } finally {
        setImportLoading(false);
    }
}

function finishImport(data) {
    const { count, year, month } = data;
    showToast(`${count} transactions imported`, "success");
    selectedYear  = String(year);
    selectedMonth = month;
    yearLabel.textContent  = year;
    monthLabel.textContent = month;
    currentYear  = String(year);
    currentMonth = month;
    clearSelectedFile();
    switchView("transactions");
    loadTransactions(year, month);
}

function setImportLoading(loading) {
    btnImport.disabled    = loading;
    btnImport.textContent = loading ? "Importing..." : "Import & Categorize";
    if (loading) {
        importProgress.classList.remove("hidden");
        animateProgress();
    } else {
        importProgress.classList.add("hidden");
        progressFill.style.width = "0%";
    }
}

function fileToBase64(file) {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onload  = () => resolve(reader.result.split(",")[1]);
        reader.onerror = reject;
        reader.readAsDataURL(file);
    });
}

function animateProgress() {
    let pct = 0;
    progressLabel.textContent = "Processing...";
    const interval = setInterval(() => {
        pct = Math.min(pct + Math.random() * 12, 90);
        progressFill.style.width = pct + "%";
        if (pct >= 90) clearInterval(interval);
    }, 300);
}

// ── TRANSACTIONS ─────────────────────────────────────────────────────────────

async function loadTransactions(year, month) {
    const result = await callPython("get_transactions", year, month);
    if (!result.ok) { showToast(result.error, "error"); return; }

    const rows = result.data;

    document.getElementById("transactions-empty").classList.add("hidden");
    document.getElementById("transactions-content").classList.remove("hidden");

    const cols = ["date","description","source","type","spend","remarks"];
    document.getElementById("all-transactions").innerHTML =
        buildTable(rows, cols, true);
}

// ── TRANSACTION FORM (Add / Edit / Delete) ────────────────────────────────────

function setupTransactionForm() {
    btnAddTx.addEventListener("click", () => openTxModal(null));
    txModalCancel.addEventListener("click", () => txModalOverlay.classList.add("hidden"));
    txModalSave.addEventListener("click", saveTx);
}

function openTxModal(row) {
    // Clear previous errors
    ["err-date","err-spend","err-description","err-type","err-source"].forEach(id => {
        document.getElementById(id).textContent = "";
    });
    ["tx-date","tx-spend","tx-description","tx-type","tx-source"].forEach(id => {
        document.getElementById(id).classList.remove("invalid");
    });

    txModalTitle.textContent = row ? "Edit Transaction" : "Add Transaction";
    document.getElementById("tx-id").value          = row ? row.id : "";
    document.getElementById("tx-date").value         = row ? row.date : "";
    document.getElementById("tx-spend").value        = row ? row.spend : "";
    document.getElementById("tx-description").value  = row ? row.description : "";
    document.getElementById("tx-type").value         = row ? row.type : "";
    document.getElementById("tx-source").value       = row ? row.source : "";
    document.getElementById("tx-remarks").value      = row ? row.remarks : "";
    txModalOverlay.classList.remove("hidden");
}

function validateTxForm() {
    const fields = [
        { id: "tx-date",        errId: "err-date",        rule: v => /^\d{2}-\d{2}-\d{4}$/.test(v),  msg: "Enter a valid date (DD-MM-YYYY)" },
        { id: "tx-spend",       errId: "err-spend",       rule: v => !isNaN(v) && Number(v) > 0,      msg: "Enter a positive amount" },
        { id: "tx-description", errId: "err-description", rule: v => v.trim().length >= 3,             msg: "Min 3 characters required" },
        { id: "tx-type",        errId: "err-type",        rule: v => v.trim().length > 0,              msg: "Category is required" },
        { id: "tx-source",      errId: "err-source",      rule: v => v.trim().length > 0,              msg: "Source is required" },
    ];

    let valid = true;

    fields.forEach(({ id, errId, rule, msg }) => {
        const input = document.getElementById(id);
        const err   = document.getElementById(errId);
        const val   = input.value;

        if (!rule(val)) {
            input.classList.add("invalid");
            err.textContent = msg;
            valid = false;
        } else {
            input.classList.remove("invalid");
            err.textContent = "";
        }
    });

    return valid;
}

async function saveTx() {
    if (!validateTxForm()) return;

    const id = document.getElementById("tx-id").value;
    const payload = {
        date:        document.getElementById("tx-date").value,
        spend:       parseFloat(document.getElementById("tx-spend").value) || 0,
        description: document.getElementById("tx-description").value,
        type:        document.getElementById("tx-type").value,
        source:      document.getElementById("tx-source").value,
        remarks:     document.getElementById("tx-remarks").value,
        year:        currentYear,
        month:       currentMonth,
    };

    const method = id ? "update_transaction" : "add_transaction";
    if (id) payload.id = parseInt(id);

    const result = await callPython(method, payload);
    if (result.ok) {
        txModalOverlay.classList.add("hidden");
        showToast(id ? "Transaction updated" : "Transaction added", "success");
        await loadTransactions(currentYear, currentMonth);
    } else {
        showToast(result.error, "error");
    }
}

async function deleteTx(id) {
    showConfirmModal("Delete Transaction", "Are you sure you want to delete this transaction?", async () => {
        const result = await callPython("delete_transaction", id);
        if (result.ok) {
            showToast("Transaction deleted", "success");
            await loadTransactions(currentYear, currentMonth);
        } else {
            showToast(result.error, "error");
        }
    });
}

// ── MODALS ───────────────────────────────────────────────────────────────────

function setupModals() {
    modalCancel.addEventListener("click",  () => modalOverlay.classList.add("hidden"));
    modalConfirm.addEventListener("click", () => {
        modalOverlay.classList.add("hidden");
        if (pendingConfirm) { pendingConfirm(); pendingConfirm = null; }
    });
}

function showConfirmModal(title, body, onConfirm) {
    modalTitle.textContent = title;
    modalBody.textContent  = body;
    pendingConfirm = onConfirm;
    modalOverlay.classList.remove("hidden");
}

// ── TABLE BUILDER ─────────────────────────────────────────────────────────────

function buildTable(rows, cols, withActions) {
    if (!rows.length) return `<div style="padding:24px;text-align:center;color:#4a4760;font-size:13px;">No transactions found</div>`;

    const headerCols = withActions ? [...cols, "actions"] : cols;
    const headers = headerCols.map(c =>
        `<th>${c.replace(/_/g," ").toUpperCase()}</th>`
    ).join("");

    const body = rows.map(row => {
        const cells = cols.map(c => {
            let val = row[c] ?? "—";
            let cls = "";
            if (c === "spend") { val = fmt(val); cls = "amount"; }
            if (c === "type")  { cls = "category"; }
            if (c === "date")  { val = formatDate(val); }
            if (c === "description" && typeof val === "string") val = val.slice(0, 55);
            return `<td class="${cls}">${val}</td>`;
        }).join("");

        const actions = withActions
            ? `<td class="actions">
                <button class="btn-edit"   onclick='openTxModal(${JSON.stringify(row)})'>✎</button>
                <button class="btn-delete" onclick='deleteTx(${row.id})'>✕</button>
               </td>`
            : "";

        return `<tr>${cells}${actions}</tr>`;
    }).join("");

    return `<table><thead><tr>${headers}</tr></thead><tbody>${body}</tbody></table>`;
}

// ── HELPERS ──────────────────────────────────────────────────────────────────

function fmt(n) {
    return `₹${Number(n).toLocaleString("en-IN", { maximumFractionDigits: 0 })}`;
}

function formatDate(str) {
    if (!str) return "—";
    const parts = str.split("-");
    if (parts.length === 3) {
        const m = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"];
        return `${parts[0]} ${m[parseInt(parts[1]) - 1]}`;
    }
    return str;
}

// ── TOAST ────────────────────────────────────────────────────────────────────

let toastTimer = null;

function showToast(message, type = "info") {
    toast.textContent = message;
    toast.className = `toast ${type} show`;
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => toast.classList.remove("show"), 3000);
}

// ── BRIDGE SETUP ─────────────────────────────────────────────────────────────

function setupBridge() {
    const script = document.createElement("script");
    script.src = "qrc:///qtwebchannel/qwebchannel.js";
    script.onload = () => {
        new QWebChannel(qt.webChannelTransport, (channel) => {
            _bridge = channel.objects.bridge;
            init();
        });
    };
    document.head.appendChild(script);
}

window.addEventListener("load", setupBridge);
