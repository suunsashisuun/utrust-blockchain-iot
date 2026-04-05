

DEBUG = False          # general logs OFF
DEBUG_IMPORTANT = False # only critical logs ON

state = {
    # IoT
    "last_events": [],
    "processed_urgent": 0,
    "processed_normal": 0,
    "last_processed_event": None,
    # queues
    "urgent_queue_size": 0,
    "normal_queue_size": 0,

    # consensus
    "domain_size": 0,
    "selected_validator": "N/A",   # 🔥 FIXED
    "consensus_result": False,     # 🔥 FIXED

    # trust
    "trust_scores": {},

    # blockchain
    "blocks": 0,

    # metrics
    "latency": 0.0,
    "throughput": 0.0,
    "fairness": 0.0,

    # time-series tracking
    "fairness_history": [0.0],     # 🔥 better init
    "latency_history": [0.0],

    # validator load
    "validator_loads": {},

    
    "event_trace": [],

    # 🔥 NEW
    "last_classification": {},
    "validator_decision": {},
    "consensus_info": {},

}
def get_initial_state():
    return {
        "last_events": [],
        "processed_urgent": 0,
        "processed_normal": 0,
        "last_processed_event": None,


        "urgent_queue_size": 0,
        "normal_queue_size": 0,


        "domain_size": 0,
        "selected_validator": "N/A",
        "consensus_result": False,


        "trust_scores": {},


        "blocks": 0,


        "latency": 0.0,
        "throughput": 0.0,
        "fairness": 0.0,


        "fairness_history": [0.0],
        "latency_history": [0.0],


        "validator_loads": {},


        "event_trace": [],


        "last_classification": {},
        "validator_decision": {},
        "consensus_info": {},


        "running": False
    }

state["running"] = False

