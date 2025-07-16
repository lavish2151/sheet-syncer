let page = 1;
let loading = false;
const pageSize = 25;

function fetchEmployees() {
    if (loading) return;
    loading = true;
    document.getElementById("loading").style.display = "block";

    fetch(`/api/employees?page=${page}&Page_size=${pageSize}`)
        .then(response => response.json())
        .then(data => {
            const tbody = document.getElementById("employee-tbody");

            data.forEach(emp => {
                const row = document.createElement("tr");
                row.innerHTML = `
                    <td>${emp.employee_id}</td>
                    <td>${emp.first_name}</td>
                    <td>${new Date(emp.date_of_joining).toLocaleDateString()}</td>
                    <td>${emp.salary || "N/A"}</td>
                    <td>${emp.pay_grade || "N/A"}</td>
                    <td>${emp.phone_number || "N/A"}</td>
                    <td>${emp.city || "N/A"}</td>
                `;
                tbody.appendChild(row);
            });

            if (data.length === 0) {
                document.getElementById("loading").innerText = "No more data.";
            } else {
                page += 1;
                loading = false;
                document.getElementById("loading").style.display = "none";

                // If still not scrollable, fetch more
                setTimeout(() => {
                    if (document.body.scrollHeight <= window.innerHeight + 100) {
                        fetchEmployees();
                    }
                }, 300);
            }
        })
        .catch(error => {
            console.error("Error:", error);
            document.getElementById("loading").innerText = "Error loading data.";
        });
}

window.addEventListener("scroll", () => {
    if (window.innerHeight + window.scrollY >= document.body.offsetHeight - 50) {
        fetchEmployees();
    }
});

fetchEmployees();
