class TrustManager:
    """
    Trust computation module for validators.


    Combines:
    - Success rate
    - Latency
    - Energy efficiency
    - Load balancing
    - Stability (consistency)


    Includes:
    - Recovery boost (for low-trust validators)
    - Domination control (prevents monopolies)
    - Temporal smoothing (stability over time)
    """


    def __init__(self, validators):


        # ---------------------------
        # STORE VALIDATORS
        # ---------------------------
        self.validators = validators


        # Initialize trust scores
        self.trust_scores = {v: 0.5 for v in validators}


        # ---------------------------
        # WEIGHTS (CORE DESIGN)
        # ---------------------------
        self.w_success = 0.4
        self.w_latency = 0.2
        self.w_energy = 0.15
        self.w_load = 0.15
        self.w_consistency = 0.1


        # ---------------------------
        # TRUST BOUNDS
        # ---------------------------
        self.min_trust = 0.1
        self.max_trust = 1.0


    # ---------------------------
    # GET TRUST SCORES
    # ---------------------------
    def get_trust_scores(self):
        return self.trust_scores


    # ---------------------------
    # COMPUTE TRUST (CORE LOGIC)
    # ---------------------------
    def compute_trust(self, validator):


        # ---------------------------
        # PERFORMANCE METRICS
        # ---------------------------
        success_rate = validator.get_success_rate()


        latency_score = 1 - validator.latency
        energy_score = 1 - validator.energy


        load_score = 1 - validator.get_load_score()


        # ---------------------------
        # CONSISTENCY (STABILITY)
        # Penalizes deviation from balanced load
        # ---------------------------
        consistency = max(0, 1 - abs(validator.current_load - 5) / 10)


        # ---------------------------
        # BASE TRUST CALCULATION
        # ---------------------------
        base_trust = (
            self.w_success * success_rate +
            self.w_latency * latency_score +
            self.w_energy * energy_score +
            self.w_load * load_score +
            self.w_consistency * consistency
        )


        # ---------------------------
        # RECOVERY BOOST (FAIRNESS FIX)
        # Helps low-trust validators recover
        # ---------------------------
        current_trust = self.trust_scores[validator.validator_id]


        if current_trust < 0.5:
            recovery = 0.05 * (0.5 - current_trust)
        else:
            recovery = 0


        # ---------------------------
        # DOMINATION CONTROL
        # Prevents high-trust monopolies
        # ---------------------------
        if current_trust > 0.8:
            penalty = 0.05 * (current_trust - 0.8)
        else:
            penalty = 0


        # ---------------------------
        # FINAL TRUST VALUE
        # ---------------------------
        trust = base_trust + recovery - penalty


        return max(self.min_trust, min(self.max_trust, trust))


    # ---------------------------
    # UPDATE ALL TRUST VALUES
    # ---------------------------
    def update_all_trust(self, validator_network):


        for validator in validator_network.get_validators():


            new_trust = self.compute_trust(validator)


            # ---------------------------
            # TEMPORAL SMOOTHING (KEY)
            # Prevents sudden fluctuations
            # ---------------------------
            old_trust = self.trust_scores[validator.validator_id]
            smoothed_trust = 0.7 * old_trust + 0.3 * new_trust


            self.trust_scores[validator.validator_id] = smoothed_trust
