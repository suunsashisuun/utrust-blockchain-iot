import sys
import os


# ---------------------------
# PATH SETUP (for module imports)
# ---------------------------
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


import simpy


# ---------------------------
# MODULE IMPORTS
# ---------------------------
from a_iot.simulation import GasSensorModel
from b_processing.urgency_classifier import UrgencyClassifier
from b_processing.transaction_builder import build_transaction


from c_network.validator_network import ValidatorNetwork
from d_trust.trust_manager import TrustManager


from f_blockchain.blockchain import Blockchain


from e_consensus.scheduler import scheduler_with_selector
from e_consensus.gwo_selector import GWOSelector


from h_metrics.metrics import record_transaction


from z_dashboard.state import state


from config import DEMO_MODE, DEMO_SEED, DEBUG, DEBUG_IMPORTANT




# ---------------------------
# LOAD DECAY PROCESS
# Periodically reduces validator load to avoid saturation
# ---------------------------
def decay_process(env, validator_network):
    while True:
        yield env.timeout(5)  # decay interval


        for validator in validator_network.get_validators():
            validator.decay_load()




# ---------------------------
# SENSOR INITIALIZATION
# Creates IoT gas sensors with varying risk levels
# ---------------------------
def create_sensors():
    sensors = []


    for sensor_id in range(1, 11):
        base = 20 + sensor_id
        risk = 0.05 + (sensor_id * 0.04)


        sensors.append(GasSensorModel(sensor_id, base, risk))


    return sensors




# ---------------------------
# IOT EVENT GENERATOR
# Continuously generates sensor events and routes to queues
# ---------------------------
def iot_generator(env, sensors, classifier, urgent_queue, normal_queue, use_ml):


    while True:
        for sensor in sensors:


            # Generate sensor reading
            sensor_values = sensor.generate_reading()


            # ---------------------------
            # URGENCY CLASSIFICATION
            # ---------------------------
            if use_ml:
                urgency, confidence = classifier.classify_with_confidence(
                    sensor.device_id,
                    sensor_values
                )


                # Update dashboard state
                state["last_classification"] = {
                    "gas": sum(sensor_values) / len(sensor_values),
                    "result": urgency,
                    "confidence": round(confidence, 3)
                }
            else:
                urgency = "NORMAL"


            # ---------------------------
            # BUILD TRANSACTION
            # ---------------------------
            gas = sum(sensor_values) / len(sensor_values)


            event = build_transaction(
                sensor.device_id,
                gas,
                urgency,
                env.now
            )


            # Maintain last 20 events for dashboard
            state["last_events"] = state["last_events"][-20:] + [event]


            # ---------------------------
            # DEBUG LOGGING
            # ---------------------------
            if DEBUG_IMPORTANT:
                print("EVENT BEFORE QUEUE:", event)
                print("TYPE OF URGENCY:", type(event["urgency"]))


            # Normalize urgency
            urgency = str(event["urgency"]).strip().upper()


            if DEBUG_IMPORTANT:
                print("RAW EVENT:", event)
                print("FINAL URGENCY USED:", urgency)


            # ---------------------------
            # QUEUE ROUTING
            # ---------------------------
            if urgency == "CRITICAL":
                if DEBUG_IMPORTANT:
                    print("➡️ SENT TO URGENT QUEUE")


                yield urgent_queue.put(event)


            else:
                if DEBUG_IMPORTANT:
                    print("➡️ SENT TO NORMAL QUEUE")


                yield normal_queue.put(event)


        # Control event generation rate
        yield env.timeout(1)




# ---------------------------
# MAIN SIMULATION RUNNER
# Initializes full simulation pipeline
# ---------------------------
def run_simulation(
    env,
    scheduler_func,
    selector_class,
    num_validators=50,
    use_ml=True
):


    # ---------------------------
    # INITIAL SETUP
    # ---------------------------
    sensors = create_sensors()
    classifier = UrgencyClassifier()


    urgent_queue = simpy.Store(env)
    normal_queue = simpy.Store(env)


    validator_network = ValidatorNetwork(num_validators)
    validator_ids = [v.validator_id for v in validator_network.get_validators()]


    trust_manager = TrustManager(validator_ids)


    selector = selector_class()


    blockchain = Blockchain(block_size=5)


    # ---------------------------
    # START IOT PROCESS
    # ---------------------------
    env.process(
        iot_generator(
            env,
            sensors,
            classifier,
            urgent_queue,
            normal_queue,
            use_ml
        )
    )


    # ---------------------------
    # START SCHEDULER
    # Handles both baseline and advanced pipelines
    # ---------------------------
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


    # ---------------------------
    # START LOAD DECAY
    # ---------------------------
    env.process(decay_process(env, validator_network))


    return blockchain, validator_network
