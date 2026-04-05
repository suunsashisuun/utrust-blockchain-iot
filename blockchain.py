from block import Block


class Blockchain:

    def __init__(self, block_size=5):

        self.chain = []
        self.block_size = block_size
        self.transaction_pool = []

        self.create_genesis_block()


    def create_genesis_block(self):

        genesis_block = Block(
            index=0,
            validator_id="genesis",
            transactions=[],
            previous_hash="0"
        )

        self.chain.append(genesis_block)


    def get_last_block(self):

        return self.chain[-1]


    def add_transaction(self, validator_id, transaction):

        self.transaction_pool.append(transaction)

        # if pool reaches block size → create block
        if len(self.transaction_pool) >= self.block_size:

            previous_block = self.get_last_block()

            new_block = Block(
                index=len(self.chain),
                validator_id=validator_id,
                transactions=self.transaction_pool.copy(),
                previous_hash=previous_block.hash
            )

            self.chain.append(new_block)

            # reset pool
            self.transaction_pool = []

            return new_block

        return None