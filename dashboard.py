import streamlit as st
import pandas as pd
import time
import random
import numpy as np
from simulation import GasSensorModel
from utrust_consensus import UTrustConsensus
from transaction_pool import TransactionPool

st.set_page_config(page_title="IoT Monitoring System", layout="wide")


# -----------------------
# STYLE
# -----------------------

st.markdown("""
<style>
.stApp {
    background: linear-gradient(180deg,#06172d,#0b2c55);
}

.block-container > div {
    background:white;
    padding:20px;
    border-radius:10px;
    margin-bottom:20px;
}

[data-testid="metric-container"] {
    background:white;
    border-radius:10px;
    padding:20px;
}

h1 {font-size:70px !important;}
h2 {font-size:32px !important;}
</style>
""", unsafe_allow_html=True)


st.markdown("<h1 style='text-align:center;'>IoT Monitoring System</h1>", unsafe_allow_html=True)


# -----------------------
# SESSION STATE
# -----------------------

if "running" not in st.session_state:
    st.session_state.running = False

if "urgent_queue" not in st.session_state:
    st.session_state.urgent_queue = []

if "normal_queue" not in st.session_state:
    st.session_state.normal_queue = []

if "tx_log" not in st.session_state:
    st.session_state.tx_log = []

if "validator_load" not in st.session_state:
    st.session_state.validator_load = {}

if "trust_history" not in st.session_state:
    st.session_state.trust_history = []

if "urgent_count" not in st.session_state:
    st.session_state.urgent_count = 0

if "normal_count" not in st.session_state:
    st.session_state.normal_count = 0

if "latencies" not in st.session_state:
    st.session_state.latencies = []
    
if "validator_history" not in st.session_state:
    st.session_state.validator_history = []
# -----------------------
# CONSENSUS ENGINE
# -----------------------

#consensus = UTrustConsensus()
if "consensus" not in st.session_state:
    st.session_state.consensus = UTrustConsensus()

consensus = st.session_state.consensus
tx_pool = TransactionPool()
# -----------------------
# CONTROL BAR
# -----------------------

c1,c2,c3 = st.columns([3,1,3])

with c2:
    start = st.button("Start Simulation")

with c3:
    stop = st.button("Stop Simulation")


if start:

    st.session_state.running = True

    # reset simulation state
    st.session_state.urgent_queue = []
    st.session_state.normal_queue = []
    st.session_state.tx_log = []
    st.session_state.validator_load = {}
    st.session_state.trust_history = []
    st.session_state.validator_history = []
    st.session_state.latencies = []
    st.session_state.urgent_count = 0
    st.session_state.normal_count = 0
    st.session_state.consensus = UTrustConsensus()

if stop:
    st.session_state.running = False


# -----------------------
# CREATE DEVICES
# -----------------------

sensors = []

for i in range(1,11):

    base = 20 + i
    risk = 0.05 + (i * 0.04)

    sensors.append(GasSensorModel(i, base, risk))


# -----------------------
# DASHBOARD LOOP
# -----------------------

