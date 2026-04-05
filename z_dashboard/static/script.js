let trustChart;
let fairnessChart;
let loadChart;
let comparisonChart;
let sensorChart;


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
        const statusBox = document.getElementById("systemStatus");

        if (data.running) {
            statusBox.innerHTML = "🟢 RUNNING";
        } else {
            statusBox.innerHTML = "🔴 STOPPED";
        }

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
        const banner = document.getElementById("alertBanner");

        if (data.last_processed_event) {
            const e = data.last_processed_event;

            if (e.urgency === "CRITICAL" && !banner.classList.contains("active")) {
                banner.classList.add("active");
                banner.style.display = "block";

                banner.innerHTML = `
                    🚨 CRITICAL EVENT — Device ${e.device_id} | Gas ${e.gas.toFixed(2)}
                `;

                setTimeout(() => {
                    banner.style.display = "none";
                    banner.classList.remove("active");
                }, 2000);
            }
        }

        const traceBox = document.getElementById("eventTrace");

        if (data.event_trace) {
            traceBox.innerHTML = data.event_trace.map(e => `
                <div style="margin-bottom:6px;">
                    📡 D${e.device} → ${e.urgency} → ${e.validator} → 
                    <span style="color:${e.result ? 'green' : 'red'};">
                        ${e.result ? '✔' : '✖'}
                    </span>
                </div>
            `).join("");
        }

        // PERFORMANCE
        document.getElementById("latency").innerText = (data.latency || 0).toFixed(4);
        document.getElementById("throughput").innerText = (data.throughput || 0).toFixed(4);

        let fairnessVal = data.fairness || 0;
        let displayVal = fairnessVal.toFixed(4);

        let color = "red";
        if (fairnessVal > 0.4) color = "orange";
        if (fairnessVal > 0.6) color = "green";

        let badge = "";
        if (fairnessVal > 0.6) badge = "🟢 Excellent";
        else if (fairnessVal > 0.4) badge = "🟡 Good";
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


        const events = data.last_events || [];

        const sensorLabels = events.map(e => `D${e.device_id}`);
        const gasValues = events.map(e => e.gas);

        const sensorColors = events.map(e => {
            if (e.urgency === "CRITICAL") return "#ef4444";
            if (e.urgency === "WARNING") return "#f59e0b";
            return "#3b82f6";
        });



        if (!sensorChart) {
            const ctx = document.getElementById("sensorChart").getContext("2d");

            sensorChart = new Chart(ctx, {
                type: "bar",
                data: {
                    labels: sensorLabels,
                    datasets: [
                        {
                            label: "Normal",
                            data: gasValues.map((v, i) => events[i].urgency === "NORMAL" ? v : null),
                            backgroundColor: "#3b82f6"
                        },
                        {
                            label: "Warning",
                            data: gasValues.map((v, i) => events[i].urgency === "WARNING" ? v : null),
                            backgroundColor: "#f59e0b"
                        },
                        {
                            label: "Critical",
                            data: gasValues.map((v, i) => events[i].urgency === "CRITICAL" ? v : null),
                            backgroundColor: "#ef4444"
                        }
                    ]

                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        y: {
                            min: 0,
                            max: 10000   // 👈 FIXED RANGE
                        }
                    }
                }
 

            });
        } else {
            sensorChart.data.labels = sensorLabels;
            sensorChart.data.datasets[0].data =
                gasValues.map((v, i) => events[i].urgency === "NORMAL" ? v : null);

            sensorChart.data.datasets[1].data =
                gasValues.map((v, i) => events[i].urgency === "WARNING" ? v : null);

            sensorChart.data.datasets[2].data =
                gasValues.map((v, i) => events[i].urgency === "CRITICAL" ? v : null);

            sensorChart.update();
        }

        if (data.last_classification) {
            const c = data.last_classification;

            document.getElementById("classificationLogic").innerHTML = `
                Gas: ${c.gas.toFixed(2)}<br>
                Prediction: <b>${c.result}</b><br>
                Confidence: ${(c.confidence * 100).toFixed(1)}%
            `;
        }


        if (data.consensus_info) {
            const c = data.consensus_info;

            document.getElementById("consensusBox").innerHTML = `
                ✔ ${c.approved} approved<br>
                ✖ ${c.rejected} rejected
            `;
        }

        if (data.validator_decision) {
            const v = data.validator_decision;

            document.getElementById("validatorDecision").innerHTML = `
                Selected: <b>${v.selected}</b><br>
                Reason: ${v.reason}
            `;
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
        const response = await res.json();

        comparisonData = response.data;        // 🔥 FIX
        const insight = response.insight;      // 🔥 NEW

        // OPTIONAL: show numeric improvement
        const insightBox = document.getElementById("comparisonInsight");

        if (insightBox && insight) {
            insightBox.innerHTML = `
                <br><br>
                📊 Fairness Gain: ${insight.fairness_gain.toFixed(3)}  
                <br>
                ⏱ Latency Change: ${insight.latency_diff.toFixed(3)}
            `;
        }

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
    const values = comparisonData.map(d => {
        if (d[metric + "_mean"] !== undefined) {
            return d[metric + "_mean"];   // 🔥 use mean if exists
        }
        return d[metric];
    });



    if (!values.length) return;

    let bestIndex, worstIndex;

    if (metric === "latency") {
        bestIndex = values.indexOf(Math.min(...values));
        worstIndex = values.indexOf(Math.max(...values));
    } else {
        bestIndex = values.indexOf(Math.max(...values));
        worstIndex = values.indexOf(Math.min(...values));
    }

    const best = labels[bestIndex];
    const worst = labels[worstIndex];

    // COLOR LOGIC (clean + meaningful)
    const colors = labels.map((_, i) => {
        if (i === bestIndex) return "#22c55e";   // best → green
        if (i === worstIndex) return "#ef4444";  // worst → red
        return "#9ca3af";                        // neutral
    });

    // INSIGHT TEXT
    const insightBox = document.getElementById("comparisonInsight");

    let message = "";

    if (metric === "latency") {
        message = `⚡ ${best} minimizes delay, ${worst} is slowest`;
    }
    else if (metric === "throughput") {
        message = `🚀 ${best} handles highest load, ${worst} is weakest`;
    }
    else {
        message = `⚖️ ${best} is most fair, ${worst} is most biased and U Trust has a balanced trade off `;
    }

    if (insightBox) {
        insightBox.innerHTML = message;
    }

    const ctx = document.getElementById("comparisonChart").getContext("2d");

    if (!comparisonChart) {
        comparisonChart = new Chart(ctx, {
            type: "bar",
            data: {
                labels: labels,
                datasets: [{
                    label: metric.toUpperCase() + " (Best & Worst Highlighted)",
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
        comparisonChart.data.datasets[0].label =
            metric.toUpperCase() + " (Best & Worst Highlighted)";
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



function resetSim() {
    fetch('/reset')
        .then(() => {
            location.reload();   // 🔥 ensures clean UI reset
        });
}

