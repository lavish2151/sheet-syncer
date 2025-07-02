document.addEventListener("DOMContentLoaded", function () {
    const syncButton = document.getElementById("sync-btn");
    const tableContainer = document.getElementById("table-container");

    syncButton.addEventListener("click", function () {
        fetch("/api/sheet")
            .then(response => response.json())
            .then(data => {
                renderTable(data);
            })
            .catch(error => {
                console.error("Error fetching data:", error);
            });
    });

    function renderTable(records) {
        if (records.length === 0) {
            tableContainer.innerHTML = "<p>No data found.</p>";
            return;
        }

        let table = "<table><thead><tr>";
        for (let key of Object.keys(records[0])) {
            table += `<th>${key}</th>`;
        }
        table += "</tr></thead><tbody>";

        for (let row of records) {
            table += "<tr>";
            for (let value of Object.values(row)) {
                table += `<td>${value}</td>`;
            }
            table += "</tr>";
        }

        table += "</tbody></table>";
        tableContainer.innerHTML = table;
    }
});
