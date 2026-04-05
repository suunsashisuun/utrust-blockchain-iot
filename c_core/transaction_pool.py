class TransactionPool:

    def __init__(self):
        self.queue = []

    def add_transaction(self, tx):
        self.queue.append(tx)

    def get_transaction(self):

        if len(self.queue) == 0:
            return None

        return self.queue.pop(0)

    def size(self):
        return len(self.queue)