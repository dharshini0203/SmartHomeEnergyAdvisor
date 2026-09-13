let energyChart = null;


function addAppliance() {

    const container =
        document.getElementById("applianceContainer");

    const row =
        document.createElement("div");

    row.className = "appliance-row";

    row.innerHTML = `

        <input
            type="text"
            placeholder="Appliance Name"
            class="appliance">

        <input
            type="number"
            placeholder="Power (W)"
            class="power">

        <input
            type="number"
            placeholder="Hours/day"
            class="hours">

        <input
            type="number"
            placeholder="Days"
            class="days"
            value="30">

        <button
            type="button"
            class="removeBtn"
            onclick="removeRow(this)">
            ✕
        </button>

    `;

    container.appendChild(row);
}


function removeRow(button) {

    button.parentElement.remove();

}


async function calculateEnergy() {

    const rows =
        document.querySelectorAll(".appliance-row");

    const tariff =
        parseFloat(
            document.getElementById("tariff").value
        );

    if (isNaN(tariff) || tariff < 0) {

        alert("Please enter a valid electricity tariff.");

        return;
    }


    const appliances = [];


    rows.forEach(row => {

        const appliance =
            row.querySelector(".appliance").value;

        const power =
            parseFloat(
                row.querySelector(".power").value
            );

        const hours =
            parseFloat(
                row.querySelector(".hours").value
            );

        const days =
            parseInt(
                row.querySelector(".days").value
            );


        if (
            appliance &&
            !isNaN(power) &&
            !isNaN(hours) &&
            !isNaN(days)
        ) {

            appliances.push({

                appliance: appliance,

                power: power,

                hours: hours,

                days: days

            });

        }

    });


    if (appliances.length === 0) {

        alert(
            "Please enter at least one appliance."
        );

        return;
    }


    const response =
        await fetch("/calculate", {

            method: "POST",

            headers: {
                "Content-Type":
                    "application/json"
            },

            body: JSON.stringify({

                appliances: appliances,

                tariff: tariff

            })

        });


    const data =
        await response.json();


    document.getElementById(
        "totalUnits"
    ).textContent =
        data.total_units + " kWh";


    document.getElementById(
        "totalCost"
    ).textContent =
        "₹" + data.total_cost;


    if (data.highest_consumer) {

        document.getElementById(
            "highestConsumer"
        ).textContent =
            data.highest_consumer.appliance;

    }


    displayRecommendations(
        data.appliances
    );


    createChart(
        data.appliances
    );

}


function displayRecommendations(appliances) {

    const container =
        document.getElementById(
            "recommendations"
        );

    container.innerHTML = "";


    appliances.forEach(item => {

        const paragraph =
            document.createElement("p");

        paragraph.innerHTML =

            `<strong>${item.appliance}:</strong>
             ${item.recommendation}`;

        container.appendChild(
            paragraph
        );

    });

}


function createChart(appliances) {

    const labels =
        appliances.map(
            item => item.appliance
        );


    const values =
        appliances.map(
            item => item.units
        );


    const ctx =
        document.getElementById(
            "energyChart"
        );


    if (energyChart) {

        energyChart.destroy();

    }


    energyChart = new Chart(
        ctx,
        {

            type: "bar",

            data: {

                labels: labels,

                datasets: [{

                    label:
                        "Energy Consumption (kWh)",

                    data: values

                }]

            },

            options: {

                responsive: true,

                plugins: {

                    legend: {

                        display: true

                    }

                }

            }

        }
    );

}