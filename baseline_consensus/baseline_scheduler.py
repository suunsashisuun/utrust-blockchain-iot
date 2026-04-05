def baseline_scheduler(
    env,
    urgent_queue,
    normal_queue,
    selector,
    validator_network,
    blockchain,
    record_transaction
):

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
        # SELECT VALIDATOR (BASELINE)
        # ---------------------------
        selected_validator = selector.select_validator(validators)

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
