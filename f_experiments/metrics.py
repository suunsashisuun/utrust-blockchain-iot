latencies = []
transaction_count = 0

def record_transaction(delay):
    global transaction_count
    latencies.append(delay)
    transaction_count += 1

def average_latency():
    if not latencies:
        return 0
    return sum(latencies) / len(latencies)

def throughput(sim_time):
    if sim_time == 0:
        return 0
    return transaction_count / sim_time

def fairness_index(validators):
    loads = [v.processed_transactions for v in validators]

    if sum(loads) == 0:
        return 0

    numerator = sum(loads) ** 2
    denominator = len(loads) * sum([x**2 for x in loads])

    return numerator / denominator

def reset_metrics():
    global latencies, transaction_count
    latencies = []
    transaction_count = 0
