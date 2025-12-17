let barChart = null;
let scatterChart = null;

async function loadData() {
  const thresholdInput = document.getElementById("threshold");
  const thresholdValue = document.getElementById("thresholdValue");
  const threshold = Number(thresholdInput.value);
  thresholdValue.textContent = threshold;

  // --------------------
  // FETCH DATA
  // --------------------
  const response = await fetch(
    "http://127.0.0.1:8000/asteroids?start_date=2024-01-01&end_date=2024-01-03"
  );
  const data = await response.json();

  // --------------------
  // TABLE
  // --------------------
  const tableBody = document.getElementById("table-body");
  tableBody.innerHTML = "";

  data.forEach(ast => {
    const row = document.createElement("tr");

    if (ast.pair_risk_score >= threshold) {
      row.style.backgroundColor = "#ffcccc";
    } else {
      row.style.backgroundColor = "#e6fffa";
    }

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
        y: {
          beginAtZero: true,
          title: {
            display: true,
            text: "PAIR Risk Score"
          }
        }
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
        x: {
          title: {
            display: true,
            text: "Impact Probability"
          }
        },
        y: {
          type: "logarithmic",
          title: {
            display: true,
            text: "Impact Severity (log scale)"
          }
        }
      }
    }
  });
}

// Slider should re-render everything
document.getElementById("threshold").addEventListener("input", loadData);
