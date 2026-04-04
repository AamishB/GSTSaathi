"""
Utilities for structured agent execution logging.
"""
import json
import logging
from typing import Any, Dict, Optional


def log_agent_event(
    logger: logging.Logger,
    *,
    agent: str,
    task: str,
    status: str,
    user_id: Optional[int] = None,
    details: Optional[Dict[str, Any]] = None,
) -> None:
    """Emit structured JSON log lines for agent execution visibility."""
    payload: Dict[str, Any] = {
        "event": "agent_execution",
        "agent": agent,
        "task": task,
        "status": status,
    }
    if user_id is not None:
        payload["user_id"] = user_id
    if details:
        payload["details"] = details

    logger.info(json.dumps(payload, ensure_ascii=False, default=str))
