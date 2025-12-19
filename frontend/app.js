let barChart = null;
let scatterChart = null;

const API_BASE = "http://127.0.0.1:8000/asteroids";

function buildApiUrl(startDate, endDate) {
  const params = new URLSearchParams({
    start_date: startDate,
    end_date: endDate
  });
  return `${API_BASE}?${params.toString()}`;
}

async function loadData() {
  const thresholdInput = document.getElementById("threshold");
  const thresholdValue = document.getElementById("thresholdValue");
  const threshold = Number(thresholdInput.value);
  thresholdValue.textContent = threshold;

  const startDate = document.getElementById("startDate").value;
  const endDate = document.getElementById("endDate").value;

  const url = buildApiUrl(startDate, endDate);

  const response = await fetch(url);
  const data = await response.json();

  // --------------------
  // TABLE
  // --------------------
  const tableBody = document.getElementById("table-body");
  tableBody.innerHTML = "";

  data.forEach(ast => {
    const row = document.createElement("tr");

    row.style.backgroundColor =
      ast.pair_risk_score >= threshold ? "#ffcccc" : "#e6fffa";

    row.innerHTML = `
      <td>${ast.name}</td>
      <td>${ast.pair_risk_score}</td>
      <td>${ast.hazardous}</td>
    `;

    tableBody.appendChild(row);
  });

  // --------------------
  // BAR CHART
  // --------------------
  const barCtx = document.getElementById("riskChart").getContext("2d");

  const names = data.map(a => a.name);
  const risks = data.map(a => a.pair_risk_score);

  if (barChart) barChart.destroy();

  barChart = new Chart(barCtx, {
    type: "bar",
    data: {
      labels: names,
      datasets: [{
        label: "PAIR Risk Score",
        data: risks,
        backgroundColor: risks.map(r =>
          r >= 70 ? "#dc3545" :
          r >= 40 ? "#ffc107" :
                    "#20c997"
        )
      }]
    },
    options: {
      responsive: true,
      scales: {
        y: { beginAtZero: true }
      }
    }
  });

  // --------------------
  // SCATTER PLOT
  // --------------------
  const scatterCtx = document.getElementById("scatterChart").getContext("2d");

  const scatterData = data.map(ast => ({
    x: ast.pair_components.impact_probability,
    y: ast.pair_components.impact_severity
  }));

  if (scatterChart) scatterChart.destroy();

  scatterChart = new Chart(scatterCtx, {
    type: "scatter",
    data: {
      datasets: [{
        label: "Asteroids",
        data: scatterData,
        backgroundColor: data.map(ast =>
          ast.pair_risk_score >= 70 ? "#dc3545" :
          ast.pair_risk_score >= 40 ? "#ffc107" :
                                      "#20c997"
        )
      }]
    },
    options: {
      scales: {
        y: {
          type: "logarithmic"
        }
      }
    }
  });
}

// Events
document.getElementById("threshold").addEventListener("input", loadData);
document.getElementById("loadBtn").addEventListener("click", loadData);

document.getElementById("threeBtn").addEventListener("click", () => {
  const startDate = document.getElementById("startDate").value;
  const endDate = document.getElementById("endDate").value;

  const params = new URLSearchParams({
    start_date: startDate,
    end_date: endDate
  });

  window.location.href = `three.html?${params.toString()}`;
});
