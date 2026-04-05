import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import simpy

from a_iot.simulation import GasSensorModel
from b_processing.urgency_classifier import UrgencyClassifier
from b_processing.transaction_builder import build_transaction

from c_network.validator_network import ValidatorNetwork
from d_trust.trust_manager import TrustManager

from f_blockchain.blockchain import Blockchain

from e_consensus.scheduler import scheduler_with_selector
from e_consensus.gwo_selector import GWOSelector

from h_metrics.metrics import record_transaction

# ---------------------------
# LOAD DECAY PROCESS (GLOBAL)
# ---------------------------
def decay_process(env, validator_network):
    while True:
        yield env.timeout(5)  # decay every 5 time units

        for v in validator_network.get_validators():
            v.decay_load()



# ---------------------------
# CREATE SENSORS
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
def iot_generator(env, sensors, classifier, urgent_queue, normal_queue):

    while True:

        for sensor in sensors:
           
           sensor_values = sensor.generate_reading()
           
           urgency = classifier.classify(sensor.device_id, sensor_values)
           #print("Urgency:", urgency)

           # OPTIONAL: derive a scalar for logging
           gas = sum(sensor_values) / len(sensor_values)


           event = build_transaction(
                    sensor.device_id,
                    gas,
                    urgency,
                    env.now
                )
           

           if urgency == "CRITICAL":    
        
                yield urgent_queue.put(event)
            
           else:
                yield normal_queue.put(event)

        yield env.timeout(1)


# ---------------------------
# MAIN SIMULATION RUNNER
# ---------------------------
def run_simulation(
    env,
    scheduler_func,
    selector_class,
    num_validators=50
):

    sensors = create_sensors()
    classifier = UrgencyClassifier()

    urgent_queue = simpy.Store(env)
    normal_queue = simpy.Store(env)

    validator_network = ValidatorNetwork(num_validators)
    validator_ids = [v.validator_id for v in validator_network.get_validators()]

    trust_manager = TrustManager(validator_ids)

    selector = selector_class()

    blockchain = Blockchain(block_size=5)

    # IoT process
    env.process(
        iot_generator(
            env,
            sensors,
            classifier,
            urgent_queue,
            normal_queue
        )
    )

    # 🔥 KEY FIX: dynamic scheduler
    if scheduler_func.__name__ == "baseline_scheduler":

        env.process(
            scheduler_func(
                env,
                urgent_queue,
                normal_queue,
                selector,
                validator_network,
                blockchain,
                record_transaction
            )
        )

    else:
        env.process(
            scheduler_func(
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
    env.process(decay_process(env, validator_network))

    return blockchain, validator_network
