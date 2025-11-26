const statusEl = document.getElementById('status');
const pgnInput = document.getElementById('pgn-input');
const urlInput = document.getElementById('url-input');
const analyseBtn = document.getElementById('analyse-btn');
const resultsSection = document.getElementById('results');
const summaryTableBody = document.querySelector('#summary-table tbody');

analyseBtn.addEventListener('click', async () => {
    statusEl.textContent = 'Analysing...';
    analyseBtn.disabled = true;

    try {
        const payload = {
            pgn: pgnInput.value.trim() || undefined,
            url: urlInput.value.trim() || undefined,
        };

        const res = await fetch('/analyse', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload),
        });

        if (!res.ok) {
            const err = await res.json();
            throw new Error(err.detail || 'Request failed');
        }

        const data = await res.json();
        renderResults(data);
        statusEl.textContent = 'Done';
    } catch (err) {
        console.error(err);
        statusEl.textContent = err.message;
    } finally {
        analyseBtn.disabled = false;
    }
});

function renderResults(data) {
    resultsSection.classList.remove('hidden');
    document.getElementById('white-name').textContent = data.white.name;
    document.getElementById('black-name').textContent = data.black.name;
    document.getElementById('white-accuracy').textContent = data.white.accuracy;
    document.getElementById('black-accuracy').textContent = data.black.accuracy;

    buildTable(data.white.move_counts, data.black.move_counts);
    drawGraph(data.evaluations);
}

function buildTable(whiteCounts, blackCounts) {
    const labels = [
        'Brilliant', 'Great', 'Best', 'Excellent', 'Good',
        'Book', 'Inaccuracy', 'Mistake', 'Miss', 'Blunder'
    ];

    summaryTableBody.innerHTML = '';
    labels.forEach(label => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${label}</td>
            <td>${whiteCounts[label] || 0}</td>
            <td>${blackCounts[label] || 0}</td>
        `;
        summaryTableBody.appendChild(row);
    });
}

function drawGraph(evals) {
    const graph = document.getElementById('graph');
    graph.innerHTML = '';
    if (!evals.length) return;

    const width = graph.clientWidth || 800;
    const height = graph.clientHeight || 180;
    const maxAbs = Math.max(...evals.map(e => Math.abs(e)), 1);
    const points = evals.map((v, i) => {
        const x = (i / Math.max(evals.length - 1, 1)) * width;
        const y = height / 2 - (v / maxAbs) * (height / 2) * 0.9;
        return `${x},${y}`;
    }).join(' ');

    const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
    svg.setAttribute('width', width);
    svg.setAttribute('height', height);

    const midLine = document.createElementNS('http://www.w3.org/2000/svg', 'line');
    midLine.setAttribute('x1', 0);
    midLine.setAttribute('y1', height / 2);
    midLine.setAttribute('x2', width);
    midLine.setAttribute('y2', height / 2);
    midLine.setAttribute('stroke', '#223227');
    midLine.setAttribute('stroke-width', 1);
    svg.appendChild(midLine);

    const polyline = document.createElementNS('http://www.w3.org/2000/svg', 'polyline');
    polyline.setAttribute('fill', 'none');
    polyline.setAttribute('stroke', '#7ac156');
    polyline.setAttribute('stroke-width', 2);
    polyline.setAttribute('points', points);
    svg.appendChild(polyline);

    graph.appendChild(svg);
}
