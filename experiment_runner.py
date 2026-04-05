import random
import time
import pandas as pd

from validator_network import ValidatorNetwork
from blockchain import Blockchain
from baseline_consensus import BaselineConsensus
from utrust_consensus import UTrustConsensus
from urgency_classifier import UrgencyClassifier


# -----------------------------
# SIMULATION PARAMETERS
# -----------------------------

NUM_TRANSACTIONS = 500
BLOCK_SIZE = 5
NUM_VALIDATORS = 50


# -----------------------------
# CREATE VALIDATOR NETWORK
# -----------------------------

network = ValidatorNetwork(NUM_VALIDATORS)

validator_objects = network.get_validators()

validator_ids = [v.validator_id for v in validator_objects]


# -----------------------------
# BASELINE SYSTEM
# -----------------------------

baseline_consensus = BaselineConsensus(validator_ids)
baseline_blockchain = Blockchain(block_size=BLOCK_SIZE)

baseline_times = []


# -----------------------------
# UTRUST SYSTEM
# -----------------------------

utrust = UTrustConsensus()

utrust_times = []


# -----------------------------
# RUN EXPERIMENT
# -----------------------------

for i in range(NUM_TRANSACTIONS):

    device_id = random.randint(1, 20)
    gas_value = random.randint(20, 100)

    # -------------------------
    # BASELINE CONSENSUS TEST
    # -------------------------

    start = time.time()

    validator = baseline_consensus.select_validator()

    transaction = {
        "device": device_id,
        "gas": gas_value
    }

    baseline_blockchain.add_transaction(validator, transaction)

    end = time.time()

    baseline_times.append(end - start)


    # -------------------------
    # UTRUST CONSENSUS TEST
    # -------------------------

    start = time.time()

    utrust.process_transaction(device_id, gas_value)

    end = time.time()

    utrust_times.append(end - start)


# -----------------------------
# CALCULATE RESULTS
# -----------------------------

baseline_avg = sum(baseline_times) / len(baseline_times)
utrust_avg = sum(utrust_times) / len(utrust_times)

print("\n================================")
print("EXPERIMENT RESULTS")
print("================================")

print("Total Transactions:", NUM_TRANSACTIONS)
print("Validators:", NUM_VALIDATORS)

print("\nBaseline Avg Latency:", baseline_avg)
print("U-Trust Avg Latency:", utrust_avg)


# -----------------------------
# SAVE RESULTS
# -----------------------------

results = pd.DataFrame({
    "Baseline_Time": baseline_times,
    "UTrust_Time": utrust_times
})

results.to_csv("experiment_results.csv", index=False)

print("\nResults saved to experiment_results.csv")