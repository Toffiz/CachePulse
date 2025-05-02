document.addEventListener('DOMContentLoaded', function () {
    const loader = document.getElementById("dashboard-loader");
    const dashboardSection = document.querySelector(".dashboard");
    const dayRangeSelector = document.getElementById("day-range");
    let selectedDays = parseInt(localStorage.getItem("selectedDays") || "30");

    function loadDashboardData(days) {
        if (loader) loader.style.display = "block";
        if (dashboardSection) dashboardSection.style.opacity = 0.3;

        Promise.all([
            fetch("http://127.0.0.1:8000/api/alerts").then(res => res.json()),
            fetch(`http://127.0.0.1:8000/api/chart?days=${days}`).then(res => res.json())
        ])
        .then(([alerts, chart]) => {
            const totalCashIn = chart.cash_in.reduce((a, b) => a + b, 0);
            const totalCashOut = chart.cash_out.reduce((a, b) => a + b, 0);
            const finalCashGap = chart.cash_gap.at(-1) ?? 0;
            const avgOut = totalCashOut / (chart.labels.length || 1);
            const daysCoverage = avgOut > 0 ? Math.floor(finalCashGap / avgOut) : 0;
        
            document.getElementById("cash-in-value").textContent = `KZT ${totalCashIn.toLocaleString()}`;
            document.getElementById("cash-out-value").textContent = `KZT ${totalCashOut.toLocaleString()}`;
            document.getElementById("cash-gap-value").textContent = `KZT ${finalCashGap.toLocaleString()}`;
            document.getElementById("days-coverage-value").textContent = `${daysCoverage}`;
        
            

            const container = document.getElementById("alerts-list");
            if (container) {
                container.innerHTML = "";
                alerts.forEach(alert => {
                    const div = document.createElement("div");
                    div.classList.add("alert-item", alert.severity);
                    div.innerHTML = `
                        <div class="alert-icon"><span class="icon">⚠️</span></div>
                        <div class="alert-content">
                            <h4>${alert.title}</h4>
                            <p>${alert.message}</p>
                            <div class="alert-meta">
                                <span class="date">${alert.date}</span>
                                <span class="status">${alert.status}</span>
                            </div>
                        </div>
                    `;
                    container.appendChild(div);
                });
            }

            const gapData = chart.cash_in.map((v, i) => v - chart.cash_out[i]);
            const alertPoints = chart.cash_gap.map((val, i) => val < 0 ? val : null);

            const ctxFlow = document.getElementById('cash-flow-chart').getContext('2d');
            new Chart(ctxFlow, {
                type: 'line',
                data: {
                    labels: chart.labels,
                    datasets: [
                        {
                            label: 'Cash In',
                            data: chart.cash_in,
                            borderColor: '#10b981',
                            pointRadius: 4,
                            pointBackgroundColor: chart.cash_in.map((v, i) => (gapData[i] < 0 ? 'red' : '#10b981')),
                            pointHoverRadius: 6,
                            pointHoverBackgroundColor: chart.cash_in.map((v, i) => (gapData[i] < 0 ? 'red' : '#10b981')),
                        },
                        {
                            label: 'Cash Out',
                            data: chart.cash_out,
                            borderColor: '#ef4444',
                            pointRadius: 4,
                            pointBackgroundColor: chart.cash_out.map((v, i) => (gapData[i] < 0 ? 'red' : '#ef4444')),
                            pointHoverRadius: 6,
                            pointHoverBackgroundColor: chart.cash_out.map((v, i) => (gapData[i] < 0 ? 'red' : '#ef4444'))
                        }
                    ]
                },
                options: {
                    plugins: {
                        tooltip: {
                            callbacks: {
                                label: function(context) {
                                    const i = context.dataIndex;
                                    const dataset = context.dataset;
                                    if (dataset.label === 'Cash In' && gapData[i] < 0) {
                                        return `⚠️ Alert: Cash Gap in ${chart.labels[i]}`;
                                    }
                                    return `${dataset.label}: $${context.raw}`;
                                }
                            }
                        }
                    }
                }
            });

            const ctxGap = document.getElementById('cash-gap-chart').getContext('2d');
            new Chart(ctxGap, {
                type: 'bar',
                data: {
                    labels: chart.labels,
                    datasets: [
                        {
                            label: 'Cash Gap',
                            data: chart.cash_gap,
                            backgroundColor: '#3b82f6'
                        },
                        {
                            type: 'line',
                            label: '⚠️ Alert',
                            data: alertPoints,
                            pointBackgroundColor: 'red',
                            pointRadius: 6,
                            borderWidth: 0,
                            fill: false
                        }
                    ]
                }
            });

            const ctxProjection = document.getElementById('projection-chart').getContext('2d');
            new Chart(ctxProjection, {
                type: 'line',
                data: {
                    labels: ['Today', '30 Days', '60 Days', '90 Days'],
                    datasets: [{ label: 'Projected Cash', data: [3000, 2800, 2600, 2500], borderColor: '#0ea5e9' }]
                }
            });
        })
        .catch(error => {
            console.error("Error loading dashboard data:", error);
        })
        .finally(() => {
            if (loader) loader.style.display = "none";
            if (dashboardSection) dashboardSection.style.opacity = 1;
        });
    }

    if (dayRangeSelector) {
        for (let i = 1; i <= 30; i++) {
            const option = document.createElement("option");
            option.value = i;
            option.textContent = i;
            if (i === selectedDays) option.selected = true;
            dayRangeSelector.appendChild(option);
        }

        dayRangeSelector.addEventListener("change", () => {
            selectedDays = parseInt(dayRangeSelector.value);
            localStorage.setItem("selectedDays", selectedDays);
            loadDashboardData(selectedDays);
        });
    }

    loadDashboardData(selectedDays);
});
