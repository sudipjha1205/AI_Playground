"""
Mind Reader Tools - MCP-style structured tools for psychic game state.
"""
import logging
from tools.base_tool import ToolResult, extract_code_block, safe_json_parse, strip_code_blocks

logger = logging.getLogger(__name__)

DEFAULT_MIND_STATE = {
    "phase": "thinking",
    "questions_asked": 0,
    "category": "unknown",
    "known_facts": [],
    "confidence": 0,
    "final_guess": None
}


def parse_mind_reader_response(raw_response: str) -> ToolResult:
    """
    Tool: Parse and validate mind reader agent response.
    Extracts mind_state JSON and oracle narrative.
    """
    tool_name = "parse_mind_reader_response"
    
    try:
        mind_state_raw = extract_code_block(raw_response, "mind_state")
        
        if mind_state_raw:
            mind_state = safe_json_parse(mind_state_raw, DEFAULT_MIND_STATE.copy())
        else:
            mind_state = DEFAULT_MIND_STATE.copy()
            logger.warning("No mind_state block found, using defaults")
        
        # Validate fields
        mind_state.setdefault("phase", "questioning")
        mind_state.setdefault("questions_asked", 0)
        mind_state.setdefault("category", "unknown")
        mind_state.setdefault("known_facts", [])
        mind_state.setdefault("confidence", 0)
        mind_state.setdefault("final_guess", None)
        
        # Clamp values
        mind_state["questions_asked"] = max(0, min(10, int(mind_state["questions_asked"])))
        mind_state["confidence"] = max(0, min(100, int(mind_state["confidence"])))
        
        narrative = strip_code_blocks(raw_response)
        questions_left = max(0, 10 - mind_state["questions_asked"])
        
        return ToolResult(
            success=True,
            data={
                "narrative": narrative,
                "mind_state": mind_state,
                "phase": mind_state["phase"],
                "questions_asked": mind_state["questions_asked"],
                "questions_left": questions_left,
                "confidence": mind_state["confidence"],
                "final_guess": mind_state["final_guess"],
                "known_facts": mind_state["known_facts"],
                "category": mind_state["category"],
                "is_guessing": mind_state["phase"] == "guessing",
                "is_revealed": mind_state["phase"] == "revealed"
            },
            tool_name=tool_name
        )
    except Exception as e:
        logger.error(f"Error in {tool_name}: {e}")
        return ToolResult(
            success=False,
            data={"narrative": raw_response, "mind_state": DEFAULT_MIND_STATE.copy()},
            error=str(e),
            tool_name=tool_name
        )


def validate_yes_no_response(user_input: str) -> ToolResult:
    """Tool: Validate if a response is yes/no type."""
    normalized = user_input.lower().strip()
    yes_variants = ["yes", "yeah", "yep", "yup", "correct", "right", "true", "affirmative", "y"]
    no_variants = ["no", "nope", "nah", "wrong", "incorrect", "false", "negative", "n"]
    
    is_yes = any(v in normalized for v in yes_variants)
    is_no = any(v in normalized for v in no_variants)
    
    return ToolResult(
        success=True,
        data={
            "is_yes_no": is_yes or is_no,
            "is_yes": is_yes,
            "is_no": is_no,
            "original": user_input
        },
        tool_name="validate_yes_no_response"
    )
