import unittest
import os
from agents.pdf_agent.pdf_agent import PDFAgent

class TestPDFAgent(unittest.TestCase):
    def setUp(self):
        self.agent = PDFAgent()
        # Create a sample PDF for testing
        from PyPDF2 import PdfWriter
        self.test_pdf_path = "test_invoice.pdf"
        writer = PdfWriter()
        writer.add_blank_page(width=72, height=72)
        with open(self.test_pdf_path, "wb") as f:
            writer.write(f)
        # Overwrite with text (PyPDF2 can't write text, so we will mock extract_text)
        self.sample_invoice_text = "Invoice\nTotal: 12050\nThank you."
        self.sample_policy_text = "This policy is compliant with GDPR and FDA regulations."

    def tearDown(self):
        if os.path.exists(self.test_pdf_path):
            os.remove(self.test_pdf_path)

    def test_extract_invoice_total(self):
        total = self.agent.extract_invoice_total(self.sample_invoice_text)
        self.assertEqual(total, 12050)

    def test_invoice_flag(self):
        # Mock extract_text to return sample_invoice_text
        self.agent.extract_text = lambda path: self.sample_invoice_text
        result = self.agent.process(self.test_pdf_path)
        self.assertEqual(result["invoice_total"], 12050)
        self.assertEqual(result["flag"], "Invoice total exceeds 10,000")

    def test_policy_mentions(self):
        self.agent.extract_text = lambda path: self.sample_policy_text
        result = self.agent.process(self.test_pdf_path)
        self.assertIn("GDPR", result["policy_mentions"])
        self.assertIn("FDA", result["policy_mentions"])
        self.assertTrue(result["flag"].startswith("Policy mentions"))

if __name__ == '__main__':
    unittest.main()
