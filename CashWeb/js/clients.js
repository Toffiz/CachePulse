document.addEventListener('DOMContentLoaded', () => {
    const clientTableBody = document.querySelector('#clients-table-body');
    const searchInput = document.getElementById('client-search');

    let clientsData = [];

    function renderClients(clients) {
        clientTableBody.innerHTML = '';
        clients.forEach(client => {
            const tr = document.createElement('tr');

            if (client.status.toLowerCase() === 'просрочено') {
                tr.classList.add('overdue');
            }

            tr.innerHTML = `
                <td>${client.name}</td>
                <td>${client.due_date}</td>
                <td>${client.actual_payment_date || '-'}</td>
                <td>$${client.actual_payment_amount?.toLocaleString() || '0'}</td>
                <td class="status ${client.status.toLowerCase()}">${client.status}</td>
                <td>$${client.debt.toLocaleString()}</td>
                <td>${client.days_overdue + ' days'}</td>
            `;
            clientTableBody.appendChild(tr);
        });
    }

    function filterClients(term) {
        const filtered = clientsData.filter(c =>
            c.name.toLowerCase().includes(term.toLowerCase())
        );
        renderClients(filtered);
    }

    searchInput?.addEventListener('input', (e) => {
        filterClients(e.target.value);
    });

    fetch('http://127.0.0.1:8000/api/clients')
        .then(res => res.json())
        .then(data => {
            clientsData = data;
            renderClients(clientsData);
        })
        .catch(err => {
            console.error('Error loading clients:', err);
        });
}); 