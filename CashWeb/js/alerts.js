


// alerts.js (updated for dynamic API alerts and rule submission)

document.addEventListener('DOMContentLoaded', function () {
    const statusFilter = document.getElementById('status-filter');
    const typeFilter = document.getElementById('type-filter');

    function filterAlerts() {
        const status = statusFilter.value;
        const type = typeFilter.value;
        const alerts = document.querySelectorAll('.alert-item');

        alerts.forEach(alert => {
            let show = true;
            if (status !== 'all' && !alert.classList.contains(status.toLowerCase())) show = false;
            if (type !== 'all' && !alert.classList.contains(type.toLowerCase())) show = false;
            alert.style.display = show ? 'flex' : 'none';
        });
    }

    statusFilter?.addEventListener('change', filterAlerts);
    typeFilter?.addEventListener('change', filterAlerts);

    // Fetch alerts from API
    fetch("http://127.0.0.1:8000/api/alerts")
        .then(res => res.json())
        .then(data => {
            const container = document.getElementById("alerts-container");
            container.innerHTML = "";

            data.forEach(alert => {
                const div = document.createElement("div");
                div.classList.add("alert-item", alert.severity.toLowerCase(), alert.status.toLowerCase());
                div.innerHTML = `
                    <div class="alert-icon">
                        <span class="icon">⚠️</span>
                    </div>
                    <div class="alert-content">
                        <h4>${alert.title}</h4>
                        <p>${alert.message}</p>
                        <div class="alert-meta">
                            <span class="date">${alert.date}</span>
                            <span class="status">${alert.status}</span>
                        </div>
                    </div>
                    <div class="alert-actions">
                        <button class="btn btn-sm btn-outline">Mark as Resolved</button>
                        <button class="btn btn-sm btn-icon">···</button>
                    </div>
                `;
                container.appendChild(div);
            });
            filterAlerts();
        })
        .catch(err => console.error("Error loading alerts:", err));

    // Modal control
    const createRuleBtn = document.getElementById('create-alert-rule');
    const modal = document.getElementById('create-rule-modal');
    const closeModal = document.querySelector('.close-modal');
    const form = document.getElementById('alert-rule-form');

    createRuleBtn?.addEventListener('click', () => modal.style.display = 'block');
    closeModal?.addEventListener('click', () => modal.style.display = 'none');
    window.addEventListener('click', (event) => {
        if (event.target === modal) {
            modal.style.display = 'none';
        }
    });

    form?.addEventListener('submit', function (e) {
        e.preventDefault();

        const metricMap = {
            cash_gap: "cash_gap",
            cash_inflow: "cash_in",
            cash_outflow: "cash_out",
            coverage: "days_coverage"
        };
        const operatorMap = {
            less_than: "<",
            greater_than: ">",
            equal_to: "==",
            change_by: "!=" // placeholder logic, should be custom later
        };

        const metric = metricMap[document.getElementById("rule-type").value];
        const operator = "";
        const value = 0;
        const message = document.getElementById("rule-name").value;
        const severityThresholds = {
            info: parseFloat(document.getElementById("severity-info").value),
            warning: parseFloat(document.getElementById("severity-warning").value),
            critical: parseFloat(document.getElementById("severity-critical").value)
        };
        
        fetch("http://127.0.0.1:8000/api/alert-rules", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                metric,
                operator,
                value,
                message,
                severity_thresholds: severityThresholds
            })
        
        })
            .then(res => res.json())
            .then(data => {
                alert("Alert rule added!");
                modal.style.display = "none";
            })
            .catch(err => {
                console.error("Failed to submit alert rule:", err);
                alert("Failed to submit rule.");
            });
    });
});