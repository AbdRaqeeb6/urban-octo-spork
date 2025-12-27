<script>
async function refreshAll() {
  // DASHBOARD
  if (typeof loadSummary === "function") loadSummary();
  if (typeof loadChart === "function") loadChart();

  // EXPENSES
  if (typeof loadExpenses === "function") loadExpenses();

  // BUDGET
  if (typeof loadBudget === "function") loadBudget();

  // REPORTS
  if (typeof loadReports === "function") loadReports();
}

/* Auto-refresh when page becomes active */
window.addEventListener("focus", refreshAll);
</script>
