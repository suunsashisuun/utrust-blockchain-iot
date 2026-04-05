import simpy
from g_simulation.simpy_engine import run_simulation
from e_consensus.scheduler import scheduler_with_selector
from e_consensus.gwo_selector import GWOSelector

env = simpy.Environment()

blockchain, network = run_simulation(
    env,
    scheduler_with_selector,
    GWOSelector,
    num_validators=10
)

env.run(until=10)

print("Blocks created:", len(blockchain.chain))
print("Validators:", len(network.get_validators()))

