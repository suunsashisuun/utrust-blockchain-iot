latencies = []
transaction_count = 0
validator_usage_list = []

# -----------------------------
# RECORD TRANSACTION
# -----------------------------
def record_transaction(delay):
    global transaction_count
    latencies.append(delay)
    transaction_count += 1

# -----------------------------
# LATENCY
# -----------------------------
def average_latency():
    if not latencies:
        return 0
    return sum(latencies) / len(latencies)

# -----------------------------
# THROUGHPUT
# -----------------------------
def throughput(sim_time):
    if sim_time == 0:
        return 0
    return transaction_count / sim_time

# -----------------------------
# FAIRNESS
# -----------------------------
def fairness_index(validators):
    loads = [v.processed_transactions for v in validators]

    if sum(loads) == 0:
        return 0

    numerator = sum(loads) ** 2
    denominator = len(loads) * sum([x**2 for x in loads])

    return numerator / denominator

# -----------------------------
# VALIDATOR USAGE (🔥 NEW METRIC)
# -----------------------------
def record_validator_usage(count):
    validator_usage_list.append(count)

def average_validator_usage():
    if not validator_usage_list:
        return 0
    return sum(validator_usage_list) / len(validator_usage_list)

# -----------------------------
# RESET
# -----------------------------
def reset_metrics():
    global latencies, transaction_count, validator_usage_list
    latencies = []
    transaction_count = 0
    validator_usage_list = []
