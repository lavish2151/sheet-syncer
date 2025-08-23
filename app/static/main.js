let currentPage = 1;
const pageSize = 25;
let isLoading = false;
let allDataLoaded = false;
let startDate = '';
let endDate = '';

// Initial load
document.addEventListener("DOMContentLoaded", () => {
    fetchEmployees();

    window.addEventListener("scroll", () => {
        if ((window.innerHeight + window.scrollY) >= document.body.offsetHeight - 100) {
            fetchEmployees();
        }
    });

    document.getElementById("applyFilter").addEventListener("click", () => {
        currentPage = 1;
        allDataLoaded = false;
        document.getElementById("employeeBody").innerHTML = "";  // Clear table
        startDate = document.getElementById("startDate").value;
        endDate = document.getElementById("endDate").value;
        fetchEmployees();
    });
});

function fetchEmployees() {
    if (isLoading || allDataLoaded) return;

    isLoading = true;
    document.getElementById("loader").style.display = "block";

    let url = `/api/employees?page=${currentPage}&page_size=${pageSize}`;
    if (startDate && endDate) {
        url += `&start_date=${startDate}&end_date=${endDate}`;
    }

    fetch(url)
        .then(res => res.json())
        .then(data => {
            if (data.length === 0) {
                allDataLoaded = true;
            } else {
                appendRows(data);
                currentPage++;
            }
        })
        .catch(error => console.error("Error fetching data:", error))
        .finally(() => {
            isLoading = false;
            document.getElementById("loader").style.display = "none";
        });
}

function appendRows(data) {
    const tbody = document.getElementById("employeeBody");
    data.forEach(emp => {
        const row = document.createElement("tr");
        row.innerHTML = `
            <td>${emp.employee_id}</td>
            <td>${emp.first_name}</td>
            <td>${emp.date_of_joining}</td>
            <td>${emp.salary ?? ''}</td>
            <td>${emp.pay_grade ?? ''}</td>
            <td>${emp.phone_number ?? ''}</td>
            <td>${emp.city ?? ''}</td>
        `;
        tbody.appendChild(row);
    });
}