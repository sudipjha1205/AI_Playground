"""
Root Orchestrator Agent — classifies user intent via LLM and routes to specialized agents.
Uses true LLM-based classification, not if-else logic.
"""
import json
from typing import Dict, Any, Optional

from langchain_anthropic import ChatAnthropic
from langchain_core.messages import SystemMessage, HumanMessage

from prompts.orchestrator_prompts import ORCHESTRATOR_SYSTEM_PROMPT, ORCHESTRATOR_CLASSIFICATION_PROMPT
from tools.base_tool import safe_json_parse
from utils.logger import get_logger
from utils.config import APP_CONFIG


class OrchestratorAgent:
    """
    Root Orchestrator: Uses Claude to classify intent and route to the correct agent.
    This is NOT simple if-else keyword matching — it uses LLM reasoning.
    """

    VALID_AGENTS = {"ESCAPE_ROOM", "MIND_READER", "PERSONALITY_ANALYZER", "UNKNOWN"}

    def __init__(self):
        self.logger = get_logger("agent.orchestrator")
        self.current_agent: Optional[str] = None
        
        self.llm = ChatAnthropic(
            api_key=APP_CONFIG["api_key"],
            model=APP_CONFIG["model"],
            temperature=0.1,  # Low temp for deterministic routing
            max_tokens=256
        )
        
        self.logger.info("OrchestratorAgent initialized — LLM-based routing active")

    def classify_intent(self, user_message: str) -> Dict[str, Any]:
        """
        Use LLM to classify user intent. Returns routing decision as structured JSON.
        This is the core intelligence of the orchestrator.
        """
        system = ORCHESTRATOR_SYSTEM_PROMPT.format(
            current_agent=self.current_agent or "NONE"
        )
        user = ORCHESTRATOR_CLASSIFICATION_PROMPT.format(
            message=user_message,
            current_agent=self.current_agent or "NONE"
        )
        
        messages = [
            SystemMessage(content=system),
            HumanMessage(content=user)
        ]
        
        self.logger.info(f"Classifying intent | current_agent={self.current_agent}")
        
        response = self.llm.invoke(messages)
        raw = response.content.strip()
        
        self.logger.info(f"Classification raw response: {raw}")
        
        # Parse the JSON routing decision
        result = safe_json_parse(raw, {
            "agent": "UNKNOWN",
            "confidence": 0.5,
            "reasoning": "Could not parse classification"
        })
        
        # Validate agent name
        if result.get("agent") not in self.VALID_AGENTS:
            result["agent"] = "UNKNOWN"
        
        self.logger.info(
            f"Routing decision | agent={result.get('agent')} | "
            f"confidence={result.get('confidence')} | "
            f"reason={result.get('reasoning', '')[:80]}"
        )
        
        return result

    def set_current_agent(self, agent_name: str):
        """Update context with the currently active agent."""
        if agent_name in self.VALID_AGENTS or agent_name is None:
            self.current_agent = agent_name
            self.logger.info(f"Active agent context set to: {agent_name}")

    def reset(self):
        """Reset orchestrator state."""
        self.current_agent = None
        self.logger.info("Orchestrator reset")
