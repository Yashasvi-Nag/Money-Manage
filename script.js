const BASELINE_BALANCE = 240000;
const BAR_SPACING_MULTIPLIER = 2.2;
const BAR_GAP = 8;
const DONUT_INNER_RADIUS_RATIO = 0.55;

const monthlyData = [
  { month: "Oct", income: 51000, expenses: 33200, savings: 17800 },
  { month: "Nov", income: 52500, expenses: 34500, savings: 18000 },
  { month: "Dec", income: 54000, expenses: 36000, savings: 18000 },
  { month: "Jan", income: 55800, expenses: 36800, savings: 19000 },
  { month: "Feb", income: 56500, expenses: 35200, savings: 21300 },
  { month: "Mar", income: 57900, expenses: 36150, savings: 21750 },
];

const spendingCategories = [
  { label: "Housing", value: 11800, color: "#7c5dff" },
  { label: "Food", value: 6400, color: "#22d3ee" },
  { label: "Transport", value: 3400, color: "#fb7185" },
  { label: "Wellness", value: 2800, color: "#34d399" },
  { label: "Subscriptions", value: 2100, color: "#f59e0b" },
  { label: "Misc", value: 2400, color: "#9ca3af" },
];

const budgets = [
  { name: "Housing", spent: 11800, limit: 15000 },
  { name: "Food & Dining", spent: 6400, limit: 7500 },
  { name: "Transport", spent: 3400, limit: 4000 },
  { name: "Lifestyle", spent: 5200, limit: 7000 },
];

const goals = [
  { name: "Emergency fund", current: 68000, target: 100000 },
  { name: "Vacation", current: 24000, target: 35000 },
  { name: "Student loan", current: 52000, target: 80000 },
];

const transactions = [
  { name: "Rent", category: "Housing", date: "Mar 05", amount: -11800 },
  { name: "Salary", category: "Income", date: "Mar 01", amount: 57900 },
  { name: "Groceries", category: "Food", date: "Mar 12", amount: -1420 },
  { name: "Gym membership", category: "Wellness", date: "Mar 02", amount: -480 },
  { name: "Internet", category: "Utilities", date: "Mar 07", amount: -650 },
  { name: "Coffee shop", category: "Lifestyle", date: "Mar 10", amount: -180 },
  { name: "Ride share", category: "Transport", date: "Mar 11", amount: -220 },
];

const insights = [
  "You’re pacing to save 26% of income this month.",
  "Dining out is 12% lower than last month—keep it up!",
  "Housing is under 80% of budget with 10 days left.",
  "Subscriptions are stable; consider cancelling unused trials.",
];

const currency = new Intl.NumberFormat("en-IN", {
  style: "currency",
  currency: "INR",
  maximumFractionDigits: 0,
});

function formatCurrency(value) {
  return currency.format(value);
}

function updateSummary(monthKey) {
  const month = monthlyData.find((m) => m.month === monthKey) || monthlyData.at(-1);
  const balance = month.income - month.expenses + BASELINE_BALANCE;
  document.getElementById("balanceValue").textContent = formatCurrency(balance);
  document.getElementById("incomeValue").textContent = formatCurrency(month.income);
  document.getElementById("expenseValue").textContent = formatCurrency(month.expenses);
  const rate = Math.round((month.savings / month.income) * 100);
  document.getElementById("savingsRate").textContent = `${rate}%`;
}

function renderBudgets() {
  const container = document.getElementById("budgetList");
  container.innerHTML = "";
  budgets.forEach((budget) => {
    const usage = Math.min(100, Math.round((budget.spent / budget.limit) * 100));
    const pillClass = usage > 90 ? "danger" : usage > 75 ? "warning" : "success";
    const row = document.createElement("div");
    row.className = "budget-row";
    row.innerHTML = `
      <div class="budget-top">
        <div>
          <div class="label">${budget.name}</div>
          <strong>${formatCurrency(budget.spent)}</strong>
          <span class="muted"> / ${formatCurrency(budget.limit)}</span>
        </div>
        <span class="pill ${pillClass}">${usage}% used</span>
      </div>
      <div class="progress" aria-label="Budget progress for ${budget.name}">
        <div style="width:${usage}%"></div>
      </div>
    `;
    container.appendChild(row);
  });
}

function renderGoals() {
  const container = document.getElementById("goalsList");
  container.innerHTML = "";
  goals.forEach((goal) => {
    const progress = Math.min(100, Math.round((goal.current / goal.target) * 100));
    const row = document.createElement("div");
    row.className = "goal-row";
    row.innerHTML = `
      <div class="goal-top">
        <div>
          <div class="label">${goal.name}</div>
          <strong>${formatCurrency(goal.current)}</strong>
          <span class="muted"> of ${formatCurrency(goal.target)}</span>
        </div>
        <span class="pill success">${progress}%</span>
      </div>
      <div class="progress" aria-label="Goal progress for ${goal.name}">
        <div style="width:${progress}%"></div>
      </div>
    `;
    container.appendChild(row);
  });
}

function renderActivity() {
  const list = document.getElementById("activityList");
  list.innerHTML = "";
  transactions.forEach((item) => {
    const li = document.createElement("li");
    const amountClass = item.amount >= 0 ? "income" : "expense";
    const amountText =
      item.amount >= 0
        ? `+${formatCurrency(item.amount)}`
        : formatCurrency(item.amount);
    li.innerHTML = `
      <div>
        <div><strong>${item.name}</strong></div>
        <div class="meta">${item.category} • ${item.date}</div>
      </div>
      <div class="amount ${amountClass}">${amountText}</div>
    `;
    list.appendChild(li);
  });
}

