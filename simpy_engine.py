import simpy
from a_iot.simulation import GasSensorModel
from c_core.validator_network import ValidatorNetwork
from c_core.trust_manager import TrustManager
from c_core.gwo_selector import GWOSelector
from d_blockchain.blockchain import Blockchain
from f_experiments.metrics import record_transaction

DEBUG = False


def classify_urgency(gas):

    if gas >= 80:
        return "CRITICAL"
    elif gas >= 60:
        return "WARNING"
    else:
        return "NORMAL"

def create_sensors():
    sensors = []

    for i in range(1, 11):
        base = 20 + i
        risk = 0.05 + (i * 0.04)
        sensors.append(GasSensorModel(i, base, risk))

    return sensors


def create_transaction_pool(env):
    return simpy.Store(env)


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
                if DEBUG:
                    print(f"[{env.now}] URGENT -> Device {sensor.device_id}, Gas {gas}")

            else:
                yield normal_queue.put(event)
                if DEBUG:
                    print(f"[{env.now}] NORMAL -> Device {sensor.device_id}, Gas {gas}")

        yield env.timeout(1)


def scheduler_with_selector(
    env,
    urgent_queue,
    normal_queue,
    selector,
    validator_network,
    trust_manager,
    blockchain,
    record_transaction
):

    while True:

        # priority selection
        if len(urgent_queue.items) > 0:
            event = yield urgent_queue.get()
            priority = "URGENT"
        else:
            event = yield normal_queue.get()
            priority = "NORMAL"

        device = event["device_id"]
        gas = event["gas"]
        urgency = event["urgency"]

        # 🔥 GET TRUST SCORES
        trust_scores = trust_manager.get_trust_scores()

        # 🔥 CONVERT URGENCY → NUMERIC
        if urgency == "CRITICAL":
            urgency_weight = 1.0
        elif urgency == "WARNING":
            urgency_weight = 0.6
        else:
            urgency_weight = 0.2

        # 🔥 SELECT VALIDATOR USING GWO
        validators = validator_network.get_validators()

        selected_validator = selector.select_validator(
            validators,
            trust_scores,
            urgency_weight
        )


        
        transaction=event
   
        # 🔥 GET VALIDATOR OBJECT (IMPORTANT)
        validator_obj = validator_network.get_validator_by_id(selected_validator)


        # simulate processing inside validator
        validator_obj.process_transaction()
        
        proposer = selected_validator
        new_block = blockchain.add_transaction(proposer, transaction)


        if DEBUG:

            print(f"[{env.now}] {priority} -> Device {device}, Gas {gas}")
            print(f"        Selected Validator: {selected_validator}")
            print(f"        Latency: {validator_obj.latency}, Energy: {validator_obj.energy}")
            if new_block:
                print(f"\n BLOCK CREATED by {selected_validator}")
                print(f"   Block Index: {new_block.index}")
                print(f"   Transactions: {len(new_block.transactions)}")
                print(f"   Hash: {new_block.hash[:10]}...\n")



        # 🔥 SIMULATE SUCCESS (temporary)
        import random
        success = random.choice([True, True, True, False])

        # 🔥 UPDATE TRUST
        trust_manager.update_trust(selected_validator, success)

        if DEBUG:

            print(f"        Success: {success}")
            print(f"        Trust: {trust_manager.get_trust_scores()}")

            print(f"        Load: {validator_obj.processed_transactions}")
            print(f"   Total Blocks: {len(blockchain.chain)}")


        start_time = env.now

        yield env.timeout(validator_obj.latency)

        end_time = env.now

        delay = end_time - start_time

        record_transaction(delay)





env = simpy.Environment()

sensors = create_sensors()

urgent_queue = simpy.Store(env)
normal_queue = simpy.Store(env)

validator_network = ValidatorNetwork(num_validators=20)
validators = [v.validator_id for v in validator_network.get_validators()]
trust_manager = TrustManager(validators)

from e_consensus.random_selector import RandomSelector
# from e_consensus.round_robin_selector import RoundRobinSelector
# from e_consensus.trust_selector import TrustSelector
# from c_core.gwo_selector import GWOSelector

selector = RandomSelector()


blockchain = Blockchain(block_size=5)

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

env.run(until=5)


if DEBUG:

    from f_experiments.metrics import average_latency, throughput, fairness_index

    print("\n========== FINAL METRICS ==========")
    print(f"Average Latency: {average_latency():.4f}")
    print(f"Throughput: {throughput(env.now):.4f} tx/sec")
    print(f"Fairness Index: {fairness_index(validator_network.get_validators()):.4f}")
