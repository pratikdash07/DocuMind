import re
import os
from PyPDF2 import PdfReader
from core.memory.redis_client import MemoryStore
from io import BytesIO

class PDFAgent:
    def __init__(self):
        self.compliance_keywords = ["GDPR", "FDA", "HIPAA", "PCI"]
        self.memory_store = MemoryStore()

    def extract_text(self, file_path):
        """
        Extracts text from a PDF file robustly, handling missing EOF markers and corrupted files.
        Returns an empty string if extraction fails.
        """
        try:
            # Read PDF as binary
            with open(file_path, "rb") as f:
                pdf_data = f.read()

            # Check for PDF header
            if not pdf_data.startswith(b'%PDF-'):
                return ""

            # Fix missing EOF marker
            eof_pos = pdf_data.rfind(b'%%EOF')
            if eof_pos == -1:
                # Try to fix by appending EOF
                pdf_data += b'\n%%EOF\n'

            # Use BytesIO for PyPDF2
            reader = PdfReader(BytesIO(pdf_data), strict=False)
            text = ""
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text
            return text

        except Exception as e:
            # Extraction failed, return empty string
            return ""

    def extract_invoice_total(self, text):
        match = re.search(r"total(?: amount)?[:\s]*([\d,\.]+)", text, re.IGNORECASE)
        if match:
            try:
                total = float(match.group(1).replace(",", ""))
                return total
            except ValueError:
                return None
        return None

    def extract_policy_mentions(self, text):
        mentions = []
        for keyword in self.compliance_keywords:
            if keyword.lower() in text.lower():
                mentions.append(keyword)
        return mentions

    def process(self, file_path, classification):
        source_id = os.path.splitext(os.path.basename(file_path))[0]

        # Log metadata
        self.memory_store.log_metadata(
            source_id,
            {
                "source": "pdf",
                "filename": file_path,
                "classification": classification
            }
        )

        text = self.extract_text(file_path)
        result = {"text": text}

        # Check for invoice total
        total = self.extract_invoice_total(text)
        if total is not None:
            result["invoice_total"] = total
            if total > 10000:
                result["flag"] = "Invoice total exceeds 10,000"

        # Check for compliance keywords
        mentions = self.extract_policy_mentions(text)
        if mentions:
            result["policy_mentions"] = mentions
            result["flag"] = f"Policy mentions: {', '.join(mentions)}"

        # Log fields and action
        self.memory_store.log_agent_fields(source_id, "pdf_agent", result)
        action = "flagged" if "flag" in result else "accepted"
        self.memory_store.log_action(source_id, action)

        # Log decision trace
        trace = {
            "step": "pdf_processed",
            "result": result,
            "action": action
        }
        self.memory_store.log_decision_trace(source_id, trace)

        return result
