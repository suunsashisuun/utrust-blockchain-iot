import random


class PBFTConsensus:
    """
    Practical Byzantine Fault Tolerance (PBFT) inspired consensus.

    Features:
    - Trust-weighted voting
    - Dynamic committee selection
    - Soft Byzantine filtering
    """

    def __init__(self, committee_size=7):
        self.committee_size = committee_size

    def run_consensus(self, proposer_id, consensus_group, trust_scores):

        # ---------------------------
        # BASIC VALIDATION
        # ---------------------------
        if len(consensus_group) <= 1:
            return False

        # ---------------------------
        # FORM COMMITTEE (exclude proposer)
        # ---------------------------
        committee_pool = [
            validator for validator in consensus_group
            if validator.validator_id != proposer_id
        ]

        if len(committee_pool) == 0:
            return False

        committee = random.sample(
            committee_pool,
            min(self.committee_size, len(committee_pool))
        )

        # ---------------------------
        # PHASE 1: PRE-PREPARE
        # ---------------------------
        proposer_trust = trust_scores.get(proposer_id, 0.5)

        # Reject weak proposer early
        if proposer_trust < 0.2:
            return False

        # ---------------------------
        # PHASE 2: PREPARE (VOTING)
        # ---------------------------
        votes = []

        for validator in committee:

            validator_id = validator.validator_id
            trust = trust_scores.get(validator_id, 0.5)

            # ---------------------------
            # VOTE PROBABILITY
            # ---------------------------
            vote_probability = (
                0.7 * trust +
                0.3 * proposer_trust
            )

            vote_probability = min(1.0, vote_probability + 0.05)

            # ---------------------------
            # BYZANTINE BEHAVIOR & FILTER
            # ---------------------------
            if validator.is_malicious:
                vote = random.random() < 0.3   # unreliable voting
            elif trust < 0.2:
                vote = False
            else:
                vote = random.random() < vote_probability

            # ---------------------------
            # WEIGHTED VOTING
            # ---------------------------
            if vote:
                votes.append(trust)
            else:
                votes.append(0)

        # ---------------------------
        # PHASE 3: COMMIT
        # ---------------------------
        positive_weight = sum(votes)

        total_weight = sum(
            trust_scores.get(validator.validator_id, 0.5)
            for validator in committee
        )

        if total_weight == 0:
            return False

        approved = sum(1 for vote in votes if vote > 0)
        rejected = len(votes) - approved

        # ---------------------------
        # UPDATE DASHBOARD STATE
        # ---------------------------
        from z_dashboard.state import state
        state["consensus_info"] = {
            "approved": approved,
            "rejected": rejected
        }

        # ---------------------------
        # COMMIT DECISION
        # ---------------------------
        commit_threshold = 0.6 * total_weight

        return positive_weight >= commit_threshold
