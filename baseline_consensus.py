class BaselineConsensus:

    def __init__(self, validators, leader_interval=10):

        self.validators = validators
        self.leader_interval = leader_interval

        self.current_leader_index = 0
        self.block_counter = 0


    def select_validator(self):

        leader = self.validators[self.current_leader_index]

        self.block_counter += 1

        if self.block_counter % self.leader_interval == 0:

            self.current_leader_index = (
                self.current_leader_index + 1
            ) % len(self.validators)

        return leader