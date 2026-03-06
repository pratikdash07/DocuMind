import unittest
from agents.classifier_agent.classifier import ClassifierAgent

class TestClassifierAgent(unittest.TestCase):
    def setUp(self):
        self.agent = ClassifierAgent()

    def test_detect_format_json(self):
        content = '{"key": "value"}'
        fmt = self.agent.detect_format("sample.json", content)
        self.assertEqual(fmt, "JSON")

    def test_detect_format_email(self):
        content = "From: test@example.com\nSubject: Test Email\nBody: Hello"
        fmt = self.agent.detect_format("sample.eml", content)
        self.assertEqual(fmt, "Email")

    def test_detect_format_pdf(self):
        content = "%PDF-1.4"
        fmt = self.agent.detect_format("sample.pdf", content)
        self.assertEqual(fmt, "PDF")

    def test_detect_intent_rfq(self):
        content = "We need a quotation for your services."
        intent = self.agent.detect_intent(content)
        self.assertEqual(intent, "RFQ")

    def test_detect_intent_complaint(self):
        content = "I have a complaint about your product."
        intent = self.agent.detect_intent(content)
        self.assertEqual(intent, "Complaint")

    def test_classify_email_invoice(self):
        content = "From: billing@company.com\nSubject: Invoice\nPlease find attached invoice."
        result = self.agent.classify("invoice.eml", content)
        self.assertEqual(result["format"], "Email")
        self.assertEqual(result["intent"], "Invoice")

if __name__ == '__main__':
    unittest.main()

