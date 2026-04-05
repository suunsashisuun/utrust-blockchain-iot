let trustChart;
let fairnessChart;
let loadChart;
let comparisonChart;

let comparisonData = [];


// -----------------------------
// ANIMATION STYLE (PIPELINE)
// -----------------------------
const style = document.createElement('style');
style.innerHTML = `
@keyframes blink {
    50% { opacity: 0.3; }
}
`;
document.head.appendChild(style);


// -----------------------------
// FETCH LIVE STATE
// -----------------------------
async function fetchState() {
    try {
        const res = await fetch('/state');
        const data = await res.json();

        const trustScores = data.trust_scores || {};
        const fairnessHistory = data.fairness_history || [];
        const validatorLoads = data.validator_loads || {};

        // QUEUES
        document.getElementById("urgent").innerText = data.urgent_queue_size || 0;
        document.getElementById("normal").innerText = data.normal_queue_size || 0;
        // PROCESSED QUEUES
        document.getElementById("processedUrgent").innerText = data.processed_urgent || 0;
        document.getElementById("processedNormal").innerText = data.processed_normal || 0;

        // LAST EVENT VISUAL
        if (data.last_processed_event) {
            const e = data.last_processed_event;
            const box = document.getElementById("lastEventBox");

            let color = "#6b7280";
            if (e.urgency === "WARNING") color = "#f59e0b";
            if (e.urgency === "CRITICAL") color = "#ef4444";

            box.innerHTML = `
                <b style="color:${color};">${e.urgency}</b><br>
                Device: ${e.device_id}<br>
                Gas: ${e.gas.toFixed(2)}
            `;

            if (e.urgency === "CRITICAL") {
                box.style.border = "2px solid #ef4444";
                box.style.animation = "pulse 1s infinite";
            } else {
                box.style.border = "none";
                box.style.animation = "none";
            }
        }

        // PERFORMANCE
        document.getElementById("latency").innerText = (data.latency || 0).toFixed(4);
        document.getElementById("throughput").innerText = (data.throughput || 0).toFixed(4);

        let fairnessVal = data.fairness || 0;
        let displayVal = fairnessVal.toFixed(4);

        let color = "red";
        if (fairnessVal > 0.6) color = "orange";
        if (fairnessVal > 0.8) color = "green";

        let badge = "";
        if (fairnessVal > 0.8) badge = "🟢 Excellent";
        else if (fairnessVal > 0.6) badge = "🟡 Good";
        else badge = "🔴 Poor";

        document.getElementById("fairness").innerHTML =
            `<span style="color:${color}; font-weight:bold;">
                ${displayVal} <small>(${badge})</small>
            </span>`;

        // BLOCKCHAIN
        document.getElementById("blocks").innerText = data.blocks || 0;

        // TRUST CHART
        const labels = Object.keys(trustScores);
        const values = Object.values(trustScores);

        if (!trustChart) {
            const ctx = document.getElementById("trustChart").getContext("2d");
            trustChart = new Chart(ctx, {
                type: "bar",
                data: {
                    labels: labels,
                    datasets: [{
                        label: "Trust",
                        data: values,
                        backgroundColor: "#3498db"
                    }]
                },
                options: {
                    animation: {
                        duration: 800,
                        easing: 'easeOutQuart'
                    },
                    responsive: true,
                    maintainAspectRatio: false
                }
            });
        } else {
            trustChart.data.labels = labels;
            trustChart.data.datasets[0].data = values;
            trustChart.update('active');
        }

        // FAIRNESS HISTORY
        if (fairnessHistory.length > 0) {
            if (!fairnessChart) {
                const ctx = document.getElementById("fairnessChart").getContext("2d");
                fairnessChart = new Chart(ctx, {
                    type: "line",
                    data: {
                        labels: fairnessHistory.map((_, i) => i),
                        datasets: [{
                            label: "Fairness",
                            data: fairnessHistory,
                            borderColor: "#2ecc71",
                            tension: 0.3
                        }]
                    },
                    options: {
                        animation: { duration: 800 },
                        responsive: true,
                        maintainAspectRatio: false
                    }
                });
            } else {
                fairnessChart.data.labels = fairnessHistory.map((_, i) => i);
                fairnessChart.data.datasets[0].data = fairnessHistory;
                fairnessChart.update('active');
            }
        }

        // VALIDATOR LOAD
        const loadLabels = Object.keys(validatorLoads);
        const loadValues = Object.values(validatorLoads);

        if (!loadChart) {
            const ctx = document.getElementById("loadChart").getContext("2d");
            loadChart = new Chart(ctx, {
                type: "bar",
                data: {
                    labels: loadLabels,
                    datasets: [{
                        label: "Transactions",
                        data: loadValues,
                        backgroundColor: "#9b59b6"
                    }]
                },
                options: {
                    animation: { duration: 800 },
                    responsive: true,
                    maintainAspectRatio: false
                }
            });
        } else {
            loadChart.data.labels = loadLabels;
            loadChart.data.datasets[0].data = loadValues;
            loadChart.update('active');
        }

        // PIPELINE STATUS
        document.getElementById("pipelineStatus").innerHTML = `
        <span style="color:#60a5fa;">Domain (${data.domain_size})</span>
        <span style="animation: blink 1s infinite;"> → </span>
        <span style="color:#c084fc;">${data.selected_validator}</span>
        <span style="animation: blink 1s infinite;"> → </span>
        <span style="color:${data.consensus_result ? '#22c55e' : '#ef4444'};">
        ${data.consensus_result ? '✔ Consensus' : '✖ Failed'}
        </span>
        `;

    } catch (err) {
        console.warn("State fetch failed");
    }
}


