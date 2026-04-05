import random


class PBFTConsensus:

    def __init__(self, committee_size=5):
        self.committee_size = committee_size

    def run_consensus(self, proposer_id, consensus_group, trust_scores):

        # ---------------------------
        # BASIC CHECK
        # ---------------------------
        if len(consensus_group) <= 1:
            return False

        # ---------------------------
        # FORM COMMITTEE (EXCLUDE PROPOSER)
        # ---------------------------
        committee_pool = [
            v for v in consensus_group
            if v.validator_id != proposer_id
        ]

        if len(committee_pool) == 0:
            return False

        committee = random.sample(
            committee_pool,
            min(self.committee_size, len(committee_pool))
        )

        # ---------------------------
        # TRUST-AWARE VOTING
        # ---------------------------
        votes = []

        for validator in committee:

            vid = validator.validator_id

            trust = trust_scores.get(vid, 0.5)
            proposer_trust = trust_scores.get(proposer_id, 0.5)

            # ---------------------------
            # VOTE PROBABILITY (BALANCED)
            # ---------------------------
            vote_probability = (
                0.7 * trust +
                0.3 * proposer_trust
            )

            vote_probability = min(1.0, vote_probability + 0.05)

            # ---------------------------
            # BYZANTINE FILTER (SOFT)
            # ---------------------------
            if trust < 0.2:
                vote = False
            else:
                vote = random.random() < vote_probability

            # ---------------------------
            # WEIGHTED VOTE (KEY CHANGE)
            # ---------------------------
            if vote:
                votes.append(trust)   # weighted contribution
            else:
                votes.append(0)

        # ---------------------------
        # TRUST-WEIGHTED DECISION
        # ---------------------------
        positive_weight = sum(votes)

        total_weight = sum(
            trust_scores.get(v.validator_id, 0.5)
            for v in committee
        )
        
        approved = sum(1 for v in votes if v > 0)
        rejected = len(votes) - approved

        from z_dashboard.state import state
        state["consensus_info"] = {
            "approved": approved,
            "rejected": rejected
        }

        # ---------------------------
        # DYNAMIC THRESHOLD
        # ---------------------------
        threshold = 0.6 * total_weight

        return positive_weight >= threshold
