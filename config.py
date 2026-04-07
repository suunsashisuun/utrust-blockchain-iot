# ---------------------------
# DEBUG
# ---------------------------
DEBUG = False          # general logs OFF
DEBUG_IMPORTANT = False # only critical logs ON


# ---------------------------
# MODE SWITCH
# ---------------------------
MODE = "DEMO"   # change to "EVAL" for final results


# ---------------------------
# COMMON
# ---------------------------
NUM_VALIDATORS = 50


# ---------------------------
# DEMO MODE (FAST)
# ---------------------------
if MODE == "DEMO":
    RUNS = 3
    SIM_TIME = 50
    DEMO_MODE = True
    DEMO_SEED = 42


# ---------------------------
# EVALUATION MODE (FINAL)
# ---------------------------
elif MODE == "EVAL":
    RUNS = 10
    SIM_TIME = 80
    DEMO_MODE = False
    DEMO_SEED = None
