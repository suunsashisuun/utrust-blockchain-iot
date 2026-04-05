
import simpy
import pandas as pd

from a_iot.simulation import GasSensorModel
from c_core.validator_network import ValidatorNetwork
from c_core.trust_manager import TrustManager
from c_core.gwo_selector import GWOSelector
from c_core.scheduler import scheduler_with_selector
from d_blockchain.blockchain import Blockchain

from f_experiments.metrics import (
    record_transaction,
    average_latency,
    reset_metrics
)

# ---------------------------
# URGENCY
# ---------------------------
def classify_urgency(gas):
    if gas >= 80:
        return "CRITICAL"
    elif gas >= 60:
        return "WARNING"
    else:
        return "NORMAL"


# ---------------------------
# SENSOR
# ---------------------------
def create_sensors():
    sensors = []
    for i in range(1, 11):
        base = 20 + i
        risk = 0.05 + (i * 0.04)
        sensors.append(GasSensorModel(i, base, risk))
    return sensors


# ---------------------------
# IOT GENERATOR
# ---------------------------
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


# ---------------------------
# RUN ONE SIZE
# ---------------------------
def run_scalability(num_validators):

    env = simpy.Environment()

    sensors = create_sensors()

    urgent_queue = simpy.Store(env)
    normal_queue = simpy.Store(env)

    validator_network = ValidatorNetwork(num_validators=num_validators)
    validators = validator_network.get_validators()
    validator_ids = [v.validator_id for v in validators]

    trust_manager = TrustManager(validator_ids)
    selector = GWOSelector()

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

    return average_latency()


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
        "AvgLatency": latency
    })

df = pd.DataFrame(results)

print("\nScalability Results")
print(df)

df.to_csv("scalability_results.csv", index=False)

