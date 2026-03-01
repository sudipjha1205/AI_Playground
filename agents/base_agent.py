"""
Base Agent class — all agents inherit from this.
Provides LangChain ChatAnthropic integration with per-agent memory.
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional

from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.chat_history import InMemoryChatMessageHistory

from utils.logger import get_logger
from utils.config import APP_CONFIG


class BaseAgent(ABC):
    """
    Abstract base class for all playground agents.
    Each agent has its own isolated memory instance.
    """

    def __init__(self, agent_name: str, system_prompt: str):
        self.agent_name = agent_name
        self.system_prompt = system_prompt
        self.logger = get_logger(f"agent.{agent_name}")
        
        # Each agent has its own isolated memory
        self.memory = InMemoryChatMessageHistory()
        
        # Initialize LLM
        self.llm = ChatAnthropic(
            api_key=APP_CONFIG["api_key"],
            model=APP_CONFIG["model"],
            temperature=APP_CONFIG["temperature"],
            max_tokens=APP_CONFIG["max_tokens"]
        )
        
        self.logger.info(f"Agent '{agent_name}' initialized with isolated memory")

    def _build_messages(self, user_message: str) -> List:
        """Build the full message list including system prompt and history."""
        messages = [SystemMessage(content=self.system_prompt)]
        
        # Add conversation history
        for msg in self.memory.messages:
            messages.append(msg)
        
        # Add current user message
        messages.append(HumanMessage(content=user_message))
        return messages

    def _invoke_llm(self, user_message: str) -> str:
        """Invoke the LLM with memory context and return raw response."""
        messages = self._build_messages(user_message)
        self.logger.info(f"Invoking LLM | history_len={len(self.memory.messages)} | user_msg_len={len(user_message)}")
        
        response = self.llm.invoke(messages)
        raw_content = response.content
        
        # Store in memory
        self.memory.add_user_message(user_message)
        self.memory.add_ai_message(raw_content)
        
        self.logger.info(f"LLM responded | response_len={len(raw_content)}")
        return raw_content

    def reset_memory(self):
        """Clear the agent's conversation memory."""
        self.memory.clear()
        self.logger.info(f"Memory cleared for agent '{self.agent_name}'")

    def get_history_length(self) -> int:
        return len(self.memory.messages)

    @abstractmethod
    def process(self, user_message: str) -> Dict[str, Any]:
        """Process a user message and return structured result."""
        pass

    @abstractmethod
    def initialize(self) -> Dict[str, Any]:
        """Initialize the agent for a new session."""
        pass
