import unittest
from agents.email_agent.email_agent import EmailAgent

class TestEmailAgent(unittest.TestCase):
    def setUp(self):
        self.agent = EmailAgent()

    def test_extract_fields(self):
        content = "From: user@example.com\nSubject: Urgent Issue\n\nThis needs to be fixed ASAP."
        fields = self.agent.extract_fields(content)
        self.assertEqual(fields["sender"], "user@example.com")
        self.assertEqual(fields["urgency"], "high")

    def test_detect_tone(self):
        content = "I am very unhappy with your service. Please escalate."
        tone = self.agent.detect_tone(content)
        self.assertEqual(tone, "escalation")

    def test_process(self):
        content = "From: boss@company.com\nSubject: Complaint\n\nThis is not acceptable. Fix immediately."
        result = self.agent.process(content)
        self.assertEqual(result["action"], "escalate")

if __name__ == '__main__':
    unittest.main()
