import streamlit as st
import time
import pandas as pd
from simulation import GasSensorModel

st.set_page_config(page_title="IoT Gas Monitoring", layout="wide")

st.title("IoT Gas Monitoring Dashboard")

# ---------------------------
# CREATE 10 DEVICES
# ---------------------------

sensors = []

for i in range(1, 11):
    base = 20 + i
    risk = 0.05 + (i * 0.01)
    sensors.append(GasSensorModel(i, base, risk))

# ---------------------------
# QUEUES
# ---------------------------

urgent_queue = []
normal_queue = []

# ---------------------------
# START BUTTON
# ---------------------------

start = st.button("Start Simulation")

if start:

    table_placeholder = st.empty()
    alert_placeholder = st.empty()
    queue_placeholder = st.empty()
    process_placeholder = st.empty()
    chart_placeholder = st.empty()

    latest_alert=None

    for t in range(200):

        rows = []
        urgent_count = 0

        # ---------------------------
        # SENSOR DATA GENERATION
        # ---------------------------

        for sensor in sensors:

            gas = sensor.generate_reading()

            if gas >= 70:
                status = "URGENT"
                urgent_queue.append((sensor.device_id, gas))
                urgent_count += 1
            else:
                status = "NORMAL"
                normal_queue.append((sensor.device_id, gas))

            rows.append({
                "Device": sensor.device_id,
                "Gas Value": gas,
                "Status": status
            })

        df = pd.DataFrame(rows)

        # ---------------------------
        # PRIORITY PROCESSING
        # ---------------------------

        processed_event = None
        processing_type = None

        if urgent_queue:
            processed_event = urgent_queue.pop(0)
            processing_type = "URGENT PRIORITY"

        elif normal_queue:
            processed_event = normal_queue.pop(0)
            processing_type = "NORMAL"

        # ---------------------------
        # UPDATE TABLE
        # ---------------------------

        table_placeholder.subheader("Device Status Table")
        table_placeholder.dataframe(df, hide_index=True)

        # ---------------------------
        # ALERT PANEL
        # ---------------------------

        with alert_placeholder.container():

            st.subheader("Urgent Alerts")

            urgent_devices = df[df["Status"] == "URGENT"]

            if not urgent_devices.empty:
                for _, row in urgent_devices.iterrows():
                    st.error(
                        f"Device {row['Device']} Gas Level Critical: {row['Gas Value']}"
                    )
            else:
                st.success("No urgent alerts")

        # ---------------------------
        # QUEUE STATUS
        # ---------------------------

        with queue_placeholder.container():

            st.subheader("Queue Status")

            st.write("Urgent Queue Size:", len(urgent_queue))
            st.write("Normal Queue Size:", len(normal_queue))

        # ---------------------------
        # CURRENT PROCESSING
        # ---------------------------

        with process_placeholder.container():

            st.subheader("Currently Processed Event")

            if processed_event:
                device, value = processed_event
                st.write(
                    f"Device {device} | Gas Level {value} | Processing Mode: {processing_type}"
                )

        # ---------------------------
        # SINGLE GRAPH (UPDATED)
        # ---------------------------

        chart_placeholder.subheader("Gas Level Graph")

        chart_data = df.set_index("Device")

        chart_placeholder.line_chart(chart_data["Gas Value"])

        time.sleep(1)