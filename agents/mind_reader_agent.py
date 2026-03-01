"""
Mind Reader Agent — ORACLE psychic AI that guesses what you're thinking.
Uses binary search logic and category elimination via LLM.
"""
from typing import Dict, Any

from agents.base_agent import BaseAgent
from prompts.mind_reader_prompts import MIND_READER_SYSTEM_PROMPT, MIND_READER_INTRO
from tools.mind_reader_tools import parse_mind_reader_response, DEFAULT_MIND_STATE


class MindReaderAgent(BaseAgent):
    """
    ORACLE Mind Reader Agent.
    Guesses user's thought through strategic yes/no questioning.
    """

    def __init__(self):
        super().__init__(
            agent_name="MindReader",
            system_prompt=MIND_READER_SYSTEM_PROMPT
        )
        self.mind_state = DEFAULT_MIND_STATE.copy()
        self.is_initialized = False

    def initialize(self) -> Dict[str, Any]:
        """Begin a new mind reading session."""
        self.reset_memory()
        self.mind_state = DEFAULT_MIND_STATE.copy()
        self.is_initialized = True
        
        self.logger.info("Initializing new mind reader session")
        
        raw_response = self._invoke_llm(MIND_READER_INTRO)
        result = parse_mind_reader_response(raw_response)
        
        if result.success and result.data.get("mind_state"):
            self.mind_state = result.data["mind_state"]
        
        return {
            "agent": "MIND_READER",
            "success": result.success,
            "narrative": result.data.get("narrative", raw_response),
            "mind_state": self.mind_state,
            "phase": self.mind_state.get("phase", "thinking"),
            "questions_asked": 0,
            "questions_left": 10,
            "confidence": 0,
            "final_guess": None,
            "known_facts": [],
            "is_new_session": True
        }

    def process(self, user_message: str) -> Dict[str, Any]:
        """Process user answer and continue questioning."""
        if not self.is_initialized:
            return self.initialize()
        
        self.logger.info(
            f"Processing mind reader response | Q={self.mind_state.get('questions_asked', 0)}"
        )
        
        # Augment with state context
        context_message = (
            f"{user_message}\n\n"
            f"[ORACLE CONTEXT: Questions asked={self.mind_state.get('questions_asked', 0)}, "
            f"Category={self.mind_state.get('category', 'unknown')}, "
            f"Known facts={self.mind_state.get('known_facts', [])}, "
            f"Confidence={self.mind_state.get('confidence', 0)}%]"
        )
        
        raw_response = self._invoke_llm(context_message)
        result = parse_mind_reader_response(raw_response)
        
        if result.success and result.data.get("mind_state"):
            self.mind_state = result.data["mind_state"]
        
        q_asked = self.mind_state.get("questions_asked", 0)
        self.logger.info(
            f"Mind state | phase={self.mind_state.get('phase')} | "
            f"questions={q_asked}/10 | confidence={self.mind_state.get('confidence')}%"
        )
        
        return {
            "agent": "MIND_READER",
            "success": result.success,
            "narrative": result.data.get("narrative", raw_response),
            "mind_state": self.mind_state,
            "phase": self.mind_state.get("phase", "questioning"),
            "questions_asked": q_asked,
            "questions_left": max(0, 10 - q_asked),
            "confidence": self.mind_state.get("confidence", 0),
            "final_guess": self.mind_state.get("final_guess"),
            "known_facts": self.mind_state.get("known_facts", []),
            "category": self.mind_state.get("category", "unknown"),
            "is_new_session": False
        }

    def reset_session(self):
        """Reset for a new game."""
        self.mind_state = DEFAULT_MIND_STATE.copy()
        self.is_initialized = False
        self.reset_memory()
        self.logger.info("Mind reader session reset")
