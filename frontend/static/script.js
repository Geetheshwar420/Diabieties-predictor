let glucoseChart = null;  // ✅ Properly initialize Chart.js variable

function predictGlucose() {
    let inputField = document.getElementById("glucoseInput");
    let inputValues = inputField.value.split(",").map(Number);

    if (inputValues.length !== 10 || inputValues.some(isNaN)) {
        alert("❌ Please enter exactly 10 numeric glucose readings.");
        return;
    }

    fetch("/predict", {
        method: "POST",
        body: JSON.stringify({ glucose_values: inputValues }),
        headers: { "Content-Type": "application/json" }
    })
    .then(response => response.json())
    .then(data => {
        let resultDiv = document.getElementById("result");
        if (data.error) {
            resultDiv.innerHTML = `<p style="color: red;">❌ ${data.error}</p>`;
        } else {
            let predictedValues = data.predicted_glucose_levels;
            resultDiv.innerHTML = `<h3>✅ Predicted Glucose Levels</h3>
                                   <p>${predictedValues.join(", ")}</p>`;

            // ✅ Draw Graph with Streamlit-Like Style
            drawGlucoseChart(inputValues, predictedValues);
        }
    })
    .catch(error => console.error("❌ API Error:", error));
}

function drawGlucoseChart(actual, predicted) {
    let ctx = document.getElementById("glucoseChart").getContext("2d");

    // ✅ Fix: Clear existing chart before creating a new one
    if (glucoseChart instanceof Chart) {
        glucoseChart.destroy();
    }

    glucoseChart = new Chart(ctx, {
        type: "line",
        data: {
            labels: ["T-9", "T-8", "T-7", "T-6", "T-5", "T-4", "T-3", "T-2", "T-1", "T-0"],
            datasets: [
                {
                    label: "Actual Glucose",
                    data: actual,
                    borderColor: "#1f77b4",  // ✅ Streamlit-style blue
                    borderWidth: 3,
                    fill: false,
                    pointBackgroundColor: "#1f77b4",
                    pointBorderColor: "#ffffff",
                    pointRadius: 5
                },
                {
                    label: "Predicted Glucose",
                    data: predicted,
                    borderColor: "#ff7f0e",  // ✅ Streamlit-style orange
                    borderWidth: 3,
                    borderDash: [5, 5],
                    fill: false,
                    pointBackgroundColor: "#ff7f0e",
                    pointBorderColor: "#ffffff",
                    pointRadius: 5
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: false,
                    grid: {
                        color: "rgba(200, 200, 200, 0.2)"  // ✅ Light grid
                    }
                },
                x: {
                    grid: {
                        color: "rgba(200, 200, 200, 0.2)"  // ✅ Light grid
                    }
                }
            },
            plugins: {
                legend: {
                    labels: {
                        color: "#000",  // ✅ Dark text for better readability
                        font: {
                            size: 14
                        }
                    }
                }
            }
        }
    });
}
