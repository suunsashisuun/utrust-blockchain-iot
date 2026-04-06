import sys
import os


# -----------------------------
# PATH SETUP
# -----------------------------
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


import simpy
import pandas as pd
import random


# -----------------------------
# ENGINE
# -----------------------------
from g_simulation.simpy_engine import run_simulation


# -----------------------------
# SCHEDULERS
# -----------------------------
from baseline_consensus.baseline_scheduler import baseline_scheduler
from e_consensus.scheduler import scheduler_with_selector


# -----------------------------
# SELECTORS
# -----------------------------
from baseline_consensus.random_selector import RandomSelector
from baseline_consensus.round_robin_selector import RoundRobinSelector
from baseline_consensus.trust_selector import TrustSelector
from e_consensus.gwo_selector import GWOSelector


# -----------------------------
# METRICS
# -----------------------------
from h_metrics.metrics import (
    record_transaction,
    average_latency,
    throughput,
    fairness_index,
    reset_metrics
)


# -----------------------------
# CONFIG
# -----------------------------
SIM_TIME = 100
RUNS = 20


# Stores per-run results
all_runs = []




# -----------------------------
# RUN SINGLE STRATEGY
# -----------------------------
def run_strategy(label, scheduler_func, selector_class, use_ml=True):


    latencies = []
    throughputs = []
    fairnesses = []


    for run_index in range(RUNS):


        # Ensure reproducibility per run
        random.seed(run_index)


        env = simpy.Environment()


        # Reset global metrics before each run
        reset_metrics()


        # Run simulation
        blockchain, validator_network = run_simulation(
            env,
            scheduler_func,
            selector_class,
            num_validators=50,
            use_ml=use_ml
        )


        env.run(until=SIM_TIME)


        # -----------------------------
        # COLLECT METRICS (PER RUN)
        # -----------------------------
        latency_val = average_latency()
        throughput_val = throughput(env.now)
        fairness_val = fairness_index(
            validator_network.get_validators()
        )


        # Store detailed run data
        all_runs.append({
            "strategy": label,
            "run": run_index,
            "latency": latency_val,
            "throughput": throughput_val,
            "fairness": fairness_val
        })


        # Store for averaging
        latencies.append(latency_val)
        throughputs.append(throughput_val)
        fairnesses.append(fairness_val)


    # -----------------------------
    # RETURN AGGREGATED RESULTS
    # -----------------------------
    return {
        "strategy": label,
        "latency": round(sum(latencies) / RUNS, 4),
        "throughput": round(sum(throughputs) / RUNS, 4),
        "fairness": round(sum(fairnesses) / RUNS, 4),


        # Standard deviation (stability indicator)
        "latency_std": round(pd.Series(latencies).std(), 4),
        "throughput_std": round(pd.Series(throughputs).std(), 4),
        "fairness_std": round(pd.Series(fairnesses).std(), 4),
    }




# -----------------------------
# RUN ALL STRATEGIES
# -----------------------------
def run_all():


    results = []


    # -----------------------------
    # BASELINE STRATEGIES
    # -----------------------------
    results.append(run_strategy("Random", baseline_scheduler, RandomSelector))
    results.append(run_strategy("RoundRobin", baseline_scheduler, RoundRobinSelector))
    results.append(run_strategy("Trust", baseline_scheduler, TrustSelector))


    # -----------------------------
    # PROPOSED MODEL
    # -----------------------------
    results.append(run_strategy("NoUrgency", scheduler_with_selector, GWOSelector, use_ml=False))
    results.append(run_strategy("UTrust+ML", scheduler_with_selector, GWOSelector, use_ml=True))


    # -----------------------------
    # CREATE DATAFRAMES
    # -----------------------------
    results_df = pd.DataFrame(results)
    detailed_df = pd.DataFrame(all_runs)


    # -----------------------------
    # SAVE OUTPUTS
    # -----------------------------
    detailed_df.to_csv("detailed_runs.csv", index=False)
    results_df.to_csv("final_results.csv", index=False)


    # -----------------------------
    # PRINT RESULTS
    # -----------------------------
    print("\n===== FINAL RESULTS =====")
    
    print(results_df)




# -----------------------------
# MAIN ENTRY
# -----------------------------
if __name__ == "__main__":
    run_all()
