import hashlib
import time


class Block:

    def __init__(
        self,
        index,
        validator_id,
        transactions,
        previous_hash,
        consensus_status
    ):
        self.index = index
        self.validator_id = validator_id
        self.transactions = transactions
        self.timestamp = time.time()
        self.previous_hash = previous_hash
        self.consensus_status = consensus_status  # 🔥 NEW
        self.transaction_count = len(transactions)  # 🔥 NEW

        self.hash = self.compute_hash()

    def compute_hash(self):

        block_string = (
            str(self.index)
            + str(self.validator_id)
            + str(self.transactions)
            + str(self.timestamp)
            + str(self.previous_hash)
            + str(self.consensus_status)
        )

        return hashlib.sha256(block_string.encode()).hexdigest()
