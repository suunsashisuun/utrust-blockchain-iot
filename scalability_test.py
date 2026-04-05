import time
import random
import pandas as pd

from validator_network import ValidatorNetwork
from utrust_consensus import UTrustConsensus


network_sizes = [50,100,200]

results = []

NUM_TRANSACTIONS = 200


for size in network_sizes:

    print("\nTesting Network Size:", size)

    network = ValidatorNetwork(size)

    utrust = UTrustConsensus()

    times = []

    for i in range(NUM_TRANSACTIONS):

        device = random.randint(1,20)
        gas = random.randint(20,100)

        start = time.time()

        utrust.process_transaction(device,gas)

        end = time.time()

        times.append(end-start)

    avg_latency = sum(times)/len(times)

    results.append({
        "Validators":size,
        "AvgLatency":avg_latency
    })


df = pd.DataFrame(results)

print("\nScalability Results")
print(df)

df.to_csv("scalability_results.csv",index=False)