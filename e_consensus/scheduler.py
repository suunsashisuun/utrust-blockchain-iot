
from e_consensus.domain_selector import DomainSelector
from e_consensus.pbft_engine import PBFTConsensus




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


    domain_selector = DomainSelector(alpha=0.3)
    pbft = PBFTConsensus(committee_size=5)


    while True:


        # ---------------------------
        # PRIORITY QUEUE
        # ---------------------------
        if len(urgent_queue.items) > 0:
            event = yield urgent_queue.get()
        else:
            event = yield normal_queue.get()


        device = event["device_id"]
        gas = event["gas"]
        urgency = event["urgency"]


        # ---------------------------
        # FLUCTUATE NETWORK
        # ---------------------------
        for v in validator_network.get_validators():
            v.fluctuate()


        # ---------------------------
        # UPDATE TRUST (GLOBAL)
        # ---------------------------
        trust_manager.update_all_trust(validator_network)
        trust_scores = trust_manager.get_trust_scores()
        #TESTING print("Trust:", trust_scores) #DELETE

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
        # CONSENSUS DOMAIN (GT-BFT)
        # ---------------------------
        validators = validator_network.get_validators()


        consensus_group = domain_selector.select_domain(
            validators,
            trust_scores
        )
        
        #TESTING print(f"Domain size: {len(consensus_group)}")#delete
        # ---------------------------
        # GWO SELECTOR (PROPOSER)
        # ---------------------------
        selected_validator = selector.select_validator(
            consensus_group,   # 🔥 IMPORTANT: domain only
            trust_scores,
            urgency_weight
        )
        #TESTING print(f"Selected Validator: {selected_validator}") #delete

        validator_obj = validator_network.get_validator_by_id(selected_validator)


        # ---------------------------
        # START TIMING (FULL PIPELINE)
        # ---------------------------
        start_time = env.now


        # ---------------------------
        # PBFT CONSENSUS (VALIDATE PROPOSER)
        # ---------------------------
        consensus_success = pbft.run_consensus(
            selected_validator,   # 🔥 FIXED
            consensus_group,
            trust_scores
        )

       #TESTING print(f"Consensus Result: {consensus_success}")#delete

        # ---------------------------
        # PROCESS RESULT
        # ---------------------------
        if consensus_success:


            validator_obj.process_transaction(success=True)


            yield env.timeout(validator_obj.latency)


            # reduce load after execution
           # validator_obj.decay_load() #instant decay isnt accumulating load
           


            blockchain.add_transaction(selected_validator, event,consensus_success)


        else:
            # failed consensus
            validator_obj.process_transaction(success=False)


            yield env.timeout(0.05)


        # ---------------------------
        # END TIMING
        # ---------------------------
        end_time = env.now
        delay = end_time - start_time


        # ---------------------------
        # RECORD METRICS
        # ---------------------------
        record_transaction(delay)


        # ---------------------------
        # TRUST UPDATE (CRITICAL)
        # ---------------------------
       # trust_manager.update_trust(selected_validator, consensus_success)
 
