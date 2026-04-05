import subprocess
import time

def submit_transaction():
    command = [
        "peer", "chaincode", "invoke",
        "-o", "localhost:7050",
        "-C", "mychannel",
        "-n", "basic",
        "--isInit",
        "-c", '{"Args":["InitLedger"]}'
    ]

    start_time = time.time()

    subprocess.run(command, capture_output=True, text=True)

    end_time = time.time()

    delay = end_time - start_time
    return delay