import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))



from g_simulation.simpy_engine import run_simulation
import simpy


def test_simulation_runs():
    env = simpy.Environment()


    blockchain, network = run_simulation(
        env,
        scheduler_func=None,  # or dummy
        selector_class=None
    )


    env.run(until=10)


    assert blockchain is not None
    assert len(network.get_validators()) > 0


print("Basic test passed")
