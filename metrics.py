transaction_delays = []

def record_delay(delay):
    transaction_delays.append(delay)

def average_delay():
    if not transaction_delays:
        return 0.0
    return sum(transaction_delays) / len(transaction_delays)