def build_transaction(device_id, gas_value, urgency, timestamp, previous_value=None):

    # ---------------------------
    # DELTA CALCULATION
    # ---------------------------
    delta = 0
    if previous_value is not None:
        delta = gas_value - previous_value

    # ---------------------------
    # TRANSACTION OBJECT
    # ---------------------------
    transaction = {
        "device_id": device_id,
        "gas": gas_value,
        "urgency": urgency,
        "timestamp": timestamp,
        "delta": delta
    }

    return transaction
