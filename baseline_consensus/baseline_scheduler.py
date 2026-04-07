BASELINE_MODE = "default"

def baseline_scheduler(
    env,
    urgent_queue,
    normal_queue,
    selector,
    validator_network,
    blockchain,
    record_transaction,
):
    mode = BASELINE_MODE

    while True:

        # ---------------------------
        # PRIORITY QUEUE
        # ---------------------------
        if len(urgent_queue.items) > 0:
            event = yield urgent_queue.get()
        else:
            event = yield normal_queue.get()

        validators = validator_network.get_validators()

        # ---------------------------
        # BASELINE MODES
        # ---------------------------

        # 🔴 FULL participation BASELINE (ALL VALIDATORS)
        if mode == "full_part":
            selected_validator = selector.select_validator(validators)
            active_validators = len(validators)   # 🔥 KEY METRIC

        # 🟡 Aggressive Trust Selection BASELINE (TOP-K)
        elif mode == "agg_trust":

            # sort by trust-like proxy (low load + low latency)
            sorted_validators = sorted(
                validators,
                key=lambda v: (v.current_load, v.latency)
            )

            top_k = max(3, int(len(validators) * 0.3))  # 30%
            selected_pool = sorted_validators[:top_k]

            selected_validator = selector.select_validator(selected_pool)
            active_validators = len(selected_pool)

        # 🔵 DEFAULT BASELINES (your original ones)
        else:
            selected_validator = selector.select_validator(validators)
            active_validators = len(validators)

        # ---------------------------
        # FETCH VALIDATOR
        # ---------------------------
        validator_obj = validator_network.get_validator_by_id(selected_validator)

        # ---------------------------
        # PROCESS TRANSACTION
        # ---------------------------
        start_time = env.now

        validator_obj.process_transaction()

        yield env.timeout(validator_obj.latency)

        validator_obj.decay_load()

        blockchain.add_transaction(selected_validator, event, True)

        end_time = env.now
        delay = end_time - start_time

        # ---------------------------
        # METRICS
        # ---------------------------
        record_transaction(delay)

        # 🔥 NEW: TRACK VALIDATOR USAGE
        try:
            from h_metrics.metrics import record_validator_usage
            record_validator_usage(active_validators)
        except:
            pass
