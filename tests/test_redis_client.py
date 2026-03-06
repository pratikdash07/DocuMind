import unittest
from core.memory.redis_client import MemoryStore

class TestMemoryStore(unittest.TestCase):
    def setUp(self):
        self.memory = MemoryStore()
        self.source_id = "test1"

    def test_log_and_get(self):
        metadata = {
            "source": "email",
            "filename": "test.eml",
            "classification": {"format": "Email", "intent": "Complaint"}
        }
        self.memory.log_metadata(self.source_id, metadata)
        self.memory.log_agent_fields(self.source_id, "email_agent", {"sender": "a@b.com"})
        self.memory.log_action(self.source_id, "escalate")
        self.memory.log_decision_trace(self.source_id, {"step": "done"})

        trace = self.memory.get_full_trace(self.source_id)
        self.assertEqual(trace["metadata"]["source"], "email")
        self.assertEqual(trace["email_agent_fields"]["sender"], "a@b.com")
        self.assertEqual(trace["action"], "escalate")
        self.assertEqual(trace["decision_trace"]["step"], "done")

if __name__ == '__main__':
    unittest.main()
