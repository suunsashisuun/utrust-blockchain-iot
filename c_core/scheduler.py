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

        # ---------------------------
        # PRIORITY QUEUE SELECTION
        # ---------------------------
        if len(urgent_queue.items) > 0:
            event = yield urgent_queue.get()
        else:
            event = yield normal_queue.get()

        device = event["device_id"]
        gas = event["gas"]
        urgency = event["urgency"]
        for v in validator_network.get_validators():
            v.fluctuate()

        # ---------------------------
        # TRUST SCORES
        # ---------------------------
        trust_scores = trust_manager.get_trust_scores()

        # ---------------------------
        # URGENCY → NUMERIC
        # ---------------------------
        if urgency == "CRITICAL":
            urgency_weight = 1.0
        elif urgency == "WARNING":
            urgency_weight = 0.6
        else:
            urgency_weight = 0.2

        # ---------------------------
        # VALIDATORS
        # ---------------------------
        validators = validator_network.get_validators()

        # ---------------------------
        # SELECT VALIDATOR (PLUG-IN)
        # ---------------------------
        selected_validator = selector.select_validator(
            validators,
            trust_scores,
            urgency_weight
        )

        validator_obj = validator_network.get_validator_by_id(selected_validator)

        # ---------------------------
        # PROCESS TRANSACTION
        # ---------------------------
        start_time = env.now

        validator_obj.process_transaction()

        yield env.timeout(validator_obj.latency)
                
        validator_obj.current_load = max(
            0,
            validator_obj.current_load - 1
        )


        end_time = env.now

        delay = end_time - start_time


        # ---------------------------
        # RECORD METRICS
        # ---------------------------
        record_transaction(delay)

        # ---------------------------
        # BLOCKCHAIN
        # ---------------------------
        transaction = event

        blockchain.add_transaction(selected_validator, transaction)

        # ---------------------------
        # TRUST UPDATE
        # ---------------------------
        import random
        success = random.choice([True, True, True, False])

        trust_manager.update_trust(selected_validator, success)

