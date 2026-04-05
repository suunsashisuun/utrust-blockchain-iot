
from e_consensus.domain_selector import DomainSelector
from e_consensus.pbft_engine import PBFTConsensus
from h_metrics.metrics import average_latency, throughput, fairness_index
from z_dashboard.state import state
from z_dashboard.state import DEBUG, DEBUG_IMPORTANT



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
        if DEBUG_IMPORTANT:
            print("SCHEDULER STATE ID:", id(state))
            print("Scheduler LOOP RUNNING")   # 🔥 ADD HERE


      # ---------------------------
        # PRIORITY QUEUE (FINAL FIX)
        # ---------------------------
        if urgent_queue.items:
            event = yield urgent_queue.get()
            if DEBUG_IMPORTANT:
                print("🚨 URGENT EVENT PICKED:", event)
            state["processed_urgent"] += 1

        elif normal_queue.items:
            event = yield normal_queue.get()
            if DEBUG_IMPORTANT:
                print("📦 NORMAL EVENT PICKED:", event)
            state["processed_normal"] += 1

        else:
            yield env.timeout(0.05)
            continue


        # UPDATE QUEUE STATE AFTER PICK
        state["urgent_queue_size"] = len(urgent_queue.items)
        state["normal_queue_size"] = len(normal_queue.items)

        if DEBUG_IMPORTANT:
            print("QUEUE SIZES:", state["urgent_queue_size"], state["normal_queue_size"])


        device = event["device_id"]
        gas = event["gas"]
        urgency = event["urgency"]
        state["last_processed_event"] = event

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

        state["domain_size"] = len(consensus_group)

        if DEBUG:
            print("DOMAIN SIZE:", state["domain_size"])   # 🔥 DEBUG

        state["trust_scores"] = trust_scores

        # ---------------------------
        # GWO SELECTOR (PROPOSER)
        # ---------------------------
        selected_validator = selector.select_validator(
            consensus_group,   # 🔥 IMPORTANT: domain only
            trust_scores,
            urgency_weight
        )

        state["selected_validator"] = selected_validator
        if DEBUG:
            print("SELECTED VALIDATOR:", selected_validator)   # 🔥 DEBUG

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


        state["consensus_result"] = consensus_success
        if DEBUG:
            print("CONSENSUS RESULT:", consensus_success)   # 🔥 DEBUG


        # ---------------------------
        # PROCESS RESULT
        # ---------------------------
        if consensus_success:


            validator_obj.process_transaction(success=True)


            yield env.timeout(validator_obj.latency)


            # reduce load after execution
           # validator_obj.decay_load() #instant decay isnt accumulating load
           


            new_block = blockchain.add_transaction(selected_validator, event, consensus_success)

            if new_block:
                state["blocks"] = max(0, len(blockchain.chain) - 1)



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

        #update metrics first 

        state["latency"] = average_latency()
        state["throughput"] = throughput(env.now)
        state["fairness"] = fairness_index(validator_network.get_validators())

        if DEBUG:
            print("METRICS:", state["latency"], state["throughput"], state["fairness"])  # 🔥 DEBUG

        #then store history

        state["fairness_history"] = state["fairness_history"][-50:] + [state["fairness"]]
        state["latency_history"] = state["latency_history"][-50:] + [state["latency"]]
        
        state["validator_loads"] = {
            v.validator_id: v.processed_transactions
            for v in validator_network.get_validators()
        }

        # ---------------------------
        # TRUST UPDATE (CRITICAL)
        # ---------------------------
       # trust_manager.update_trust(selected_validator, consensus_success)
 
