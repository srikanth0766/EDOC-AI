/* global Chart */
'use strict';

const BACKEND = 'http://localhost:8000';

// ─── Chart instances ──────────────────────────────────────────────────────────
let histChart = null;
let debtChart = null;
let riskChart = null;

// ─── Chart.js defaults ───────────────────────────────────────────────────────
Chart.defaults.color = '#64748b';
Chart.defaults.font.family = 'Inter, sans-serif';

// ─── On load ──────────────────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
    loadData();
    seedDemoData(); // seed charts if backend has no data yet
});

// ─── Load & render ────────────────────────────────────────────────────────────
async function loadData() {
    try {
        const res = await fetch(`${BACKEND}/sprint-analytics`);
        if (!res.ok) throw new Error(`Backend ${res.status}`);
        const data = await res.json();
        renderSummaryCards(data.summary);
        renderHistoryChart(data.sprints);
        renderDebtChart(data.sprints);
        renderSprintTable(data.sprints);
        if (data.sprints.length >= 2) runRiskPrediction();
    } catch (e) {
        console.warn('Backend unavailable — showing demo data.', e.message);
        seedDemoData();
    }
}

// ─── Summary Cards ────────────────────────────────────────────────────────────
function renderSummaryCards(summary) {
    if (!summary) return;
    setText('stat-sprints', summary.total_sprints);
    setText('stat-smells', summary.total_smells_detected);
    setText('stat-refactored', summary.total_refactored);
    setText('stat-avg', summary.average_smell_per_sprint);

    const trend = summary.trend || 'stable';
    const icons = { increasing: '📈', decreasing: '📉', stable: '➡️', insufficient_data: '❓' };
    setText('trend-icon', icons[trend] || '➡️');
    setText('stat-trend', trend.replace('_', ' '));
}

// ─── Sprint History Line Chart ────────────────────────────────────────────────
function renderHistoryChart(sprints) {
    const labels = sprints.map(s => s.sprint_id);
    const smells = sprints.map(s => s.smell_count);
    const refactored = sprints.map(s => s.refactor_count);

    const ctx = document.getElementById('chart-history').getContext('2d');
    if (histChart) histChart.destroy();

    histChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels,
            datasets: [
                {
                    label: 'Smells',
                    data: smells,
                    borderColor: '#6c63ff',
                    backgroundColor: 'rgba(108,99,255,0.1)',
                    fill: true,
                    tension: 0.4,
                    pointBackgroundColor: '#6c63ff',
                },
                {
                    label: 'Refactored',
                    data: refactored,
                    borderColor: '#22c55e',
                    backgroundColor: 'rgba(34,197,94,0.08)',
                    fill: true,
                    tension: 0.4,
                    pointBackgroundColor: '#22c55e',
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { labels: { color: '#94a3b8' } } },
            scales: {
                x: { grid: { color: 'rgba(255,255,255,0.04)' }, ticks: { color: '#64748b' } },
                y: { grid: { color: 'rgba(255,255,255,0.04)' }, ticks: { color: '#64748b' }, beginAtZero: true }
            }
        }
    });

    const badge = document.getElementById('badge-history');
    badge.textContent = `${sprints.length} sprints`;
}

// ─── Technical Debt Accumulation ─────────────────────────────────────────────
function renderDebtChart(sprints) {
    const labels = sprints.map(s => s.sprint_id);
    let cumSmells = 0, cumFixed = 0;
    const netDebt = sprints.map(s => {
        cumSmells += s.smell_count;
        cumFixed += s.refactor_count;
        return cumSmells - cumFixed;
    });

    const ctx = document.getElementById('chart-debt').getContext('2d');
    if (debtChart) debtChart.destroy();

    debtChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels,
            datasets: [{
                label: 'Net Technical Debt (smells)',
                data: netDebt,
                backgroundColor: netDebt.map(v =>
                    v > 20 ? 'rgba(239,68,68,0.7)' : v > 10 ? 'rgba(245,158,11,0.7)' : 'rgba(34,197,94,0.7)'
                ),
                borderRadius: 6,
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { labels: { color: '#94a3b8' } } },
            scales: {
                x: { grid: { color: 'rgba(255,255,255,0.04)' }, ticks: { color: '#64748b' } },
                y: { grid: { color: 'rgba(255,255,255,0.04)' }, ticks: { color: '#64748b' }, beginAtZero: true }
            }
        }
    });
}

// ─── Sprint Table ─────────────────────────────────────────────────────────────
function renderSprintTable(sprints) {
    const tbody = document.getElementById('sprint-tbody');
    if (!sprints.length) {
        tbody.innerHTML = '<tr><td colspan="5" class="empty-row">No sprint data. Click "+ Log Sprint".</td></tr>';
        return;
    }
    tbody.innerHTML = sprints.map(s => {
        const net = s.smell_count - s.refactor_count;
        const cls = net > 15 ? 'status-danger' : net > 8 ? 'status-warn' : 'status-ok';
        const emoji = net > 15 ? '🔴' : net > 8 ? '🟡' : '🟢';
        return `
      <tr>
        <td>${s.sprint_id}</td>
        <td>${s.smell_count}</td>
        <td>${s.refactor_count}</td>
        <td class="${cls}">${net >= 0 ? '+' : ''}${net}</td>
        <td>${emoji}</td>
      </tr>`;
    }).join('');
}

