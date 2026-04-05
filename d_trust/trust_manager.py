class TrustManager:

    def __init__(self, validators):

        # store validator IDs
        self.validators = validators

        # initialize trust
        self.trust_scores = {v: 0.5 for v in validators}

        # weights (IMPORTANT)
        self.w_success = 0.4
        self.w_latency = 0.2
        self.w_energy = 0.15
        self.w_load = 0.15
        self.w_consistency = 0.1

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

        success_rate = validator.get_success_rate()

        latency_score = 1 - validator.latency
        energy_score = 1 - validator.energy

        load_score = 1 - validator.get_load_score()

        # ---------------------------
        # CONSISTENCY (stability)
        # ---------------------------
        consistency = 1 - abs(validator.current_load - 5) / 10

        # ---------------------------
        # BASE TRUST
        # ---------------------------
        base_trust = (
            self.w_success * success_rate +
            self.w_latency * latency_score +
            self.w_energy * energy_score +
            self.w_load * load_score +
            self.w_consistency * consistency
        )

        # ---------------------------
        # 🔥 RECOVERY BOOST (KEY FIX)
        # ---------------------------
        current_trust = self.trust_scores[validator.validator_id]

        if current_trust < 0.5:
            recovery = 0.05 * (0.5 - current_trust)
        else:
            recovery = 0

        # ---------------------------
        # 🔥 DOMINATION CONTROL (CAP)
        # ---------------------------
        if current_trust > 0.8:
            penalty = 0.05 * (current_trust - 0.8)
        else:
            penalty = 0

        # ---------------------------
        # FINAL TRUST
        # ---------------------------
        trust = base_trust + recovery - penalty

        return max(self.min_trust, min(self.max_trust, trust))

    # ---------------------------
    # UPDATE ALL TRUST VALUES
    # ---------------------------
    def update_all_trust(self, validator_network):

        for validator in validator_network.get_validators():

            new_trust = self.compute_trust(validator)

            self.trust_scores[validator.validator_id] = new_trust