// -----------------------------
// LOAD COMPARISON DATA
// -----------------------------
async function loadComparison() {
    try {
        const res = await fetch('/comparison');
        if (!res.ok) throw new Error();

        comparisonData = await res.json();
        updateComparison('fairness');

    } catch {
        console.warn("Comparison data not loaded");
    }
}


// -----------------------------
// UPDATE COMPARISON (TOGGLE)
// -----------------------------
function updateComparison(metric) {

    if (!comparisonData.length) return;

    const labels = comparisonData.map(d => d.strategy);
    const values = comparisonData.map(d => d[metric]);

    let bestIndex;

    if (metric === "latency") {
        bestIndex = values.indexOf(Math.min(...values));
    } else {
        bestIndex = values.indexOf(Math.max(...values));
    }

    const colors = labels.map((_, i) =>
        i === bestIndex ? "#22c55e" : "#6b7280"
    );

    const ctx = document.getElementById("comparisonChart").getContext("2d");

    if (!comparisonChart) {
        comparisonChart = new Chart(ctx, {
            type: "bar",
            data: {
                labels: labels,
                datasets: [{
                    label: metric.toUpperCase() + " (Best Highlighted)",
                    data: values,
                    backgroundColor: colors
                }]
            },
            options: {
                animation: {
                    duration: 900,
                    easing: 'easeOutQuart'
                },
                responsive: true,
                maintainAspectRatio: false
            }
        });
    } else {
        comparisonChart.data.labels = labels;
        comparisonChart.data.datasets[0].data = values;
        comparisonChart.data.datasets[0].label = metric.toUpperCase() + " (Best Highlighted)";
        comparisonChart.data.datasets[0].backgroundColor = colors;
        comparisonChart.update('active');
    }
}


// -----------------------------
// POLLING
// -----------------------------
setInterval(fetchState, 1000);


// -----------------------------
// INIT
// -----------------------------
loadComparison();


// -----------------------------
// CONTROL
// -----------------------------
function startSim() {
    fetch('/start');
}

function stopSim() {
    fetch('/stop');
}
