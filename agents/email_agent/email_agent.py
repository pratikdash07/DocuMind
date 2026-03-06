import re
import os
from core.memory.redis_client import MemoryStore

class EmailAgent:
    def __init__(self):
        self.urgent_keywords = ["urgent", "immediately", "asap", "important", "high priority"]
        self.tone_keywords = {
            "escalation": ["not acceptable", "unhappy", "angry", "frustrated", "escalate"],
            "polite": ["please", "kindly", "would you", "thank you"],
            "threatening": ["legal action", "lawsuit", "report", "compensation"],
        }
        self.memory_store = MemoryStore()

    def extract_fields(self, content):
        sender = re.search(r"From:\s*(.*)", content)
        subject = re.search(r"Subject:\s*(.*)", content)
        body = content.split("\n\n", 1)[-1] if "\n\n" in content else content

        sender = sender.group(1).strip() if sender else "Unknown"
        subject = subject.group(1).strip() if subject else "No Subject"

        urgency = any(word in content.lower() for word in self.urgent_keywords)
        issue = subject if subject != "No Subject" else body[:50]

        return {
            "sender": sender,
            "subject": subject,
            "urgency": "high" if urgency else "normal",
            "issue": issue,
            "body": body
        }

    def detect_tone(self, content):
        content_lower = content.lower()
        for tone, keywords in self.tone_keywords.items():
            for kw in keywords:
                if kw in content_lower:
                    return tone
        return "neutral"

    def process(self, file_path, content, classification):
        # Generate source_id from file name
        source_id = os.path.splitext(os.path.basename(file_path))[0]

        # Log metadata
        self.memory_store.log_metadata(
            source_id,
            {
                "source": "email",
                "filename": file_path,
                "classification": classification
            }
        )

        # Extract fields and log
        fields = self.extract_fields(content)
        self.memory_store.log_agent_fields(source_id, "email_agent", fields)

        # Detect tone and determine action
        tone = self.detect_tone(content)
        fields["tone"] = tone
        if tone in ["escalation", "threatening"] or fields["urgency"] == "high":
            action = "escalate"
        else:
            action = "routine"

        # Log action
        self.memory_store.log_action(source_id, action)
        fields["action"] = action

        # Log decision trace (for demonstration, a simple dict)
        trace = {
            "step": "email_processed",
            "fields": fields,
            "action": action
        }
        self.memory_store.log_decision_trace(source_id, trace)

        return fields
