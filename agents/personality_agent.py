"""
Personality Analyzer Agent — PSYCHE deep personality profiler.
5-question interview followed by comprehensive Big Five + archetype analysis.
"""
from typing import Dict, Any

from agents.base_agent import BaseAgent
from prompts.personality_prompts import PERSONALITY_ANALYZER_SYSTEM_PROMPT, PERSONALITY_ANALYZER_INTRO
from tools.personality_tools import parse_personality_response, format_big_five_chart, DEFAULT_ANALYSIS_STATE


class PersonalityAnalyzerAgent(BaseAgent):
    """
    PSYCHE Personality Analyzer Agent.
    Conducts structured 5-question interview then delivers comprehensive report.
    """

    def __init__(self):
        super().__init__(
            agent_name="PersonalityAnalyzer",
            system_prompt=PERSONALITY_ANALYZER_SYSTEM_PROMPT
        )
        self.analysis_state = DEFAULT_ANALYSIS_STATE.copy()
        self.is_initialized = False

    def initialize(self) -> Dict[str, Any]:
        """Begin a new personality analysis session."""
        self.reset_memory()
        self.analysis_state = DEFAULT_ANALYSIS_STATE.copy()
        self.is_initialized = True
        
        self.logger.info("Initializing personality analysis session")
        
        raw_response = self._invoke_llm(PERSONALITY_ANALYZER_INTRO)
        result = parse_personality_response(raw_response)
        
        if result.success and result.data.get("analysis_state"):
            self.analysis_state = result.data["analysis_state"]
        
        return {
            "agent": "PERSONALITY_ANALYZER",
            "success": result.success,
            "narrative": result.data.get("narrative", raw_response),
            "analysis_state": self.analysis_state,
            "phase": "interviewing",
            "questions_asked": 0,
            "current_question": 1,
            "report_ready": False,
            "big_five": {},
            "formatted_traits": [],
            "archetype": None,
            "mbti_type": None,
            "progress_pct": 0,
            "is_new_session": True
        }

    def process(self, user_message: str) -> Dict[str, Any]:
        """Process a user answer and continue the analysis."""
        if not self.is_initialized:
            return self.initialize()
        
        q_num = self.analysis_state.get("questions_asked", 0)
        self.logger.info(f"Processing personality response | Q={q_num}/5")
        
        # Context augmentation
        context_message = (
            f"{user_message}\n\n"
            f"[PSYCHE CONTEXT: Questions asked={q_num}, "
            f"Phase={self.analysis_state.get('phase', 'interviewing')}, "
            f"Report ready={self.analysis_state.get('report_ready', False)}]"
        )
        
        raw_response = self._invoke_llm(context_message)
        result = parse_personality_response(raw_response)
        
        if result.success and result.data.get("analysis_state"):
            self.analysis_state = result.data["analysis_state"]
        
        # Format Big Five if available
        big_five = self.analysis_state.get("big_five", {})
        formatted_traits = []
        if any(v is not None for v in big_five.values()):
            chart_result = format_big_five_chart(big_five)
            if chart_result.success:
                formatted_traits = chart_result.data.get("traits", [])
        
        report_ready = self.analysis_state.get("report_ready", False)
        q_asked = self.analysis_state.get("questions_asked", 0)
        
        self.logger.info(
            f"Analysis state | phase={self.analysis_state.get('phase')} | "
            f"q={q_asked}/5 | report_ready={report_ready} | "
            f"archetype={self.analysis_state.get('archetype')}"
        )
        
        return {
            "agent": "PERSONALITY_ANALYZER",
            "success": result.success,
            "narrative": result.data.get("narrative", raw_response),
            "analysis_state": self.analysis_state,
            "phase": self.analysis_state.get("phase", "interviewing"),
            "questions_asked": q_asked,
            "current_question": self.analysis_state.get("current_question", q_asked + 1),
            "report_ready": report_ready,
            "big_five": big_five,
            "formatted_traits": formatted_traits,
            "archetype": self.analysis_state.get("archetype"),
            "mbti_type": self.analysis_state.get("mbti_type"),
            "progress_pct": (q_asked / 5) * 100,
            "questions_left": max(0, 5 - q_asked),
            "is_new_session": False
        }

    def reset_session(self):
        """Reset for a new analysis."""
        self.analysis_state = DEFAULT_ANALYSIS_STATE.copy()
        self.is_initialized = False
        self.reset_memory()
        self.logger.info("Personality analyzer session reset")
