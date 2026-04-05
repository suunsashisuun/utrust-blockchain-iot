from trust_manager import TrustManager
from gwo_selector import GWOSelector
from blockchain import Blockchain
from urgency_classifier import UrgencyClassifier
from validator_network import ValidatorNetwork
import time

class UTrustConsensus:

    def __init__(self):

        network = ValidatorNetwork(50)
        self.validators = network.get_validators()
        #validator_objects = network.get_validators()
        #self.validators = [v.validator_id for v in validator_objects]
        #self.trust_manager = TrustManager(self.validators)
        self.trust_manager = TrustManager([v.validator_id for v in self.validators])
        self.gwo = GWOSelector()
        self.blockchain = Blockchain()
        self.urgency_classifier = UrgencyClassifier()
       


    def process_transaction(self, device_id, gas_value):
        start_time = time.time()
        # 1️⃣ classify urgency
        urgency_level = self.urgency_classifier.classify(device_id, gas_value)

        # convert urgency to weight
        if urgency_level == "CRITICAL":
            urgency_weight = 0.8
        elif urgency_level == "WARNING":
            urgency_weight = 0.4
        else:
            urgency_weight = 0.1


        # 2️⃣ get trust scores
        trust_scores = self.trust_manager.get_trust_scores()


        # 3️⃣ select validator using GWO
       
        selected_validator = self.gwo.select_validator(
            self.validators,
            self.trust_manager.get_trust_scores(),
            urgency_weight
        )
        validator_id = selected_validator
        
        # 4️⃣ create transaction
        transaction = {
            "device": device_id,
            "gas": gas_value,
            "urgency": urgency_level
        }


        # 5️⃣ add block
        block = self.blockchain.add_transaction(
            validator_id,
            [transaction]
        )

        block_index = None
        if block is not None:
            block_index = block.index


        # 6️⃣ assume success (simulation)
        success = True


        # 7️⃣ update trust
        self.trust_manager.update_trust(
            selected_validator,
            success
        )

        latency = time.time() - start_time

        return {
            "validator": selected_validator,
            "urgency": urgency_level,
            "block_index": block_index,
            "trust_scores": self.trust_manager.get_trust_scores(),
            "latency": latency

        }
   