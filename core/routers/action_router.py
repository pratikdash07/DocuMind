import requests
import time

class ActionRouter:
    def __init__(self):
        self.endpoints = {
            "escalate": "http://localhost:8001/crm/escalate",
            "routine": "http://localhost:8001/crm/log",
            "alert": "http://localhost:8001/risk_alert",
            "flagged": "http://localhost:8001/compliance/flag",
            "accepted": "http://localhost:8001/compliance/accept"
        }
        self.max_retries = 3
        self.base_delay = 1  # seconds

    def route_action(self, action: str, payload: dict) -> dict:
        url = self.endpoints.get(action)
        if not url:
            return {"status": "error", "message": f"No endpoint for action: {action}"}
        last_exception = None
        for attempt in range(1, self.max_retries + 1):
            try:
                response = requests.post(url, json=payload, timeout=5)
                return {
                    "status": "success",
                    "endpoint": url,
                    "response": response.json() if response.content else {}
                }
            except Exception as e:
                last_exception = e
                time.sleep(self.base_delay * (2 ** (attempt - 1)))  # exponential backoff
        # If all retries failed
        return {
            "status": "failed",
            "endpoint": url,
            "error": str(last_exception),
            "retries": self.max_retries
        }
