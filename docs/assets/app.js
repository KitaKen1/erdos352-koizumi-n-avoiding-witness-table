(function () {
  const data = window.WITNESS_DATA;
  const rows = data.rows.slice().sort((a, b) => a.N - b.N);
  const byN = new Map(rows.map((row) => [row.N, row]));
  let currentN = readNFromHash() || 28;

  const nSelect = document.getElementById("nSelect");
  const nGrid = document.getElementById("nGrid");
  const title = document.getElementById("title");
  const stats = document.getElementById("stats");
  const plot = document.getElementById("plot");
  const pointText = document.getElementById("pointText");
  const verifyList = document.getElementById("verifyList");
  const showLabels = document.getElementById("showLabels");

  function readNFromHash() {
    const match = location.hash.match(/n=(\d+)/i);
    return match ? Number(match[1]) : null;
  }

  function pointString(row) {
    return row.points.map(([x, y]) => `${x},${y}`).join(" ");
  }

  function formatNumber(value) {
    return Number(value).toLocaleString("en-US");
  }

  function escapeHTML(value) {
    return String(value ?? "").replace(/[&<>"']/g, (char) => {
      return {
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        '"': "&quot;",
        "'": "&#39;",
      }[char];
    });
  }

  function makeStat(label, value) {
    return `<div class="stat"><span>${label}</span><strong>${value}</strong></div>`;
  }

  function setN(n, updateHash = true) {
    if (!byN.has(n)) {
      n = rows[0].N;
    }
    currentN = n;
    if (updateHash) {
      history.replaceState(null, "", `#n=${n}`);
    }
    render();
  }

  function renderSelector() {
    nSelect.innerHTML = rows
      .map((row) => `<option value="${row.N}">N=${row.N}, |S|=${row.size}</option>`)
      .join("");

    nGrid.innerHTML = rows
      .map(
        (row) => `
          <button class="n-button" type="button" data-n="${row.N}">
            <strong>${row.N}</strong>
            <span>${row.size}</span>
          </button>
        `
      )
      .join("");

    nSelect.addEventListener("change", () => setN(Number(nSelect.value)));
    nGrid.addEventListener("click", (event) => {
      const button = event.target.closest("[data-n]");
      if (button) setN(Number(button.dataset.n));
    });
  }

  function renderPlot(row) {
    const xs = row.points.map((p) => p[0]);
    const ys = row.points.map((p) => p[1]);
    const minX = Math.min(...xs);
    const maxX = Math.max(...xs);
    const minY = Math.min(...ys);
    const maxY = Math.max(...ys);
    const width = 900;
    const height = 560;
    const pad = 58;
    const spanX = Math.max(1, maxX - minX);
    const spanY = Math.max(1, maxY - minY);
    const sx = (width - pad * 2) / spanX;
    const sy = (height - pad * 2) / spanY;
    const scale = Math.min(sx, sy);
    const plotW = spanX * scale;
    const plotH = spanY * scale;
    const ox = (width - plotW) / 2;
    const oy = (height - plotH) / 2;
    const labelsOn = showLabels.checked && row.size <= 80;

    const px = (x) => ox + (x - minX) * scale;
    const py = (y) => height - (oy + (y - minY) * scale);

    const grid = [];
    for (let x = minX; x <= maxX; x += 1) {
      grid.push(`<line class="grid-line" x1="${px(x)}" y1="${oy}" x2="${px(x)}" y2="${height - oy}"></line>`);
      grid.push(`<text class="axis-label" x="${px(x)}" y="${height - oy + 22}" text-anchor="middle">${x}</text>`);
    }
    for (let y = minY; y <= maxY; y += 1) {
      grid.push(`<line class="grid-line" x1="${ox}" y1="${py(y)}" x2="${width - ox}" y2="${py(y)}"></line>`);
      grid.push(`<text class="axis-label" x="${ox - 16}" y="${py(y) + 4}" text-anchor="end">${y}</text>`);
    }

    const radius = Math.max(4, Math.min(7, 32 / Math.sqrt(row.size)));
    const points = row.points
      .map(([x, y], index) => {
        const label = labelsOn
          ? `<text class="point-label" x="${px(x) + radius + 3}" y="${py(y) - radius - 2}">${index + 1}</text>`
          : "";
        return `
          <g>
            <circle class="point" cx="${px(x)}" cy="${py(y)}" r="${radius}">
              <title>(${x}, ${y})</title>
            </circle>
            ${label}
          </g>
        `;
      })
      .join("");

    plot.setAttribute("viewBox", `0 0 ${width} ${height}`);
    plot.innerHTML = `${grid.join("")}${points}`;
  }

  function renderDetails(row) {
    const v = row.verification;
    const source = row.source || {};
    const sourceName = [source.author, source.method].filter(Boolean).join(" / ") || "unknown";
    const sourceReference = source.reference || source.local_experiment_file || "";
    const sourceURL = source.url || "";
    const sourceReferenceHTML = sourceURL
      ? `<a href="${escapeHTML(sourceURL)}" target="_blank" rel="noopener">${escapeHTML(sourceReference || sourceURL)}</a>`
      : escapeHTML(sourceReference || "unknown");
    title.textContent = `N=${row.N}, |S|=${row.size}`;
    stats.innerHTML = [
      makeStat("lower bound", row.size),
      makeStat("min_gap", formatNumber(v.min_margin_squared_numerator)),
      makeStat("triples checked", formatNumber(v.triple_count_with_repetition)),
      makeStat("max D2", formatNumber(v.max_diameter_squared)),
      makeStat("max A2", formatNumber(v.max_twice_area)),
    ].join("");

    pointText.textContent = pointString(row);
    verifyList.innerHTML = `
      <dt>sha256</dt><dd>${row.points_sha256.slice(0, 16)}...</dd>
      <dt>source</dt><dd>${escapeHTML(sourceName)}</dd>
      <dt>reference</dt><dd>${sourceReferenceHTML}</dd>
      <dt>file</dt><dd>${row.witness_file}</dd>
      <dt>claim</dt><dd>${row.claim}</dd>
      <dt>model</dt><dd>${data.model}</dd>
    `;
  }

  function render() {
    const row = byN.get(currentN);
    nSelect.value = String(currentN);
    document.querySelectorAll(".n-button").forEach((button) => {
      button.classList.toggle("active", Number(button.dataset.n) === currentN);
    });
    renderDetails(row);
    renderPlot(row);
  }

  function step(delta) {
    const index = rows.findIndex((row) => row.N === currentN);
    const next = rows[Math.max(0, Math.min(rows.length - 1, index + delta))];
    setN(next.N);
  }

  document.getElementById("prevN").addEventListener("click", () => step(-1));
  document.getElementById("nextN").addEventListener("click", () => step(1));
  showLabels.addEventListener("change", render);
  document.getElementById("copyPoints").addEventListener("click", async () => {
    const row = byN.get(currentN);
    await navigator.clipboard.writeText(pointString(row));
  });
  document.getElementById("downloadJson").addEventListener("click", () => {
    const row = byN.get(currentN);
    const blob = new Blob([JSON.stringify(row, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `n${String(row.N).padStart(3, "0")}_${row.size}.json`;
    a.click();
    URL.revokeObjectURL(url);
  });
  window.addEventListener("hashchange", () => {
    const n = readNFromHash();
    if (n && byN.has(n)) setN(n, false);
  });

  renderSelector();
  setN(currentN, false);
})();
