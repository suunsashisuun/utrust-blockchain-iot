import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import simpy
import pandas as pd
import random


# engine
from g_simulation.simpy_engine import run_simulation

# schedulers
from baseline_consensus.baseline_scheduler import baseline_scheduler
from e_consensus.scheduler import scheduler_with_selector

# selectors
from baseline_consensus.random_selector import RandomSelector
from baseline_consensus.round_robin_selector import RoundRobinSelector
from baseline_consensus.trust_selector import TrustSelector
from e_consensus.gwo_selector import GWOSelector

# metrics
from h_metrics.metrics import (
    record_transaction,
    average_latency,
    throughput,
    fairness_index,
    reset_metrics
)


SIM_TIME = 100
RUNS = 5


# -----------------------------
# RUN ONE STRATEGY
# -----------------------------
def run_strategy(label, scheduler_func, selector_class,use_ml=True):

    latencies = []
    throughputs = []
    fairnesses = []

    for i in range(RUNS):
        random.seed(i)


        env = simpy.Environment()

        reset_metrics()

        blockchain, validator_network = run_simulation(
            env,
            scheduler_func,
            selector_class,
            num_validators=50,
            use_ml=use_ml
        )

        env.run(until=SIM_TIME)

        latencies.append(average_latency())
        throughputs.append(throughput(SIM_TIME))
        fairnesses.append(
            fairness_index(validator_network.get_validators())
        )

    return {
        "strategy": label,
        "latency": round(sum(latencies) / RUNS, 4),
        "throughput": round(sum(throughputs) / RUNS, 4),
        "fairness": round(sum(fairnesses) / RUNS, 4)
    }


# -----------------------------
# RUN ALL
# -----------------------------
def run_all():

    results = []

    # 🔥 BASELINES
    results.append(run_strategy("Random", baseline_scheduler, RandomSelector))
    results.append(run_strategy("RoundRobin", baseline_scheduler, RoundRobinSelector))
    results.append(run_strategy("Trust", baseline_scheduler, TrustSelector))

    # 🔥 YOUR MODEL
    results.append(run_strategy("NoUrgency", scheduler_with_selector, GWOSelector, use_ml=False))
    results.append(run_strategy("UTrust+ML", scheduler_with_selector, GWOSelector, use_ml=True))

    df = pd.DataFrame(results)

    df.to_csv("final_results.csv", index=False)

    print("\n===== FINAL RESULTS =====")
    print(df)


# -----------------------------
# MAIN
# -----------------------------
if __name__ == "__main__":
    run_all()
