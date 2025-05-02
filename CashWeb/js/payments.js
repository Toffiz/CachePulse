
  document.addEventListener("DOMContentLoaded", function () {
    const calendarEl = document.getElementById("calendar");
    const searchInput = document.getElementById("payment-search");
  
    async function fetchPayments() {
      try {
        const res = await fetch("http://127.0.0.1:8000/api/payments");
        const data = await res.json();
        return data.map(payment => ({
          title: `${payment.category} - KZT ${(payment.amount * -1).toLocaleString()}`,
          start: payment.date,
          backgroundColor: payment.amount >= 0 ? "#22c55e" : "#f97316",
          borderColor: "#ccc",
          extendedProps: {
            category: payment.category
          }
        }));
      } catch (err) {
        console.error("Failed to load payments:", err);
        return [];
      }
    }
  
    let calendar = new FullCalendar.Calendar(calendarEl, {
      initialView: "dayGridMonth",
      locale: "en",
      height: "auto",
      headerToolbar: {
        left: "prev,next today",
        center: "title",
        right: "dayGridMonth,listWeek"
      },
      events: [],
      eventClick: function(info) {
        const { title, start } = info.event;
        alert(`Payment: ${title}\nDate: ${start.toLocaleDateString()}`);
    }
    });
  
    calendar.render();
  
    fetchPayments().then(events => {
      events.forEach(event => calendar.addEvent(event));
  
      searchInput?.addEventListener("input", (e) => {
        const query = e.target.value.toLowerCase();
        const filtered = events.filter(event =>
          event.title.toLowerCase().includes(query)
        );
        calendar.removeAllEvents();
        filtered.forEach(event => calendar.addEvent(event));
      });
    });
  });
  