alert("app.js loaded successfully");

const API = window.location.origin;


/* ================= AUTH ================= */
function authHeaders() {
  return {
    "Content-Type": "application/json",
    "Authorization": "Bearer " + localStorage.getItem("token")
  };
}

function logout() {
  localStorage.removeItem("token");
  window.location.href = "index.html";
}

/* ================= DASHBOARD ================= */
function loadSummary() {
  fetch(`${API}/net-balance`, { headers: authHeaders() })
    .then(res => res.json())
    .then(data => {
      const income = Number(data.total_income || 0);
      const expenses = Number(data.total_expenses || 0);
      const balance = Number(data.net_balance || 0);

      document.getElementById("totalIncome").innerText = `GHS ${income.toLocaleString()}`;
      document.getElementById("totalExpenses").innerText = `GHS ${expenses.toLocaleString()}`;
      document.getElementById("netBalance").innerText = `GHS ${balance.toLocaleString()}`;

      drawBarChart(income, expenses);
    });
}

let barChart;
function drawBarChart(income, expenses) {
  const ctx = document.getElementById("barChart");
  if (!ctx) return;

  if (barChart) barChart.destroy();

  barChart = new Chart(ctx, {
    type: "bar",
    data: {
      labels: ["Income", "Expenses"],
      datasets: [{
        data: [income, expenses],
        backgroundColor: ["#1cc88a", "#e74a3b"]
      }]
    },
    options: { responsive: true }
  });
}

/* ================= EXPENSES ================= */
ffunction addExpense() {
  const description = document.getElementById("exp_desc").value;
  const category = document.getElementById("exp_category").value;
  const amount = Number(document.getElementById("exp_amount").value);

  if (!description || !amount) {
    alert("Please enter description and amount");
    return;
  }

  fetch(`${API}/expenses`, {
    method: "POST",
    headers: authHeaders(),
    body: JSON.stringify({
      description,
      category,
      amount,
      date: new Date().toISOString().slice(0, 10)
    })
  })
  .then(async res => {
    if (!res.ok) {
      const err = await res.text();
      throw new Error(err);
    }
    return res.json();
  })
  .then(() => {
    document.getElementById("exp_desc").value = "";
    document.getElementById("exp_amount").value = "";

    loadCategoryChart();
    loadSummary();
  })
  .catch(err => alert("Expense error: " + err.message));
}



function loadCategoryChart(canvasId = "categoryChart") {
  fetch(`${API}/expenses-by-category`, { headers: authHeaders() })
    .then(res => res.json())
    .then(data => {
      const ctx = document.getElementById(canvasId);
      if (!ctx) return;

      new Chart(ctx, {
        type: "pie",
        data: {
          labels: data.map(d => d.category),
          datasets: [{
            data: data.map(d => d.total),
            backgroundColor: [
              "#4e73df",
              "#1cc88a",
              "#36b9cc",
              "#f6c23e",
              "#e74a3b",
              "#858796"
            ]
          }]
        }
      });
    });
}

/* ================= BUDGET ================= */
function setBudget() {
  const month = document.getElementById("budget_month").value;
  const amount = Number(document.getElementById("budget_amount").value);

  if (!month || !amount) {
    alert("Please enter month and budget amount");
    return;
  }

  fetch(`${API}/budget`, {
    method: "POST",
    headers: authHeaders(),
    body: JSON.stringify({
      month,
      amount
    })
  })
  .then(async res => {
    if (!res.ok) {
      const err = await res.text();
      throw new Error(err);
    }
    return res.json();
  })
  .then(() => loadBudget(month))
  .catch(err => alert("Budget error: " + err.message));
}



function loadBudget(month) {
  fetch(`${API}/budget-status/${month}`, { headers: authHeaders() })
    .then(res => res.json())
    .then(data => {
      const budget = Number(data.budget || 0);
      const spent = Number(data.spent || 0);
      const remaining = Math.max(budget - spent, 0);
      const percent = budget ? Math.min((spent / budget) * 100, 100) : 0;

      const bar = document.getElementById("budgetProgress");
      if (!bar) return;

      bar.style.width = percent + "%";
      bar.innerText = Math.round(percent) + "%";
      bar.className = "progress-bar " +
        (percent < 70 ? "bg-success" : percent < 90 ? "bg-warning" : "bg-danger");

      document.getElementById("budgetUsed").innerText = `Used: GHS ${spent.toLocaleString()}`;
      document.getElementById("budgetRemaining").innerText = `Remaining: GHS ${remaining.toLocaleString()}`;
    });
}

/* ================= DARK MODE ================= */
function toggleDarkMode() {
  document.body.classList.toggle("dark");
  localStorage.setItem("darkMode", document.body.classList.contains("dark"));
}

/* ================= INIT ================= */
document.addEventListener("DOMContentLoaded", () => {
  if (localStorage.getItem("darkMode") === "true") {
    document.body.classList.add("dark");
  }

  if (localStorage.getItem("token")) {
    if (window.location.pathname.includes("dashboard")) {
      loadSummary();
    }

    if (window.location.pathname.includes("expenses")) {
      loadCategoryChart();
    }

    if (window.location.pathname.includes("budget")) {
      const month = new Date().toISOString().slice(0, 7);
      document.getElementById("budget_month").value = month;
      loadBudget(month);
    }
  }
});
