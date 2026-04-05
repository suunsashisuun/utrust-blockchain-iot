import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import simpy
import pandas as pd
import random


# 🔥 USE MAIN ENGINE (IMPORTANT)
from g_simulation.simpy_engine import run_simulation

# scheduler + selector
from e_consensus.scheduler import scheduler_with_selector
from e_consensus.gwo_selector import GWOSelector

# metrics
from h_metrics.metrics import (
    average_latency,
    reset_metrics
)


SIM_TIME = 100
RUNS = 5


# ---------------------------
# RUN ONE SIZE (MULTIPLE RUNS)
# ---------------------------
def run_scalability(num_validators):

    latencies = []

    for i in range(RUNS):

        random.seed(i)  # 🔥 ensures variation

        env = simpy.Environment()

        reset_metrics()

        # 🔥 USE SAME ENGINE (CONSISTENT PIPELINE)
        blockchain, validator_network = run_simulation(
            env,
            scheduler_with_selector,
            GWOSelector,
            num_validators=num_validators
        )

        env.run(until=SIM_TIME)

        latencies.append(average_latency())

    return round(sum(latencies) / len(latencies), 4)


# ---------------------------
# MAIN
# ---------------------------
network_sizes = [50, 100, 200]

results = []

for size in network_sizes:

    print(f"\nRunning for {size} validators...")

    latency = run_scalability(size)

    results.append({
        "Validators": size,
        "AvgLatency": round(latency, 4)
    })


df = pd.DataFrame(results)

print("\nScalability Results")
print(df)

df.to_csv("scalability_results.csv", index=False)
