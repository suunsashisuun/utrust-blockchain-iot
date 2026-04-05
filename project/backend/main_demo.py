from trust_manager import TrustManager
from gwo_validator import gwo_select_validator
from submit_transaction import submit_transaction
from delay_tracker import record_delay, average_delay

trust_manager = TrustManager()

NUM_TRANSACTIONS = 5

for i in range(1, NUM_TRANSACTIONS + 1):
    trust_scores = trust_manager.get_trust_scores()

    selected_validator = gwo_select_validator(trust_scores)

    delay = submit_transaction()

    record_delay(delay)

    trust_manager.update_trust(selected_validator, success=True)

    print(f"Transaction {i}:")
    print(f"  Selected Validator  : {selected_validator}")
    print(f"  Transaction Delay   : {delay:.4f} seconds")
    print(f"  Updated Trust Values: {trust_manager.get_trust_scores()}")
    print()

print(f"Average Transaction Delay: {average_delay():.4f} seconds")