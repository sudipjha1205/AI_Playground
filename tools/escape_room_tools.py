"""
Escape Room Tools - MCP-style structured tools for game state management.
"""
import logging
from typing import Dict, Any
from tools.base_tool import ToolResult, extract_code_block, safe_json_parse, strip_code_blocks

logger = logging.getLogger(__name__)

DEFAULT_GAME_STATE = {
    "oxygen_level": 23,
    "puzzles_solved": 0,
    "current_puzzle": "POWER_GRID",
    "game_status": "active",
    "solved_list": []
}

PUZZLE_ORDER = ["POWER_GRID", "AIRLOCK_CODE", "NAVIGATION", "REACTOR", "ESCAPE_POD"]


def parse_escape_room_response(raw_response: str) -> ToolResult:
    """
    Tool: Parse and validate escape room agent response.
    Extracts game_state JSON and narrative text.
    """
    tool_name = "parse_escape_room_response"
    
    try:
        # Extract game state JSON
        game_state_raw = extract_code_block(raw_response, "game_state")
        
        if game_state_raw:
            game_state = safe_json_parse(game_state_raw, DEFAULT_GAME_STATE.copy())
        else:
            game_state = DEFAULT_GAME_STATE.copy()
            logger.warning("No game_state block found, using defaults")
        
        # Validate required fields
        game_state.setdefault("oxygen_level", 23)
        game_state.setdefault("puzzles_solved", 0)
        game_state.setdefault("current_puzzle", "POWER_GRID")
        game_state.setdefault("game_status", "active")
        game_state.setdefault("solved_list", [])
        
        # Clamp oxygen
        game_state["oxygen_level"] = max(0, min(100, int(game_state["oxygen_level"])))
        
        # Clean narrative (remove code blocks)
        narrative = strip_code_blocks(raw_response)
        
        return ToolResult(
            success=True,
            data={
                "narrative": narrative,
                "game_state": game_state,
                "oxygen_level": game_state["oxygen_level"],
                "puzzles_solved": game_state["puzzles_solved"],
                "game_status": game_state["game_status"],
                "current_puzzle": game_state["current_puzzle"],
                "solved_list": game_state.get("solved_list", []),
                "progress_pct": (game_state["puzzles_solved"] / 5) * 100
            },
            tool_name=tool_name
        )
    except Exception as e:
        logger.error(f"Error in {tool_name}: {e}")
        return ToolResult(
            success=False,
            data={"narrative": raw_response, "game_state": DEFAULT_GAME_STATE.copy()},
            error=str(e),
            tool_name=tool_name
        )


def get_puzzle_hint(puzzle_name: str) -> ToolResult:
    """Tool: Return a cryptic hint for a given puzzle."""
    hints = {
        "POWER_GRID": "Think of something that represents the world, but isn't the world itself...",
        "AIRLOCK_CODE": "Consider what you leave behind when you walk...",
        "NAVIGATION": "What travels without a body, speaks without a mouth?",
        "REACTOR": "Think of water in motion — it has features but no face...",
        "ESCAPE_POD": "Time is of the essence. What tells time but has no voice?"
    }
    
    return ToolResult(
        success=True,
        data={"hint": hints.get(puzzle_name, "The answer lies within the question itself..."), "puzzle": puzzle_name},
        tool_name="get_puzzle_hint"
    )
