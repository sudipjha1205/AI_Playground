"""
Base tool definitions following MCP-style structured tool pattern.
All tools return validated JSON responses.
"""
import json
import logging
from typing import Any, Dict
from pydantic import BaseModel, ValidationError

logger = logging.getLogger(__name__)


class ToolResult(BaseModel):
    success: bool
    data: Dict[str, Any]
    error: str = ""
    tool_name: str


def safe_json_parse(text: str, fallback: Dict = None) -> Dict:
    """Safely parse JSON from text, with fallback."""
    if fallback is None:
        fallback = {}
    try:
        # Try direct parse
        return json.loads(text)
    except json.JSONDecodeError:
        # Try to extract JSON from text
        import re
        patterns = [
            r'\{[^{}]*\}',  # Simple object
            r'\{.*?\}',     # Any object (non-greedy)
        ]
        for pattern in patterns:
            matches = re.findall(pattern, text, re.DOTALL)
            for match in matches:
                try:
                    return json.loads(match)
                except json.JSONDecodeError:
                    continue
        logger.warning(f"Could not parse JSON from: {text[:100]}...")
        return fallback


def extract_code_block(text: str, label: str) -> str:
    """Extract content from a labeled code block."""
    import re
    pattern = rf'```{label}\s*(.*?)\s*```'
    match = re.search(pattern, text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return ""


def strip_code_blocks(text: str) -> str:
    """Remove all code blocks from text for display."""
    import re
    # Remove labeled code blocks
    text = re.sub(r'```\w+\s*\{.*?\}\s*```', '', text, flags=re.DOTALL)
    # Remove any remaining code fences with game_state/mind_state/analysis_state
    text = re.sub(r'```(?:game_state|mind_state|analysis_state).*?```', '', text, flags=re.DOTALL)
    return text.strip()
