class TrustManager:
    def __init__(self):
        self.trust_scores = {
            "peer0.org1": 0.8,
            "peer0.org2": 0.9
        }

    def get_trust_scores(self):
        return self.trust_scores

    def get_highest_trust_peer(self):
        return max(self.trust_scores, key=lambda peer: self.trust_scores[peer])

    def update_trust(self, peer, success=True):
        if peer not in self.trust_scores:
            return
        if success:
            self.trust_scores[peer] = min(1.0, self.trust_scores[peer] + 0.05)
        else:
            self.trust_scores[peer] = max(0.0, self.trust_scores[peer] - 0.05)