if st.session_state.running:

    metric_placeholder = st.empty()
    alert_placeholder = st.empty()
    table_placeholder = st.empty()
    queue_placeholder = st.empty()
    processing_placeholder = st.empty()
    trust_placeholder = st.empty()
    log_placeholder = st.empty()
    chart_placeholder = st.empty()
    pipeline_placeholder = st.empty()

    while st.session_state.running:

        

        rows=[]
        urgent_count=0
        latest_alert=None

        # -------------------
        # SENSOR READINGS
        # -------------------

        for sensor in sensors:

            gas=sensor.generate_reading()

            if gas>=70:

                status="URGENT"
                urgent_count+=1
                latest_alert=(sensor.device_id,gas)

                transaction = {"device": sensor.device_id, "gas": gas}
                tx_pool.add_transaction(transaction)
                st.session_state.urgent_queue.append((sensor.device_id, gas))
            else:

                status="NORMAL"
                transaction = {"device": sensor.device_id, "gas": gas}
                tx_pool.add_transaction(transaction)
                st.session_state.normal_queue.append((sensor.device_id, gas))

            rows.append({
                "Device":sensor.device_id,
                "Gas Value":gas,
                "Status":status
            })

        df=pd.DataFrame(rows)


        # -------------------
        # PROCESS EVENTS
        # -------------------

        processed_events=[]

       

        PROCESS_LIMIT = random.randint(4,8)

        for _ in range(PROCESS_LIMIT):

            if st.session_state.urgent_queue:
                processed_events.append(("URGENT", st.session_state.urgent_queue.pop(0)))

            elif st.session_state.normal_queue:
                processed_events.append(("NORMAL", st.session_state.normal_queue.pop(0)))


        # -------------------
        # METRICS
        # -------------------

        with metric_placeholder.container():

            m1,m2,m3,m4,m5 = st.columns(5)

            m1.metric("Devices", len(df))
            m2.metric("Urgent Devices", urgent_count)
            m3.metric("Urgent Queue", len(st.session_state.urgent_queue))
            m4.metric("Normal Queue", len(st.session_state.normal_queue))
            m5.metric("Transaction Pool", tx_pool.size())

        if st.session_state.latencies:

            avg_latency = sum(st.session_state.latencies) / len(st.session_state.latencies)

            st.metric("Average Consensus Latency (sec)", round(avg_latency,4))

        with pipeline_placeholder.container():

            st.subheader("IoT → Blockchain Processing Pipeline")

            p1,p2,p3,p4 = st.columns(4)

            p1.metric("IoT Events", len(df))

            p2.metric("Transactions in Pool", tx_pool.size())

            p3.metric("Events Processing", len(processed_events))

            blocks_created = len(consensus.blockchain.chain) - 1
            blocks_created = max(blocks_created, 0)

            p4.metric("Blocks Created", blocks_created)
        # -------------------
        # ALERT PANEL
        # -------------------

        with alert_placeholder.container():

            st.subheader("Latest Alert")

            if latest_alert:
                device,value=latest_alert
                st.error(f"Device {device} Gas Level Critical: {value}")
            else:
                st.success("System Normal")


        # -------------------
        # TABLE + GRAPH
        # -------------------

        with table_placeholder.container():

            left,right=st.columns(2)

            with left:

                st.subheader("Device Status")
                st.dataframe(df,use_container_width=True,hide_index=True)

            with right:

                st.subheader("Gas Monitoring")
                chart_data=df.set_index("Device")
                st.line_chart(chart_data["Gas Value"])


        # -------------------
        # QUEUES
        # -------------------

        with queue_placeholder.container():

            q1,q2 = st.columns(2)

            with q1:

                st.subheader("Urgent Queue")
                st.write(len(st.session_state.urgent_queue))

            with q2:

                st.subheader("Normal Queue")
                st.write(len(st.session_state.normal_queue))


        # -------------------
        # PROCESS EVENTS
        # -------------------

        latest_trust=None

        with processing_placeholder.container():

            st.subheader("Processing Events")

            for mode,event in processed_events:

                device,value = event

                transaction = {
                    "device": device,
                    "gas": value
                }

              

                tx = tx_pool.get_transaction()

                if tx:

                    result = consensus.process_transaction(
                        tx["device"],
                        tx["gas"]
                    )

                st.session_state.latencies.append(result["latency"])

                validator = result["validator"]

                # track validator workload
                if validator not in st.session_state.validator_load:
                    st.session_state.validator_load[validator] = 0

                st.session_state.validator_load[validator] += 1

                st.session_state.validator_history.append(
                    dict(st.session_state.validator_load)
                )

                # track urgency distribution
                if value >= 70:
                    st.session_state.urgent_count += 1
                else:
                    st.session_state.normal_count += 1


                # store trust evolution
                st.session_state.trust_history.append(result["trust_scores"])

                st.session_state.tx_log.append({
                    "Device":device,
                    "Gas":value,
                    "Validator":result["validator"]
                })

                if value>=70:
                    st.error(f"URGENT → Validator {result['validator']}")
                else:
                    st.success(f"Normal → Validator {result['validator']}")

                latest_trust=result["trust_scores"]


        # -------------------
        # TRUST TABLE
        # -------------------

        if latest_trust:

            with trust_placeholder.container():

                st.subheader("Validator Trust Scores")

                trust_df=pd.DataFrame(
                    latest_trust.items(),
                    columns=["Validator","Trust"]
                )

                st.dataframe(trust_df,use_container_width=True)


        # -------------------
        # BLOCKCHAIN LOG
        # -------------------

        with log_placeholder.container():

            st.subheader("Blockchain Transaction Log")

            if st.session_state.tx_log:

                log_df=pd.DataFrame(st.session_state.tx_log)

                st.dataframe(
                    log_df.tail(10),
                    height=200,
                    use_container_width=True
                )


        st.subheader("System Status")

        s1,s2,s3,s4 = st.columns(4)

        s1.metric("Total Transactions", len(st.session_state.tx_log))

        s2.metric("Active Validators", len(st.session_state.validator_load))

        s3.metric("Blockchain Height", len(consensus.blockchain.chain))

        s4.metric("Pending Pool Size", tx_pool.size())

        
        st.subheader("System Performance Analysis")

        g1,g2,g3,g4 = st.columns(4)


        # -------------------
        # Validator Load
        # -------------------

        with g1:

            st.subheader("Validator Load Distribution")

            if st.session_state.validator_load:

                load_df = pd.DataFrame(
                    list(st.session_state.validator_load.items()),
                    columns=["Validator","Transactions"]
                ).sort_values(by="Transactions", ascending=False)

                st.bar_chart(load_df.set_index("Validator"))


        # -------------------
        # Urgent vs Normal
        # -------------------

        with g2:

            st.subheader("Urgent vs Normal Transactions")

            urgency_df = pd.DataFrame({
                "Type":["Urgent","Normal"],
                "Count":[
                    st.session_state.urgent_count,
                    st.session_state.normal_count
                ]
            })

            st.bar_chart(urgency_df.set_index("Type"))


        # -------------------
        # Trust Evolution
        # -------------------

        with g3:

            st.subheader("Trust Evolution")

            if st.session_state.trust_history:

                trust_df = pd.DataFrame(st.session_state.trust_history)

                if len(trust_df) > 1:
                    trust_df = trust_df.rolling(5).mean()

                st.line_chart(trust_df)


        with g4:

            st.subheader("Validator Activity Over Time")

            if st.session_state.validator_history:

                history_df = pd.DataFrame(st.session_state.validator_history)

                st.line_chart(history_df)



        st.subheader("Consensus Performance Comparison")

        try:

            results = pd.read_csv("experiment_results.csv")

            comparison_df = pd.DataFrame({
                "Baseline": results["Baseline_Time"],
                "UTrust": results["UTrust_Time"]
            })

            st.line_chart(comparison_df)

        except:
            st.info("Run experiment_runner.py to generate comparison results")



        st.subheader("Validator Fairness Analysis")
        if st.session_state.validator_load:

            load_df = pd.DataFrame(
                list(st.session_state.validator_load.items()),
                columns=["Validator","Transactions"]
            )

            st.bar_chart(load_df.set_index("Validator"))

        loads = np.array(list(st.session_state.validator_load.values()))

        if len(loads) > 0 and np.sum(loads**2) != 0:

            fairness_index = (np.sum(loads) ** 2) / (len(loads) * np.sum(loads ** 2))

            st.metric("Validator Fairness Index", round(fairness_index, 3))

        else:

            st.metric("Validator Fairness Index", "N/A")

        total_tx = len(st.session_state.tx_log)

        elapsed_time = len(st.session_state.tx_log) if len(st.session_state.tx_log) > 0 else 1

        throughput = total_tx / elapsed_time

        st.metric("Network Throughput (Tx/sec)", round(throughput,2))


        st.subheader("Network Scalability Analysis")

        try:

            scale_df = pd.read_csv("scalability_results.csv")

            st.line_chart(scale_df.set_index("Validators"))

        except:
            st.info("Run scalability_test.py to generate results")

            
        time.sleep(2)