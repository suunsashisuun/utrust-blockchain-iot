from flask import Flask, jsonify, render_template
import threading
import simpy
import pandas as pd
import time
import random


from z_dashboard.state import state
from z_dashboard.state import get_initial_state


import sys
import os


# ---------------------------
# PATH SETUP
# ---------------------------
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


# ---------------------------
# ENGINE + COMPONENTS
# ---------------------------
from g_simulation.simpy_engine import run_simulation
from e_consensus.scheduler import scheduler_with_selector
from e_consensus.gwo_selector import GWOSelector


# ---------------------------
# METRICS
# ---------------------------
from h_metrics.metrics import reset_metrics


# ---------------------------
# CONFIG
# ---------------------------
from config import DEMO_MODE, DEMO_SEED, DEBUG, DEBUG_IMPORTANT, NUM_VALIDATORS


# ---------------------------
# APP INIT
# ---------------------------
app = Flask(__name__)


# ---------------------------
# GLOBAL STATE
# ---------------------------
simulation_thread = None
running = False


env = None
blockchain = None
validator_network = None




# ---------------------------
# SIMULATION LOOP (CORE ENGINE)
# ---------------------------
def run_sim():
    global running, env, blockchain, validator_network


    # ---------------------------
    # DEMO MODE (DETERMINISTIC)
    # ---------------------------
    if DEMO_MODE:
        random.seed(DEMO_SEED)


    # ---------------------------
    # CREATE SIMULATION ONCE
    # ---------------------------
    if env is None:
        env = simpy.Environment()


        blockchain, validator_network = run_simulation(
            env,
            scheduler_with_selector,
            GWOSelector,
            num_validators=NUM_VALIDATORS,
            use_ml=True
        )


        # Warm start (avoids blank dashboard)
        env.run(until=1)


    # ---------------------------
    # CONTINUOUS LOOP
    # ---------------------------
    while True:
        if running:
            try:
                env.run(until=env.now + 1)
            except Exception as e:
                print("Simulation stopped due to error:", e)
                break


        time.sleep(0.1)




# ---------------------------
# ROUTES
# ---------------------------
@app.route("/")
def index():
    return render_template("index.html")




# ---------------------------
# STATE API
# ---------------------------
@app.route("/state")
def get_state():
    if DEBUG:
        print("APP STATE ID:", id(state))
        print("STATE", state)


    return jsonify(state)




# ---------------------------
# START (RESUME)
# ---------------------------
@app.route("/start")
def start():
    global simulation_thread, running


    print("START CALLED")


    if running:
        return "Already running"


    running = True
    state["running"] = True


    # Start thread only once
    if simulation_thread is None:
        simulation_thread = threading.Thread(target=run_sim)
        simulation_thread.daemon = True
        simulation_thread.start()


    return "Started"




# ---------------------------
# STOP (PAUSE)
# ---------------------------
@app.route("/stop")
def stop():
    global running


    running = False
    state["running"] = False


    print("STOP CALLED")


    return "Stopped"




# ---------------------------
# RESET (FULL RESTART)
# ---------------------------
@app.route("/reset")
def reset():
    global env, blockchain, validator_network, simulation_thread, running


    print("RESET CALLED")


    # Stop simulation
    running = False


    # Reset simulation objects
    env = None
    blockchain = None
    validator_network = None
    simulation_thread = None


    # Reset metrics
    reset_metrics()


    # Reset dashboard state safely
    new_state = get_initial_state()
    state.clear()
    state.update(new_state)


    return "Reset"




# ---------------------------
# COMPARISON API
# ---------------------------
@app.route("/comparison")
def get_comparison():
    df = pd.read_csv("final_results.csv")


    def get_val(row, key):
        if key + "_mean" in df.columns:
            return row[key + "_mean"]
        return row[key]


    try:
        baseline = df[df["strategy"] == "Random"].iloc[0]
        utrust = df[df["strategy"].str.contains("UTrust")].iloc[0]


        improvement = {
            "fairness_gain": round(
                get_val(utrust, "fairness") - get_val(baseline, "fairness"), 4
            ),
            "latency_diff": round(
                get_val(utrust, "latency") - get_val(baseline, "latency"), 4
            )
        }


    except Exception:
        improvement = {
            "fairness_gain": 0,
            "latency_diff": 0
        }


    return {
        "data": df.to_dict(orient="records"),
        "insight": improvement
    }




# ---------------------------
# MAIN
# ---------------------------
if __name__ == "__main__":
    app.run(debug=True)
