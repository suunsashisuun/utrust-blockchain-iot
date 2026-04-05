import sys
import os

sys.path.append(os.path.abspath(".."))

import simpy
import pandas as pd
import random
random.seed(42)

# -----------------------------
# IMPORT YOUR MODULES
# -----------------------------
from a_iot.simulation import GasSensorModel
from c_core.validator_network import ValidatorNetwork
from c_core.trust_manager import TrustManager
from c_core.gwo_selector import GWOSelector
from c_core.scheduler import scheduler_with_selector
from d_blockchain.blockchain import Blockchain

# selectors
from e_consensus.random_selector import RandomSelector
from e_consensus.round_robin_selector import RoundRobinSelector
from e_consensus.trust_selector import TrustSelector

# metrics
from f_experiments.metrics import (
    record_transaction,
    average_latency,
    throughput,
    fairness_index,
    reset_metrics
)

# -----------------------------
# URGENCY CLASSIFIER
# -----------------------------
def classify_urgency(gas):
    if gas >= 80:
        return "CRITICAL"
    elif gas >= 60:
        return "WARNING"
    else:
        return "NORMAL"


# -----------------------------
# SENSOR CREATION
# -----------------------------
def create_sensors():
    sensors = []
    for i in range(1, 11):
        base = 20 + i
        risk = 0.05 + (i * 0.04)
        sensors.append(GasSensorModel(i, base, risk))
    return sensors


# -----------------------------
# IOT GENERATOR (NO PRINTS)
# -----------------------------
def iot_generator(env, sensors, urgent_queue, normal_queue):

    while True:
        for sensor in sensors:

            gas = sensor.generate_reading()
            urgency = classify_urgency(gas)

            event = {
                "device_id": sensor.device_id,
                "gas": gas,
                "urgency": urgency,
                "timestamp": env.now
            }

            if urgency in ["CRITICAL", "WARNING"]:
                yield urgent_queue.put(event)
            else:
                yield normal_queue.put(event)

        yield env.timeout(1)


# -----------------------------
# RUN ONE SIMULATION
# -----------------------------
def run_simulation(selector_class, label, runs=5):

    latencies = []
    throughputs = []
    fairnesses = []

    for _ in range(runs):

        env = simpy.Environment()

        sensors = create_sensors()

        urgent_queue = simpy.Store(env)
        normal_queue = simpy.Store(env)

        validator_network = ValidatorNetwork(num_validators=50)
        validators = validator_network.get_validators()
        validator_ids = [v.validator_id for v in validators]

        trust_manager = TrustManager(validator_ids)

        selector = selector_class()

        blockchain = Blockchain(block_size=5)

        reset_metrics()

        env.process(iot_generator(env, sensors, urgent_queue, normal_queue))

        env.process(
            scheduler_with_selector(
                env,
                urgent_queue,
                normal_queue,
                selector,
                validator_network,
                trust_manager,
                blockchain,
                record_transaction
            )
        )

        SIM_TIME = 100
        env.run(until=SIM_TIME)

        latencies.append(average_latency())
        throughputs.append(throughput(SIM_TIME))
        fairnesses.append(fairness_index(validator_network.get_validators()))

    return {
        "strategy": label,
        "latency": round(sum(latencies)/len(latencies), 4),
        "throughput": round(sum(throughputs)/len(throughputs), 4),
        "fairness": round(sum(fairnesses)/len(fairnesses), 4)
    }


# -----------------------------
# RUN ALL STRATEGIES
# -----------------------------
def run_all():

    results = []

    results.append(run_simulation(RandomSelector, "Random"))
    results.append(run_simulation(RoundRobinSelector, "RoundRobin"))
    results.append(run_simulation(TrustSelector, "Trust"))
    results.append(run_simulation(GWOSelector, "GWO"))

    df = pd.DataFrame(results)

    df.to_csv("final_results.csv", index=False)

    print("\n===== FINAL RESULTS =====")
    print(df)


# -----------------------------
# MAIN
# -----------------------------
if __name__ == "__main__":
    run_all()

