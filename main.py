from fastapi import FastAPI, UploadFile, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from agents.classifier_agent.classifier import ClassifierAgent
from agents.email_agent.email_agent import EmailAgent
from agents.json_agent.json_agent import JSONAgent
from agents.pdf_agent.pdf_agent import PDFAgent
from core.routers.action_router import ActionRouter
from core.memory.redis_client import MemoryStore
import os
import logging
from datetime import datetime

# Set up logging
os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    filename="logs/processing.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dummy endpoints unchanged...

# Initialize components
classifier = ClassifierAgent()
email_agent = EmailAgent()
json_agent = JSONAgent()
pdf_agent = PDFAgent()
action_router = ActionRouter()
memory_store = MemoryStore()

@app.post("/process-file")
async def process_file(file: UploadFile):
    try:
        filename = file.filename
        ext = os.path.splitext(filename)[1].lower()
        source_id = os.path.splitext(filename)[0]

        logger.info(f"Started processing: {filename}")

        # Read content
        if ext == ".pdf":
            temp_path = f"temp_{filename}"
            with open(temp_path, "wb") as f_out:
                content_bytes = await file.read()
                f_out.write(content_bytes)
            content = None
        else:
            content_bytes = await file.read()
            content = content_bytes.decode("utf-8")
            temp_path = None

        # Classify
        classification = classifier.classify(filename, content if content else "")
        logger.info(f"Classification result: {classification}")

        # Agent processing
        if classification["format"] == "Email":
            result = email_agent.process(filename, content, classification)
            action = result["action"]
        elif classification["format"] == "JSON":
            result = json_agent.process(filename, content, classification)
            action = "alert" if not result["valid"] else "accept"
        elif classification["format"] == "PDF":
            result = pdf_agent.process(temp_path, classification)
            action = result.get("flag", "accepted")
        else:
            raise HTTPException(status_code=400, detail="Unsupported format")

        logger.info(f"Processing result: {result}")

        # Action routing
        payload = {"source_id": source_id, "result": result}
        action_result = action_router.route_action(
            action if action in action_router.endpoints else "routine", 
            payload
        )
        logger.info(f"Action result: {action_result}")

        # Get and log full trace
        trace = memory_store.get_full_trace(source_id)
        logger.info(f"Redis trace data: {trace}")

        # Cleanup
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)

        return {
            "classification": classification,
            "processing_result": result,
            "action_router_result": action_result,
            "full_trace": trace
        }

    except Exception as e:
        logger.error(f"Error processing {filename}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