// ─── Risk Gauge ───────────────────────────────────────────────────────────────
async function runRiskPrediction() {
    try {
        const analytics = await fetch(`${BACKEND}/sprint-analytics`).then(r => r.json());
        const history = analytics.sprints.map(s => s.smell_count);
        const refHist = analytics.sprints.map(s => s.refactor_count);
        if (history.length < 2) return;

        const res = await fetch(`${BACKEND}/predict-sprint-risk`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ sprint_history: history, refactor_history: refHist, threshold: 10 })
        });
        const risk = await res.json();
        renderRiskGauge(risk);
    } catch (e) {
        console.warn('Risk prediction failed', e.message);
        renderRiskGauge({ risk_probability: 0.42, predicted_smell_count: 7, threshold: 10, trend: 'stable', recommendation: '✅ Stable quality.' });
    }
}

function renderRiskGauge(risk) {
    const prob = risk.risk_probability;
    const pct = Math.round(prob * 100);
    const ctx = document.getElementById('chart-risk').getContext('2d');
    if (riskChart) riskChart.destroy();

    const color = prob > 0.7 ? '#ef4444' : prob > 0.4 ? '#f59e0b' : '#22c55e';

    riskChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            datasets: [{
                data: [prob, 1 - prob],
                backgroundColor: [color, 'rgba(255,255,255,0.05)'],
                borderWidth: 0,
                circumference: 270,
                rotation: -135,
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            cutout: '78%',
            plugins: { legend: { display: false }, tooltip: { enabled: false } }
        }
    });

    setText('risk-percent', `${pct}%`);
    document.getElementById('risk-percent').style.color = color;
    setText('risk-predicted', Math.round(risk.predicted_smell_count));
    setText('risk-threshold', risk.threshold);
    setText('risk-trend', risk.trend.replace(/_/g, ' '));
    setText('risk-recommendation', risk.recommendation);
}

// ─── Quick Smell Analysis ─────────────────────────────────────────────────────
async function analyzeCode() {
    const code = document.getElementById('code-input').value;
    if (!code.trim()) return;

    const container = document.getElementById('smell-results');
    container.innerHTML = '<p style="color:#64748b;font-size:.85rem">Analysing…</p>';
    container.classList.remove('hidden');

    try {
        const res = await fetch(`${BACKEND}/analyze-smells`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ code, language: 'python' })
        });
        if (!res.ok) {
            const errText = await res.text();
            let errMsg = `HTTP ${res.status}`;
            try { errMsg = JSON.parse(errText).detail || errMsg; } catch (e) { }
            throw new Error(errMsg);
        }
        const data = await res.json();

        if (!data.smells || data.smells.length === 0) {
            container.innerHTML = '<p style="color:#22c55e">✅ No smells detected!</p>';
            return;
        }

        container.innerHTML = data.smells.map(s => {
            const pct = Math.round(s.confidence * 100);
            const barColor = pct > 75 ? '#ef4444' : pct > 50 ? '#f59e0b' : '#6c63ff';
            return `
        <div class="smell-item">
          <span class="smell-name">${s.display_name}</span>
          <span class="smell-loc">Line ${s.start_line}</span>
          <div class="smell-bar-wrap">
            <div class="smell-bar" style="width:${pct}%;background:${barColor}"></div>
          </div>
          <span class="smell-conf" style="color:${barColor}">${pct}%</span>
        </div>`;
        }).join('');

    } catch (e) {
        container.innerHTML = `<p style="color:#ef4444">❌ ${e.message}. Make sure the backend is running.</p>`;
    }
}

// ─── Log Sprint Modal ─────────────────────────────────────────────────────────
function openLogModal() {
    document.getElementById('modal-overlay').classList.remove('hidden');
    document.getElementById('modal-msg').textContent = '';
}
function closeModal() {
    document.getElementById('modal-overlay').classList.add('hidden');
}

async function logSprint() {
    const sprint_id = document.getElementById('m-sprint-id').value.trim() || `Sprint-${Date.now()}`;
    const smell_count = parseInt(document.getElementById('m-smell-count').value) || 0;
    const refactor_count = parseInt(document.getElementById('m-refactor-count').value) || 0;
    const module = document.getElementById('m-module').value.trim() || 'default';
    const msg = document.getElementById('modal-msg');

    try {
        const res = await fetch(`${BACKEND}/log-sprint`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ sprint_id, smell_count, refactor_count, module })
        });
        if (!res.ok) throw new Error(await res.text());
        msg.textContent = '✅ Sprint logged!';
        msg.style.color = '#22c55e';
        setTimeout(() => { closeModal(); loadData(); }, 800);
    } catch (e) {
        msg.textContent = `❌ Error: ${e.message}`;
        msg.style.color = '#ef4444';
    }
}

// ─── Demo seed (so charts are never empty on first load) ─────────────────────
function seedDemoData() {
    const demoSprints = [
        { sprint_id: 'Sprint-1', smell_count: 5, refactor_count: 2, module: 'demo' },
        { sprint_id: 'Sprint-2', smell_count: 8, refactor_count: 3, module: 'demo' },
        { sprint_id: 'Sprint-3', smell_count: 12, refactor_count: 5, module: 'demo' },
        { sprint_id: 'Sprint-4', smell_count: 9, refactor_count: 6, module: 'demo' },
        { sprint_id: 'Sprint-5', smell_count: 14, refactor_count: 4, module: 'demo' },
    ];
    const summary = {
        total_sprints: 5,
        total_smells_detected: 48,
        total_refactored: 20,
        average_smell_per_sprint: 9.6,
        trend: 'increasing'
    };
    renderSummaryCards(summary);
    renderHistoryChart(demoSprints);
    renderDebtChart(demoSprints);
    renderSprintTable(demoSprints);
    renderRiskGauge({ risk_probability: 0.61, predicted_smell_count: 13, threshold: 10, trend: 'increasing', recommendation: '⚠️ WARNING: Smells trending upward. Include refactoring in next sprint.' });
}

// ─── Utility ──────────────────────────────────────────────────────────────────
function setText(id, val) {
    const el = document.getElementById(id);
    if (el) el.textContent = val;
}
