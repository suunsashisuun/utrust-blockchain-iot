class TrustManager:

    def __init__(self, validators):

        # initialize trust for all validators dynamically
        self.trust_scores = {v: 0.5 for v in validators}

        self.reward = 0.05
        self.penalty = 0.07
        self.decay = 0.01

        # recovery prevents permanent starvation
        self.recovery = 0.005

        # minimum trust floor
        self.min_trust = 0.1

        # maximum trust cap
        self.max_trust = 1.0


    def get_trust_scores(self):
        return self.trust_scores


    def get_highest_trust_peer(self):
        return max(self.trust_scores, key=lambda p: self.trust_scores[p])


    def update_trust(self, selected_peer, success=True):

        for peer in self.trust_scores:

            if peer == selected_peer:

                if success:
                    self.trust_scores[peer] = min(
                        self.max_trust,
                        self.trust_scores[peer] + self.reward
                    )

                else:
                    self.trust_scores[peer] = max(
                        self.min_trust,
                        self.trust_scores[peer] - self.penalty
                    )

            else:
                # reputation aging
                decayed = self.trust_scores[peer] - self.decay

                # recovery mechanism
                recovered = decayed + self.recovery

                self.trust_scores[peer] = max(
                    self.min_trust,
                    min(self.max_trust, recovered)
                )