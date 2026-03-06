import json
import os
import dotenv

# LLM imports
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI

dotenv.load_dotenv()

class ClassifierAgent:
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash")
        self.intent_labels = ["RFQ", "Complaint", "Invoice", "Regulation", "Fraud Risk"]
        # For fallback rule-based detection
        self.intent_examples = {
            "RFQ": ["request for quote", "quotation", "quote needed", "rfq"],
            "Complaint": ["not satisfied", "complaint", "issue", "problem", "bad experience", "unsatisfied"],
            "Invoice": ["invoice", "bill", "amount due", "payment due", "billed"],
            "Regulation": ["regulation", "compliance", "policy", "gdpr", "fda"],
            "Fraud Risk": ["fraud", "suspicious", "unauthorized", "risk", "scam"]
        }

    def generate_few_shot_prompt(self, content: str) -> str:
        return f"""
You are a business document classifier. Classify this document into one of:
[RFQ, Complaint, Invoice, Regulation, Fraud Risk]

Here are some examples:

Example 1:
Content: "Please send me a quote for 100 units of product X."
Label: RFQ

Example 2:
Content: "I am unhappy with the service and want to file a complaint."
Label: Complaint

Example 3:
Content: "This invoice shows a total amount due of $12,000."
Label: Invoice

Example 4:
Content: "Our policy is compliant with GDPR and FDA."
Label: Regulation

Example 5:
Content: "We have detected unauthorized activity. This may be fraud."
Label: Fraud Risk

Now classify the following document. Respond with only the label.
Content:
{content}
"""

    def detect_format(self, file_path, content):
        ext = os.path.splitext(file_path)[1].lower()
        if ext == ".json":
            return "JSON"
        elif ext in [".eml", ".msg", ".txt"]:
            return "Email"
        elif ext == ".pdf":
            return "PDF"
        try:
            json.loads(content)
            return "JSON"
        except Exception:
            pass
        if "From:" in content and "Subject:" in content:
            return "Email"
        return "Unknown"

    def detect_intent(self, content):
        # --- 1. Schema Matching for JSON ---
        try:
            data = json.loads(content)
            # Invoice schema
            if all(key in data for key in ["order_id", "customer", "amount"]):
                return "Invoice"
            # RFQ schema
            if all(key in data for key in ["rfq_id", "customer", "items"]):
                return "RFQ"
            # Add more schemas as needed
        except Exception:
            pass

        # --- 2. LLM with Few-Shot Prompt ---
        prompt_str = self.generate_few_shot_prompt(content)
        prompt = ChatPromptTemplate.from_template(prompt_str)
        chain = prompt | self.llm
        try:
            result = chain.invoke({"content": content}).content.strip()
            for label in self.intent_labels:
                if label.lower() in result.lower():
                    return label
        except Exception:
            pass

        # --- 3. Fallback: Rule-based intent detection ---
        content_lower = content.lower()
        for intent, keywords in self.intent_examples.items():
            for kw in keywords:
                if kw in content_lower:
                    return intent
        return "Unknown"

    def classify(self, file_path, content):
        fmt = self.detect_format(file_path, content)
        intent = self.detect_intent(content)
        return {"format": fmt, "intent": intent}