function renderInsights() {
  const list = document.getElementById("insightsList");
  list.innerHTML = "";
  insights.forEach((tip) => {
    const li = document.createElement("li");
    li.textContent = tip;
    list.appendChild(li);
  });
}

function renderSpendingLegend() {
  const legend = document.getElementById("spendingLegend");
  legend.innerHTML = "";
  const total = spendingCategories.reduce((sum, c) => sum + c.value, 0);
  spendingCategories.forEach((cat) => {
    const percent = ((cat.value / total) * 100).toFixed(1);
    const item = document.createElement("li");
    item.innerHTML = `
      <span class="swatch" style="background:${cat.color}"></span>
      <div>
        <div><strong>${cat.label}</strong></div>
        <div class="meta">${formatCurrency(cat.value)} • ${percent}%</div>
      </div>
    `;
    legend.appendChild(item);
  });
}

function setupMonthSelect() {
  const select = document.getElementById("monthSelect");
  monthlyData.forEach((m) => {
    const option = document.createElement("option");
    option.value = m.month;
    option.textContent = m.month;
    select.appendChild(option);
  });
  select.value = monthlyData.at(-1).month;
  select.addEventListener("change", (evt) => {
    updateSummary(evt.target.value);
  });
}

function drawCashflowChart() {
  const canvas = document.getElementById("cashflowChart");
  const ctx = canvas.getContext("2d");
  const dpr = window.devicePixelRatio || 1;
  const width = canvas.clientWidth || 600;
  const rawHeight = canvas.getAttribute("height");
  const height = rawHeight ? parseInt(rawHeight, 10) : canvas.clientHeight || 260;
  canvas.width = width * dpr;
  canvas.height = height * dpr;
  ctx.scale(dpr, dpr);

  ctx.clearRect(0, 0, width, height);
  const maxValue = Math.max(
    ...monthlyData.map((m) => Math.max(m.income, m.expenses))
  );

  const padding = 40;
  const chartHeight = height - padding * 2;
  const chartWidth = width - padding * 2;
  const barWidth = chartWidth / (monthlyData.length * 2);

  ctx.strokeStyle = "rgba(255,255,255,0.1)";
  ctx.lineWidth = 1;
  ctx.beginPath();
  ctx.moveTo(padding, height - padding);
  ctx.lineTo(width - padding, height - padding);
  ctx.stroke();

  monthlyData.forEach((item, index) => {
    const incomeHeight = (item.income / maxValue) * chartHeight;
    const expenseHeight = (item.expenses / maxValue) * chartHeight;
    const baseX = padding + index * (barWidth * BAR_SPACING_MULTIPLIER);

    ctx.fillStyle = "rgba(45, 212, 191, 0.85)";
    ctx.fillRect(
      baseX,
      height - padding - incomeHeight,
      barWidth,
      incomeHeight
    );

    ctx.fillStyle = "rgba(244, 63, 94, 0.8)";
    ctx.fillRect(
      baseX + barWidth + BAR_GAP,
      height - padding - expenseHeight,
      barWidth,
      expenseHeight
    );

    ctx.fillStyle = "rgba(255,255,255,0.75)";
    ctx.font = "12px Inter, sans-serif";
    ctx.textAlign = "center";
    ctx.fillText(item.month, baseX + barWidth, height - padding + 16);
  });
}

function drawSpendingChart() {
  const canvas = document.getElementById("spendingChart");
  const ctx = canvas.getContext("2d");
  const dpr = window.devicePixelRatio || 1;
  const width = canvas.clientWidth || 320;
  const rawHeight = canvas.getAttribute("height");
  const height = rawHeight ? parseInt(rawHeight, 10) : canvas.clientHeight || 240;
  canvas.width = width * dpr;
  canvas.height = height * dpr;
  ctx.scale(dpr, dpr);

  ctx.clearRect(0, 0, width, height);
  const total = spendingCategories.reduce((sum, c) => sum + c.value, 0);
  let startAngle = -Math.PI / 2;
  const centerX = width / 2;
  const centerY = height / 2;
  const radius = Math.min(width, height) / 2.4;

  spendingCategories.forEach((cat) => {
    const sliceAngle = (cat.value / total) * Math.PI * 2;
    ctx.beginPath();
    ctx.moveTo(centerX, centerY);
    ctx.arc(centerX, centerY, radius, startAngle, startAngle + sliceAngle);
    ctx.closePath();
    ctx.fillStyle = cat.color;
    ctx.fill();
    startAngle += sliceAngle;
  });

  ctx.globalCompositeOperation = "destination-out";
  ctx.beginPath();
  ctx.arc(centerX, centerY, radius * DONUT_INNER_RADIUS_RATIO, 0, Math.PI * 2);
  ctx.fill();
  ctx.globalCompositeOperation = "source-over";

  ctx.fillStyle = "#e5e7eb";
  ctx.font = "700 18px Inter, sans-serif";
  ctx.textAlign = "center";
  ctx.fillText("Spend", centerX, centerY - 4);
  ctx.fillStyle = "#9ca3af";
  ctx.font = "12px Inter, sans-serif";
  ctx.fillText("this month", centerX, centerY + 14);
}

function init() {
  setupMonthSelect();
  updateSummary(monthlyData.at(-1).month);
  renderBudgets();
  renderGoals();
  renderActivity();
  renderInsights();
  renderSpendingLegend();
  drawCashflowChart();
  drawSpendingChart();
}

document.addEventListener("DOMContentLoaded", init);
