import random


class PBFTConsensus:

    def __init__(self, committee_size=5):
        self.committee_size = committee_size

    def run_consensus(self, proposer_id, consensus_group, trust_scores):

        if len(consensus_group) <= 1:
            return False

        # remove proposer from voting
        committee_pool = [
            v for v in consensus_group
            if v.validator_id != proposer_id
        ]

        committee = random.sample(
            committee_pool,
            min(self.committee_size, len(committee_pool))
        )

        votes = []

        for validator in committee:

            vid = validator.validator_id
            trust = trust_scores.get(vid, 0.5)
            proposer_trust = trust_scores.get(proposer_id, 0.5)

            # 🔥 balanced probability
            vote_probability = (
                0.7 * trust +
                0.3 * proposer_trust
            )

            vote_probability = min(1.0, vote_probability + 0.1)

            # 🔥 soft filter (not harsh)
            if trust < 0.2:
                vote = False
            else:
                vote = random.random() < vote_probability

            votes.append(vote)

        positive_votes = sum(votes)

        return positive_votes >= (len(votes) // 2 + 1)
