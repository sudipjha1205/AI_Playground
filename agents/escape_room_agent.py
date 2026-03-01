"""
Escape Room Agent — Manages the EREBUS-7 space station escape room experience.
Full game logic, state tracking, and atmospheric narrative generation.
"""
from typing import Dict, Any

from agents.base_agent import BaseAgent
from prompts.escape_room_prompts import ESCAPE_ROOM_SYSTEM_PROMPT, ESCAPE_ROOM_INTRO
from tools.escape_room_tools import parse_escape_room_response, DEFAULT_GAME_STATE


class EscapeRoomAgent(BaseAgent):
    """
    EREBUS-7 Escape Room Agent.
    Maintains full game state across conversation turns using LangChain memory.
    """

    def __init__(self):
        super().__init__(
            agent_name="EscapeRoom",
            system_prompt=ESCAPE_ROOM_SYSTEM_PROMPT
        )
        self.game_state = DEFAULT_GAME_STATE.copy()
        self.is_initialized = False

    def initialize(self) -> Dict[str, Any]:
        """Start a new escape room session."""
        self.reset_memory()
        self.game_state = DEFAULT_GAME_STATE.copy()
        self.is_initialized = True
        
        self.logger.info("Initializing new escape room session")
        
        raw_response = self._invoke_llm(ESCAPE_ROOM_INTRO)
        result = parse_escape_room_response(raw_response)
        
        if result.success and result.data.get("game_state"):
            self.game_state = result.data["game_state"]
        
        return {
            "agent": "ESCAPE_ROOM",
            "success": result.success,
            "narrative": result.data.get("narrative", raw_response),
            "game_state": self.game_state,
            "oxygen_level": self.game_state.get("oxygen_level", 23),
            "puzzles_solved": self.game_state.get("puzzles_solved", 0),
            "game_status": self.game_state.get("game_status", "active"),
            "current_puzzle": self.game_state.get("current_puzzle", "POWER_GRID"),
            "solved_list": self.game_state.get("solved_list", []),
            "progress_pct": 0,
            "is_new_session": True
        }

    def process(self, user_message: str) -> Dict[str, Any]:
        """Process a player action and update game state."""
        if not self.is_initialized:
            return self.initialize()
        
        self.logger.info(f"Processing escape room action: {user_message[:60]}")
        
        # Augment user message with current game state context
        context_message = (
            f"{user_message}\n\n"
            f"[SYSTEM CONTEXT: Current oxygen={self.game_state.get('oxygen_level', 23)}%, "
            f"Puzzles solved={self.game_state.get('puzzles_solved', 0)}/5, "
            f"Current puzzle={self.game_state.get('current_puzzle', 'POWER_GRID')}, "
            f"Solved: {self.game_state.get('solved_list', [])}]"
        )
        
        raw_response = self._invoke_llm(context_message)
        result = parse_escape_room_response(raw_response)
        
        # Update stored game state
        if result.success and result.data.get("game_state"):
            self.game_state = result.data["game_state"]
        
        oxygen = self.game_state.get("oxygen_level", 23)
        puzzles = self.game_state.get("puzzles_solved", 0)
        status = self.game_state.get("game_status", "active")
        
        self.logger.info(
            f"Game state | oxygen={oxygen}% | puzzles={puzzles}/5 | status={status}"
        )
        
        return {
            "agent": "ESCAPE_ROOM",
            "success": result.success,
            "narrative": result.data.get("narrative", raw_response),
            "game_state": self.game_state,
            "oxygen_level": oxygen,
            "puzzles_solved": puzzles,
            "game_status": status,
            "current_puzzle": self.game_state.get("current_puzzle", "POWER_GRID"),
            "solved_list": self.game_state.get("solved_list", []),
            "progress_pct": (puzzles / 5) * 100,
            "is_new_session": False
        }

    def reset_game(self):
        """Reset the game for a new playthrough."""
        self.game_state = DEFAULT_GAME_STATE.copy()
        self.is_initialized = False
        self.reset_memory()
        self.logger.info("Escape room game reset")
