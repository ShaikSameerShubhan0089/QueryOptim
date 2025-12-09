document.addEventListener("DOMContentLoaded", () => {
  const API = "http://127.0.0.1:8000/analyze";

  const sqlEl = document.getElementById("sql");
  const sandboxEl = document.getElementById("sandbox");
  const runBtn = document.getElementById("run");
  const clearBtn = document.getElementById("clear");

  const resultsEl = document.getElementById("results");
  const summaryEl = document.getElementById("summary");
  const optQueryEl = document.getElementById("opt-query");
  const recsEl = document.getElementById("recommendations");
  const warningsEl = document.getElementById("warnings");
  const impactEl = document.getElementById("impact");
  const aiNotesEl = document.getElementById("ai-notes");
  const planEl = document.getElementById("plan");
  const rowsEl = document.getElementById("rows");
  const rawEl = document.getElementById("raw");
  const messageEl = document.getElementById("message");

  runBtn.onclick = async () => {
    messageEl.className = "hidden";
    const sql = sqlEl.value.trim();
    if (!sql) {
      showMessage("Please paste a SQL query.", "error");
      return;
    }
    const run_in_sandbox = sandboxEl.value === "true";

    runBtn.disabled = true;
    runBtn.textContent = "⏳ Running...";

    try {
      const resp = await fetch(API, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ sql, run_in_sandbox })
      });

      if (!resp.ok) {
        const txt = await resp.text();
        showMessage("Server error: " + resp.status + " - " + txt, "error");
        return;
      }

      const data = await resp.json();
      console.log("Response:", data);
      renderResults(data);

    } catch (err) {
      showMessage("Request failed: " + err.message, "error");
    } finally {
      runBtn.disabled = false;
      runBtn.textContent = "▶ Run Analysis";
    }
  };

  clearBtn.onclick = () => {
    sqlEl.value = "";
    resultsEl.className = "hidden";
    summaryEl.textContent = "";
    optQueryEl.textContent = "";
    recsEl.textContent = "";
    warningsEl.textContent = "";
    impactEl.textContent = "";
    aiNotesEl.textContent = "";
    planEl.textContent = "";
    rowsEl.textContent = "";
    rawEl.textContent = "";
    messageEl.className = "hidden";
  };

  function showMessage(text, type = "info") {
    messageEl.textContent = text;
    messageEl.className = type === "error" ? "error" : "info";
    messageEl.classList.remove("hidden");
  }

  function escapeHtml(text) {
    const map = { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#039;' };
    return String(text).replace(/[&<>"']/g, m => map[m]);
  }

  function makeTable(rows) {
    if (!Array.isArray(rows) || rows.length === 0) return "<p>No data</p>";

    const headers = Object.keys(rows[0]);
    let html = "<table border='1' cellpadding='4' cellspacing='0'><thead><tr>";
    headers.forEach(h => html += `<th>${h}</th>`);
    html += "</tr></thead><tbody>";

    rows.forEach(r => {
      html += "<tr>";
      headers.forEach(h => html += `<td>${r[h]}</td>`);
      html += "</tr>";
    });

    html += "</tbody></table>";
    return html;
  }

  function renderResults(data) {
    resultsEl.classList.remove("hidden");

    const db = data.database || data.database_used || "unknown";
    const query = data.original_query || "";
    const summary = data.summary || {};
    const opt = data.optimization || {};
    const cost = data.cost_analysis || {};
    const schema = data.schema_improvements || {};
    const validator = data.data_quality || {};
    const technical = data.technical_details || {};

    summaryEl.innerHTML = `<h3>📊 Analysis Summary</h3>
<p><strong>Database:</strong> ${db}</p>
<p><strong>Performance Impact:</strong> <span class="impact-${(summary.performance_impact || "unknown").toLowerCase()}">${summary.performance_impact || "Unknown"}</span></p>
<p><strong>Key Findings:</strong> ${summary.optimization_reason || "Query analyzed"}</p>`;

    if (opt.status === "success") {
      const optimizedQuery = opt.optimized_query || query;
      optQueryEl.innerHTML = `<strong>Optimized Query:</strong><pre>${escapeHtml(optimizedQuery)}</pre>
<p><strong>Why Faster:</strong> ${opt.why_faster || "See recommendations below"}</p>`;
    } else {
      optQueryEl.innerHTML = "<p>⚠ Optimization analysis in progress</p>";
    }

    if (opt.recommendations && opt.recommendations.length > 0) {
      recsEl.innerHTML = "<strong>💡 Optimization Tips:</strong><ul>" + opt.recommendations.map(r => `<li>${r}</li>`).join("") + "</ul>";
    } else {
      recsEl.innerHTML = "<p>✓ No specific optimizations needed</p>";
    }

    if (opt.warnings && opt.warnings.length > 0) {
      warningsEl.innerHTML = "<strong>⚠ Warnings:</strong><ul>" + opt.warnings.map(w => `<li>${w}</li>`).join("") + "</ul>";
    } else {
      warningsEl.innerHTML = "<p>✓ No issues detected</p>";
    }

    impactEl.innerHTML = `<strong>Impact Level:</strong> ${opt.estimated_impact || "Unknown"}`;
    if (opt.engine_advice && opt.engine_advice.length > 0) {
      impactEl.innerHTML += `<br><strong>🔧 Engine Tips:</strong><ul>${opt.engine_advice.map(a => `<li>${a}</li>`).join("")}</ul>`;
    }

    let aiHTML = "";

    aiHTML += `<h4>💰 Cost Analysis</h4>`;
    if (cost.status === "success") {
      aiHTML += `<p><strong>Estimated Cost:</strong> <strong class="cost-${(cost.estimated_cost || "medium").toLowerCase()}">${cost.estimated_cost || "Medium"}</strong></p>`;
      if (cost.cost_saving_tips && cost.cost_saving_tips.length > 0) {
        aiHTML += `<ul>${cost.cost_saving_tips.map(t => `<li>${t}</li>`).join("")}</ul>`;
      }
      if (cost.warnings && cost.warnings.length > 0) {
        aiHTML += `<p><strong>Warnings:</strong><ul>${cost.warnings.map(w => `<li>${w}</li>`).join("")}</ul></p>`;
      }
    } else {
      aiHTML += `<p>⚠ ${cost.error || "Cost analysis unavailable"}</p>`;
    }

    aiHTML += `<h4>🗄️ Schema Improvements</h4>`;
    if (schema.status === "success") {
      if (schema.recommended_indexes && schema.recommended_indexes.length > 0) {
        aiHTML += `<p><strong>Recommended Indexes:</strong></p><ul>${schema.recommended_indexes.map(idx => `<li><code>${escapeHtml(idx)}</code></li>`).join("")}</ul>`;
      }
      if (schema.schema_changes && schema.schema_changes.length > 0) {
        aiHTML += `<p><strong>Schema Changes:</strong></p><ul>${schema.schema_changes.map(change => `<li>${escapeHtml(change)}</li>`).join("")}</ul>`;
      }
      if (!schema.recommended_indexes && !schema.schema_changes) {
        aiHTML += `<p>✓ Current schema is well-designed</p>`;
      }
    } else if (schema.status === "unsafe") {
      aiHTML += `<p>⚠️ Query contains unsafe operations</p>`;
    } else {
      aiHTML += `<p>⚠ ${schema.error || "Schema analysis unavailable"}</p>`;
    }

    aiHTML += `<h4>✅ Data Quality</h4>`;
    if (validator.status === "success") {
      if (validator.issues && validator.issues.length > 0) {
        aiHTML += `<p><strong>Issues Found (${validator.confidence || "Medium"} confidence):</strong></p><ul>${validator.issues.map(issue => `<li>${issue}</li>`).join("")}</ul>`;
        if (validator.reasoning) aiHTML += `<p><em>${validator.reasoning}</em></p>`;
      } else {
        aiHTML += `<p>✓ Data quality looks good</p>`;
        if (validator.reasoning) aiHTML += `<p><em>${validator.reasoning}</em></p>`;
      }
    } else {
      aiHTML += `<p>⚠ ${validator.error || "Data validation unavailable"}</p>`;
    }

    aiNotesEl.innerHTML = aiHTML;

    if (Array.isArray(technical.explain_plan) && technical.explain_plan.length > 0) {
      planEl.innerHTML = makeTable(technical.explain_plan);
    } else {
      planEl.innerHTML = "<p>⚠ No explain plan available</p>";
    }

    if (technical.sample_rows && technical.sample_rows.rows && technical.sample_rows.rows.length > 0) {
      rowsEl.innerHTML = makeTable(technical.sample_rows.rows);
      if (technical.sample_rows.message) {
        rowsEl.innerHTML += `<p><em>${technical.sample_rows.message}</em></p>`;
      }
    } else if (technical.sample_rows && technical.sample_rows.error) {
      rowsEl.innerHTML = `<p>⚠ ${technical.sample_rows.error}</p>`;
    } else {
      rowsEl.innerHTML = "<p>⚠ No sample data available</p>";
    }

    renderRawJson(technical);
  }

  function renderRawJson(technical) {
    let html = "";

    if (technical.schema_context) {
      html += `<h3>📂 Schema Context</h3>`;
      const schema = technical.schema_context;
      if (typeof schema === "object" && !Array.isArray(schema)) {
        for (const [table, cols] of Object.entries(schema)) {
          html += `<h4>Table: <code>${escapeHtml(table)}</code></h4>`;
          if (Array.isArray(cols)) {
            html += makeTable(cols);
          } else if (cols && typeof cols === "object") {
            html += `<p>${JSON.stringify(cols)}</p>`;
          }
        }
      }
    }

    rawEl.innerHTML = html;
  }

  async function analyzeSchema() {
    const response = await fetch("/analyze-schema", { method: "POST" });
    const data = await response.json();

    const resultDiv = document.getElementById("schema-results");
    resultDiv.innerHTML = `
      <h3>🗄 Schema Overview</h3>
      <pre>${JSON.stringify(data, null, 2)}</pre>
    `;
  }

  window.analyzeSchema = analyzeSchema;
});
