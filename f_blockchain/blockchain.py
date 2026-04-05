from .block import Block


class Blockchain:

    def __init__(self, block_size=5):

        self.chain = []
        self.block_size = block_size
        self.transaction_pool = []

        self.total_transactions = 0  # 🔥 NEW

        self.create_genesis_block()

    def create_genesis_block(self):

        genesis_block = Block(
            index=0,
            validator_id="genesis",
            transactions=[],
            previous_hash="0",
            consensus_status=True
        )

        self.chain.append(genesis_block)

    def get_last_block(self):
        return self.chain[-1]

    def add_transaction(self, validator_id, transaction, consensus_status=True):

        # 🔥 track total transactions
        self.total_transactions += 1

        self.transaction_pool.append(transaction)

        # create block when pool full
        if len(self.transaction_pool) >= self.block_size:

            previous_block = self.get_last_block()

            new_block = Block(
                index=len(self.chain),
                validator_id=validator_id,
                transactions=self.transaction_pool.copy(),
                previous_hash=previous_block.hash,
                consensus_status=consensus_status  # 🔥 NEW
            )

            #DELETE
           # print(f"\nBLOCK CREATED by {validator_id}")
            #print(f"Block Index: {new_block.index}")
            #print(f"Transactions in Block: {len(new_block.transactions)}")
            #print(f"Chain Length: {len(self.chain)}\n")

            self.chain.append(new_block)

            # reset pool
            self.transaction_pool = []

            return new_block

        return None

    # 🔥 OPTIONAL (but useful for metrics)
    def get_chain_length(self):
        return len(self.chain)

    def get_total_transactions(self):
        return self.total_transactions
