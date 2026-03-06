import unittest
from agents.json_agent.json_agent import JSONAgent

class TestJSONAgent(unittest.TestCase):
    def setUp(self):
        self.agent = JSONAgent()

    def test_valid_json(self):
        content = '{"order_id": 123, "customer": "Alice", "amount": 99.99, "items": ["item1", "item2"]}'
        result = self.agent.process(content)
        self.assertTrue(result["valid"])
        self.assertIsNone(result.get("alert", None))

    def test_missing_field(self):
        content = '{"order_id": 123, "customer": "Alice", "items": ["item1", "item2"]}'
        result = self.agent.process(content)
        self.assertFalse(result["valid"])
        self.assertIn("Missing field: amount", result["anomalies"])
        self.assertEqual(result["alert"], "Anomaly detected and logged")

    def test_type_error(self):
        content = '{"order_id": "not-an-int", "customer": "Alice", "amount": 99.99, "items": ["item1"]}'
        result = self.agent.process(content)
        self.assertFalse(result["valid"])
        self.assertIn("Type error: order_id should be int", result["anomalies"])
        self.assertEqual(result["alert"], "Anomaly detected and logged")

    def test_invalid_json(self):
        content = '{order_id: 123, customer: Alice, amount: 99.99, items: [item1]}'
        result = self.agent.process(content)
        self.assertFalse(result["valid"])
        self.assertIn("Invalid JSON", result["anomalies"])
        self.assertEqual(result["alert"], "Anomaly detected and logged")

if __name__ == '__main__':
    unittest.main()
