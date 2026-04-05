from flask import Flask, jsonify, render_template
import threading
import simpy
import pandas as pd
import time

from z_dashboard.state import state
from z_dashboard.state import DEBUG



import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# engine
from g_simulation.simpy_engine import run_simulation
from e_consensus.scheduler import scheduler_with_selector
from e_consensus.gwo_selector import GWOSelector

app = Flask(__name__)

simulation_thread = None
running = False


# ---------------------------
# SIMULATION LOOP
# ---------------------------
    
def run_sim():
    global running

    env = simpy.Environment()

    blockchain, validator_network = run_simulation(
        env,
        scheduler_with_selector,
        GWOSelector,
        num_validators=50,
        use_ml=True
    )

    # 🔥 CRITICAL: kickstart simulation
    env.run(until=1)

    while running:
        if DEBUG:
              print("SIMULATION LOOP RUNNING")   # 🔥 ADD HERE

        try:
            env.run(until=env.now + 1)
            time.sleep(0.1)
        except:
            break



# ---------------------------
# ROUTES
# ---------------------------
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/state")
def get_state():
    if DEBUG:
        print("APP STATE ID:", id(state))  #add debug
    

    if DEBUG:
        print("STATE", state)

    return jsonify(state)



@app.route("/start")
def start():
    global simulation_thread, running

    print("START CALLED")   # 🔥 ADD THIS

    if running:
        print("Already running")
        return "Already running"

    running = True
    state["running"] = True

    simulation_thread = threading.Thread(target=run_sim)
    simulation_thread.daemon = True
    simulation_thread.start()

    return "Started"



@app.route("/stop")
def stop():
    global running
    running = False
    state["running"] = False

    print("STOP CALLED")   # 🔥 ADD THIS

    return "Stopped"


@app.route("/comparison")
def get_comparison():
    df = pd.read_csv("final_results.csv")

    # -----------------------------
    # HANDLE mean/std format safely
    # -----------------------------
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

    except Exception as e:
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
