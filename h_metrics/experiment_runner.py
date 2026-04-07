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
from baseline_consensus import baseline_scheduler as bs
from e_consensus.gwo_selector import GWOSelector

# -----------------------------
# METRICS
# -----------------------------
from h_metrics.metrics import (
    record_transaction,
    average_latency,
    throughput,
    fairness_index,
    reset_metrics,
    average_validator_usage   # 🔥 NEW
)

# -----------------------------
# CONFIG
# -----------------------------
from config import RUNS, SIM_TIME

# Stores per-run results
all_runs = []

# -----------------------------
# RUN SINGLE STRATEGY
# -----------------------------
def run_strategy(label, scheduler_func, selector_class, use_ml=True):

    latencies = []
    throughputs = []
    fairnesses = []
    validator_usages = []

    for run_index in range(RUNS):

        random.seed(run_index)

        env = simpy.Environment()

        reset_metrics()

        # 🔥 Inject mode using wrapper
        # 🔥 SAFE MODE INJECTION (ONLY FOR BASELINE)
        
        if scheduler_func == baseline_scheduler:
            if label == "FullParticipation":
                bs.BASELINE_MODE = "full_part"
            elif label == "GreedyTrust":
                bs.BASELINE_MODE = "agg_trust"

            else:
                bs.BASELINE_MODE = "default"
        scheduler = scheduler_func

        blockchain, validator_network = run_simulation(
            env,
            scheduler,
            selector_class,
            num_validators=50,
            use_ml=use_ml
        )

        env.run(until=SIM_TIME)

        # -----------------------------
        # COLLECT METRICS
        # -----------------------------
        latency_val = average_latency()
        throughput_val = throughput(env.now)
        fairness_val = fairness_index(
            validator_network.get_validators()
        )
        validator_usage = average_validator_usage()

        # Detailed runs
        all_runs.append({
            "strategy": label,
            "run": run_index,
            "latency": latency_val,
            "throughput": throughput_val,
            "fairness": fairness_val,
            "validators_used": validator_usage   # 🔥 NEW
        })

        latencies.append(latency_val)
        throughputs.append(throughput_val)
        fairnesses.append(fairness_val)
        validator_usages.append(validator_usage)

    # -----------------------------
    # AGGREGATED RESULTS
    # -----------------------------
    return {
        "strategy": label,
        "latency": round(sum(latencies) / RUNS, 4),
        "throughput": round(sum(throughputs) / RUNS, 4),
        "fairness": round(sum(fairnesses) / RUNS, 4),
        "validators_used": round(sum(validator_usages) / RUNS, 2),

        "latency_std": round(pd.Series(latencies).std(), 4),
        "throughput_std": round(pd.Series(throughputs).std(), 4),
        "fairness_std": round(pd.Series(fairnesses).std(), 4),
    }

# -----------------------------
# RUN ALL STRATEGIES
# -----------------------------
def run_all():

    results = []

    # 🔥 STRONG BASELINES
    results.append(run_strategy("FullParticipation", baseline_scheduler, RandomSelector))
    results.append(run_strategy("GreedyTrust", baseline_scheduler, TrustSelector))


    # Existing baselines (optional but useful)
    results.append(run_strategy("Random", baseline_scheduler, RandomSelector))
    results.append(run_strategy("RoundRobin", baseline_scheduler, RoundRobinSelector))
    results.append(run_strategy("BalancedTrust", baseline_scheduler, TrustSelector))

    # Proposed model
    results.append(run_strategy("NoUrgency", scheduler_with_selector, GWOSelector, use_ml=False))
    results.append(run_strategy("UTrust", scheduler_with_selector, GWOSelector, use_ml=True))

    results_df = pd.DataFrame(results)
    detailed_df = pd.DataFrame(all_runs)

    detailed_df.to_csv("detailed_runs.csv", index=False)
    results_df.to_csv("final_results.csv", index=False)

    print("\n===== FINAL RESULTS =====")
    print(results_df)
    print("\n===== VALIDATOR USAGE (EFFICIENCY) =====")
    print(results_df[["strategy", "validators_used"]])


# -----------------------------
# MAIN
# -----------------------------
if __name__ == "__main__":
    run_all()
