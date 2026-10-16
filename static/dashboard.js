
document.addEventListener("DOMContentLoaded", async () => {
    const money = amount =>
        `$${Number(amount).toFixed(2)}`;

    try {
        const response = await fetch("/api/attribution");

        if (!response.ok) {
            throw new Error("Could not load attribution data.");
        }

        const data = await response.json();

        // Update summary cards
        document.getElementById("total-revenue").textContent =
            money(data.total_revenue);

        document.getElementById("total-orders").textContent =
            data.total_orders;

        document.getElementById("attributed-orders").textContent =
            data.attributed_orders;

        document.getElementById("unattributed-revenue").textContent =
            money(data.unattributed_revenue);

        // Populate table safely
        const table = document.getElementById(
            "attribution-table"
        );

        data.channels.forEach(row => {
            const tr = document.createElement("tr");

            [
                row.channel,
                money(row.first_touch),
                money(row.last_touch),
                money(row.linear)
            ].forEach(value => {
                const td = document.createElement("td");
                td.textContent = value;
                tr.appendChild(td);
            });

            table.appendChild(tr);
        });

        // Draw grouped bar chart
        if (typeof Chart === "undefined") {
            throw new Error("Chart.js did not load.");
        }

        new Chart(
            document.getElementById("attribution-chart"),
            {
                type: "bar",
                data: {
                    labels: data.channels.map(r => r.channel),
                    datasets: [
                        {
                            label: "First-Touch",
                            data: data.channels.map(
                                r => r.first_touch
                            ),
                            backgroundColor: "#D9481F"
                        },
                        {
                            label: "Last-Touch",
                            data: data.channels.map(
                                r => r.last_touch
                            ),
                            backgroundColor: "#F2B134"
                        },
                        {
                            label: "Linear",
                            data: data.channels.map(
                                r => r.linear
                            ),
                            backgroundColor: "#3E6B35"
                        }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        y: {
                            beginAtZero: true,
                            title: {
                                display: true,
                                text: "Attributed Revenue ($)"
                            }
                        }
                    }
                }
            }
        );

    } catch (error) {
        document.getElementById(
            "error-message"
        ).textContent = error.message;

        console.error(error);
    }
});
