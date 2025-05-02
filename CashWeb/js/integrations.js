// integrations.js

document.addEventListener('DOMContentLoaded', function() {
    const refreshBtn = document.getElementById('refresh-sheets');
    const disconnectBtn = document.getElementById('disconnect-sheets');
    const connectForm = document.getElementById('google-sheets-form');

    if (refreshBtn) {
        refreshBtn.addEventListener('click', function() {
            alert('Sheets refreshed successfully (fake)');
            location.reload();
        });
    }

    if (disconnectBtn) {
        disconnectBtn.addEventListener('click', function() {
            alert('Disconnected from Google Sheets (fake)');
            location.reload();
        });
    }

    if (connectForm) {
        connectForm.addEventListener('submit', function(event) {
            event.preventDefault();
            alert('Google Sheet connected (fake)');
            location.reload();
        });
    }
});
document.getElementById("connect-sheet").addEventListener("click", () => {
    const url = document.getElementById("sheet-url").value.trim();
    const match = url.match(/\/d\/([a-zA-Z0-9-_]+)/);
    const sheetId = match ? match[1] : null;

    if (!sheetId) {
        alert("Invalid Google Sheets URL.");
        return;
    }

    fetch("http://127.0.0.1:8000/api/connect-sheet", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ sheet_id: sheetId })
    })
    .then(res => res.json())
    .then(data => alert("✅ Sheet connected: " + data.message))
    .catch(err => alert("❌ Failed to connect sheet."));
});
