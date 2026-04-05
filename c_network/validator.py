import random

class Validator:
    """
    Represents a validator node in the network.


    Attributes:
    - latency (dynamic)
    - energy (dynamic)
    - load (dynamic)
    - success/failure tracking
    """


    def __init__(self, validator_id):


        self.validator_id = validator_id

        # ---------------------------
        # CORE PROPERTIES
        # ---------------------------
        self.latency = round(random.uniform(0.1, 0.5), 3)
        self.energy = round(random.uniform(0.2, 0.8), 3)


        # ---------------------------
        # PERFORMANCE TRACKING
        # ---------------------------
        self.processed_transactions = 0
        self.successful_transactions = 0
        self.failed_transactions = 0


        # ---------------------------
        # DYNAMIC LOAD
        # ---------------------------
        self.current_load = 0

        # ---------------------------
        # BYZANTINE BEHAVIOR FLAG
        # ---------------------------
        self.is_malicious = (random.random() < 0.1)


    # ---------------------------
    # PROCESS TRANSACTION
    # ---------------------------
    def process_transaction(self, success=True):


        self.processed_transactions += 1
        self.current_load += 1


        if success:
            self.successful_transactions += 1
        else:
            self.failed_transactions += 1


    # ---------------------------
    # SUCCESS RATE
    # ---------------------------
    def get_success_rate(self):


        if self.processed_transactions == 0:
            return 0.5  # neutral default


        return self.successful_transactions / self.processed_transactions


    # ---------------------------
    # LOAD SCORE (NORMALIZED)
    # ---------------------------
    def get_load_score(self):
        return min(1.0, self.current_load / 10)


    # ---------------------------
    # NETWORK FLUCTUATION
    # Simulates real-world variability
    # ---------------------------
    def fluctuate(self):


        self.latency = max(
            0.05,
            min(1.0, self.latency + random.uniform(-0.05, 0.05))
        )


        self.energy = max(
            0.1,
            min(1.0, self.energy + random.uniform(-0.05, 0.05))
        )


    # ---------------------------
    # LOAD DECAY
    # Prevents permanent overload
    # ---------------------------
    def decay_load(self):
        self.current_load = max(0, self.current_load - 1)
