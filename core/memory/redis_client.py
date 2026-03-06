import redis
import json
from datetime import datetime
from typing import Dict, Any, Optional

class MemoryStore:
    def __init__(self, host="localhost", port=6379, db=0):
        self.conn = redis.Redis(host=host, port=port, db=db, decode_responses=True)

    def _make_key(self, source_id: str) -> str:
        return f"trace:{source_id}"

    def log_metadata(self, source_id: str, metadata: Dict[str, Any]):
        key = self._make_key(source_id)
        metadata["timestamp"] = metadata.get("timestamp") or datetime.utcnow().isoformat()
        self.conn.hset(key, mapping={"metadata": json.dumps(metadata)})

    def log_agent_fields(self, source_id: str, agent_name: str, fields: Dict[str, Any]):
        key = self._make_key(source_id)
        self.conn.hset(key, mapping={f"{agent_name}_fields": json.dumps(fields)})

    def log_action(self, source_id: str, action: str):
        key = self._make_key(source_id)
        self.conn.hset(key, mapping={"action": action})

    def log_decision_trace(self, source_id: str, trace: Any):
        key = self._make_key(source_id)
        self.conn.hset(key, mapping={"decision_trace": json.dumps(trace)})

    def get_full_trace(self, source_id: str) -> Optional[Dict[str, Any]]:
        key = self._make_key(source_id)
        data = self.conn.hgetall(key)
        # Parse JSON fields if present
        for k in data:
            try:
                data[k] = json.loads(data[k])
            except Exception:
                pass
        return data if data else None
