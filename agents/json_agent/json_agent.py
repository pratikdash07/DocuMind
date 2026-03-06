import json
from core.memory.redis_client import MemoryStore

class JSONAgent:
    def __init__(self):
        self.memory_store = MemoryStore()

    def process(self, file_path, content, classification):
        source_id = file_path.split('.')[0]
        try:
            data = json.loads(content)
        except Exception:
            self.memory_store.log_metadata(
                source_id,
                {
                    "error": "Invalid JSON",
                    "classification": classification
                }
            )
            return {
                "valid": False,
                "type": None,
                "data": None,
                "anomalies": ["Invalid JSON"]
            }

        anomalies = []
        detected_type = None

        # --- Invoice Schema ---
        invoice_required = {"order_id", "customer", "amount"}
        if invoice_required.issubset(data.keys()):
            detected_type = "Invoice"
            if not isinstance(data.get("order_id"), int):
                anomalies.append("order_id should be int")
            if not isinstance(data.get("amount"), (int, float)):
                anomalies.append("amount should be a number")

        # --- RFQ Schema ---
        rfq_required = {"rfq_id", "customer", "items"}
        if rfq_required.issubset(data.keys()):
            detected_type = "RFQ"
            if not isinstance(data.get("rfq_id"), int):
                anomalies.append("rfq_id should be int")
            if not isinstance(data.get("items"), list):
                anomalies.append("items should be a list")

        # If no schema matched
        if not detected_type:
            anomalies.append("Unknown JSON schema")
            # Log alert in Redis
            self.memory_store.log_metadata(
                source_id,
                {
                    "alert": "Unknown JSON schema",
                    "classification": classification,
                    "data": data
                }
            )

        # Log extracted fields and anomalies
        self.memory_store.log_metadata(
            source_id,
            {
                "json_agent_fields": {
                    "type": detected_type,
                    "data": data,
                    "anomalies": anomalies
                }
            }
        )

        return {
            "valid": len(anomalies) == 0,
            "type": detected_type,
            "data": data,
            "anomalies": anomalies
        }
