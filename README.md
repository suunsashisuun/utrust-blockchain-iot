# U-TRUST: Urgency-Aware Trust-Based Consensus for Lightweight IoT Blockchain

This project presents a simulation-based implementation of an urgency-aware, trust-based consensus framework designed for resource-constrained IoT environments. The term "lightweight" refers to a design approach aimed at reducing computational and communication overhead in consensus through simplified protocol phases and selective validator participation, making it suitable for resource-constrained IoT environments.

---

## Overview

U-TRUST is a simulation-based framework that integrates IoT data processing, machine learning-based urgency classification, and trust-aware blockchain consensus mechanisms.

The system models how IoT sensor data flows through a network, is prioritized based on urgency, and is validated using a PBFT-inspired consensus enhanced with trust scoring and optimization techniques.

The primary contribution of this work lies in combining trust-aware consensus, urgency-driven prioritization, and distribution-based evaluation within a unified simulation framework.

---

## Key Features

* **SimPy-based Simulation Engine**

  * Models IoT transaction flow and system dynamics

* **ML-based Urgency Classification**

  * Classifies incoming sensor data into priority levels

* **Priority Scheduling**

  * Separates urgent and normal transactions

* **Trust-Aware Validator Selection**

  * Uses Grey Wolf Optimization (GWO)
  * Penalizes malicious or unreliable validators

* **PBFT-Inspired Consensus (Simplified for Simulation)**

  * Simulates Pre-Prepare, Prepare, and Commit phases

* **Malicious Node Simulation**

  * 10% adversarial validators included

* **Evaluation Framework**

  * Multi-run experiments with statistical analysis
  * Metrics:

    * Latency
    * Throughput
    * Fairness

---

## System Architecture

Pipeline:

IoT Sensors → ML Classifier → Priority Queues → Validator Selection (GWO + Trust) → PBFT Consensus → Metrics Collection

---

## Evaluation Strategy

The system is evaluated across multiple independent simulation runs to ensure statistical reliability.

### Metrics:

* **Latency** – Time taken for transaction confirmation
* **Throughput** – Transactions processed per unit time
* **Fairness** – Distribution balance across validators

### Key Strength:

Unlike simple average-based evaluation, this project uses:

* Distribution analysis (box/violin plots)
* Run-to-run variability
* Stability metrics

---

## Project Structure

* `a_iot/` – Sensor simulation
* `b_processing/` – ML classifier and preprocessing
* `baseline_consensus/` – Baseline strategies
* `c_network/` – Validator network logic
* `d_trust/` – Trust management system
* `e_consensus/` – GWO + PBFT logic
* `g_simulation/` – SimPy engine
* `h_metrics/` – Metrics and experiment runner
* `i_visualization/` – Plot generation
* `z_dashboard/` – Real-time dashboard

---

## How to Run

### Run Experiments

```bash
python h_metrics/experiment_runner.py
```

### Run Dashboard

```bash
python z_dashboard/app.py
```
---
## Running Evaluation and Visualization

### Generate Plots

After running experiments, generate evaluation plots:

```bash
python i_visualization/plot.py
```

This produces:

* Distribution plots (box/violin)
* Error bar plots
* Run-wise consistency plots

These plots highlight variability, stability, and performance differences across strategies.

---

### Run Scalability Tests

To evaluate system performance under increasing load:

```bash
python h_metrics/scalability_test.py
```

This analyzes how:

* Latency
* Throughput
* Fairness

scale with system size and transaction volume.

---

### Important Notes

* Ensure experiment data (`final_results.csv`, `detailed_runs.csv`) exists before generating plots.
* All CSV files are expected in the project root directory.

---

## Key Design Decisions

* PBFT is simulated (not fully implemented) for tractability
* IoT data is statistically modeled, not physically simulated
* Trust system is heuristic (no ML training required)
* Random seeds ensure reproducibility across runs

---

## Limitations

* Not a production blockchain implementation
* Simplified network and consensus assumptions
* Sensor data lacks real-world physical modeling

---

## Conclusion

This project demonstrates a modular and extensible approach to evaluating blockchain consensus strategies in IoT environments, with a strong focus on fairness, trust, and statistical evaluation.
