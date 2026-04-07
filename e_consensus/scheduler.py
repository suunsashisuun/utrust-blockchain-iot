from e_consensus.domain_selector import DomainSelector
from e_consensus.pbft_engine import PBFTConsensus
from h_metrics.metrics import average_latency, throughput, fairness_index
from z_dashboard.state import state
from h_metrics.metrics import record_validator_usage


from config import DEMO_MODE, DEMO_SEED, DEBUG, DEBUG_IMPORTANT


# ---------------------------
# MAIN SCHEDULER WITH SELECTOR
# Handles:
# - Queue prioritization
# - Domain selection (GT-BFT)
# - GWO proposer selection
# - PBFT consensus
# - Metrics + state updates
# ---------------------------

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


    # ---------------------------
    # INITIALIZE COMPONENTS
    # ---------------------------
    domain_selector = DomainSelector(alpha=0.3)
    pbft = PBFTConsensus(committee_size=7)


    while True:


        # ---------------------------
        # DEBUG ENTRY
        # ---------------------------
        if DEBUG_IMPORTANT:
            print("SCHEDULER STATE ID:", id(state))
            print("Scheduler LOOP RUNNING")


        # ---------------------------
        # PRIORITY QUEUE HANDLING
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
            # No events → wait briefly
            yield env.timeout(0.05)
            continue


        # ---------------------------
        # UPDATE QUEUE STATE
        # ---------------------------
        state["urgent_queue_size"] = len(urgent_queue.items)
        state["normal_queue_size"] = len(normal_queue.items)


        if DEBUG_IMPORTANT:
            print("QUEUE SIZES:", state["urgent_queue_size"], state["normal_queue_size"])


        # ---------------------------
        # EXTRACT EVENT DATA
        # ---------------------------
        device = event["device_id"]
        gas = event["gas"]
        urgency = event["urgency"]


        state["last_processed_event"] = event


        # ---------------------------
        # NETWORK FLUCTUATION
        # Simulates real-world instability
        # ---------------------------
        for validator in validator_network.get_validators():
            validator.fluctuate()


        # ---------------------------
        # TRUST UPDATE
        # ---------------------------
        trust_manager.update_all_trust(validator_network)
        trust_scores = trust_manager.get_trust_scores()


        # ---------------------------
        # URGENCY → NUMERIC WEIGHT
        # ---------------------------
        if urgency == "CRITICAL":
            urgency_weight = 1.0
        elif urgency == "WARNING":
            urgency_weight = 0.6
        else:
            urgency_weight = 0.2


        # ---------------------------
        # DOMAIN SELECTION (GT-BFT)
        # ---------------------------
        validators = validator_network.get_validators()


        consensus_group = domain_selector.select_domain(
            validators,
            trust_scores
        )
        # ---------------------------
        # ACTIVE VALIDATOR COUNT (NEW METRIC)
        # ---------------------------
        
        active_validators = len(consensus_group)

        # dashboard
        state["active_validators"] = active_validators  #selected subset

        # 🔥 CRITICAL: record for experiments
        record_validator_usage(active_validators)



        state["domain_size"] = len(consensus_group)  #total network


        if DEBUG:
            print("DOMAIN SIZE:", state["domain_size"])


        state["trust_scores"] = trust_scores


        # ---------------------------
        # GWO VALIDATOR SELECTION
        # ---------------------------
        selected_validator = selector.select_validator(
            consensus_group,
            trust_scores,
            urgency_weight
        )


        state["validator_decision"] = {
            "selected": selected_validator,
            "reason": "High trust & low load"
        }


        state["selected_validator"] = selected_validator


        if DEBUG:
            print("SELECTED VALIDATOR:", selected_validator)


        validator_obj = validator_network.get_validator_by_id(selected_validator)


        # ---------------------------
        # START TIMING
        # ---------------------------
        start_time = env.now


        # ---------------------------
        # PBFT CONSENSUS
        # ---------------------------
        consensus_success = pbft.run_consensus(
            selected_validator,
            consensus_group,
            trust_scores
        )


        state["consensus_result"] = consensus_success


        if DEBUG:
            print("CONSENSUS RESULT:", consensus_success)


        # ---------------------------
        # TRACE LOG (LAST 5 EVENTS)
        # ---------------------------
        trace_entry = {
            "device": event["device_id"],
            "gas": event["gas"],
            "urgency": event["urgency"],
            "validator": selected_validator,
            "result": consensus_success
        }


        state["event_trace"].append(trace_entry)
        state["event_trace"] = state["event_trace"][-5:]


        # ---------------------------
        # PROCESS RESULT
        # ---------------------------
        if consensus_success:


            validator_obj.process_transaction(success=True)


            # Simulate processing delay
            yield env.timeout(validator_obj.latency)


            # Add block
            new_block = blockchain.add_transaction(
                selected_validator,
                event,
                consensus_success
            )


            if new_block:
                state["blocks"] = max(0, len(blockchain.chain) - 1)


        else:
            # Failed consensus path
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


        state["latency"] = average_latency()
        state["throughput"] = throughput(env.now)
        state["fairness"] = fairness_index(
            validator_network.get_validators()
        )


        if DEBUG:
            print(
                "METRICS:",
                state["latency"],
                state["throughput"],
                state["fairness"]
            )


        # ---------------------------
        # STORE HISTORY
        # ---------------------------
        state["fairness_history"] = (
            state["fairness_history"][-50:] + [state["fairness"]]
        )


        state["latency_history"] = (
            state["latency_history"][-50:] + [state["latency"]]
        )


        # ---------------------------
        # VALIDATOR LOAD TRACKING
        # ---------------------------
        state["validator_loads"] = {
            validator.validator_id: validator.processed_transactions
            for validator in validator_network.get_validators()
        }


        # ---------------------------
        # OPTIONAL TRUST UPDATE (DISABLED)
        # ---------------------------
        # trust_manager.update_trust(selected_validator, consensus_success)
