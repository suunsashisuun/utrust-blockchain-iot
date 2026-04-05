# ---------------------------
# INITIAL STATE TEMPLATE
# (Single Source of Truth)
# ---------------------------
def get_initial_state():
    return {
        # ---------------------------
        # IoT
        # ---------------------------
        "last_events": [],
        "processed_urgent": 0,
        "processed_normal": 0,
        "last_processed_event": None,


        # ---------------------------
        # QUEUES
        # ---------------------------
        "urgent_queue_size": 0,
        "normal_queue_size": 0,


        # ---------------------------
        # CONSENSUS
        # ---------------------------
        "domain_size": 0,
        "selected_validator": "N/A",
        "consensus_result": False,


        # ---------------------------
        # TRUST
        # ---------------------------
        "trust_scores": {},


        # ---------------------------
        # BLOCKCHAIN
        # ---------------------------
        "blocks": 0,


        # ---------------------------
        # METRICS
        # ---------------------------
        "latency": 0.0,
        "throughput": 0.0,
        "fairness": 0.0,


        # ---------------------------
        # HISTORY TRACKING
        # ---------------------------
        "fairness_history": [0.0],
        "latency_history": [0.0],


        # ---------------------------
        # VALIDATOR LOAD
        # ---------------------------
        "validator_loads": {},


        # ---------------------------
        # TRACE
        # ---------------------------
        "event_trace": [],


        # ---------------------------
        # DASHBOARD DETAILS
        # ---------------------------
        "last_classification": {},
        "validator_decision": {},
        "consensus_info": {},


        # ---------------------------
        # SYSTEM STATE
        # ---------------------------
        "running": False
    }




# ---------------------------
# GLOBAL STATE (INITIALIZED ONCE)
# ---------------------------
state = get_initial_state()
