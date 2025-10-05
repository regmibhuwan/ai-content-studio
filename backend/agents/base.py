"""
Base Agent Class

Provides abstract foundation for all specialized agents in the content creation pipeline.
All agents inherit from this class and implement the execute() method.
"""

import time
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

from openai import AsyncOpenAI

from backend.config import get_settings
from utils.logger import get_logger

settings = get_settings()
logger = get_logger(__name__)


class AgentResponse:
    """Standardized response format for all agents."""

    def __init__(
        self,
        status: str,
        data: Optional[Dict[str, Any]] = None,
        message: str = "",
        error: Optional[str] = None,
        execution_time: float = 0.0,
    ):
        self.status = status  # "success" or "error"
        self.data = data or {}
        self.message = message
        self.error = error
        self.execution_time = execution_time

    def to_dict(self) -> Dict[str, Any]:
        """Convert response to dictionary."""
        result = {
            "status": self.status,
            "data": self.data,
            "message": self.message,
            "execution_time": self.execution_time,
        }
        if self.error:
            result["error"] = self.error
        return result

    def is_success(self) -> bool:
        """Check if execution was successful."""
        return self.status == "success"


class BaseAgent(ABC):
    """
    Abstract base class for all AI agents.

    Provides common functionality:
    - Logging with agent name
    - OpenAI client access
    - Error handling
    - Execution timing
    - Standardized response format
    """

    def __init__(self, name: str):
        """
        Initialize base agent.

        Args:
            name: Agent name for logging and identification
        """
        self.name = name
        self.logger = get_logger(f"agent.{name}")
        self.settings = settings
        
        # Initialize OpenAI client
        self.llm_client = AsyncOpenAI(api_key=settings.openai_api_key)

    @abstractmethod
    async def execute(self, input_data: Dict[str, Any]) -> AgentResponse:
        """
        Execute the agent's main functionality.

        Must be implemented by all subclasses.

        Args:
            input_data: Input data dictionary with required parameters

        Returns:
            AgentResponse: Standardized response with status and data

        Raises:
            NotImplementedError: If not implemented by subclass
        """
        raise NotImplementedError(f"{self.name} must implement execute()")

    async def run(self, input_data: Dict[str, Any]) -> AgentResponse:
        """
        Execute agent with error handling and timing.

        This is the main entry point - it wraps execute() with logging and error handling.

        Args:
            input_data: Input data dictionary

        Returns:
            AgentResponse: Execution result
        """
        start_time = time.time()
        self.logger.info(f"[{self.name}] Starting execution...")

        try:
            # Validate input
            self._validate_input(input_data)

            # Execute agent logic
            response = await self.execute(input_data)
            
            # Add execution time
            response.execution_time = time.time() - start_time

            self.logger.info(
                f"[{self.name}] Completed successfully in {response.execution_time:.2f}s"
            )
            return response

        except Exception as e:
            execution_time = time.time() - start_time
            self.logger.error(f"[{self.name}] Failed after {execution_time:.2f}s: {str(e)}")
            
            return AgentResponse(
                status="error",
                message=f"{self.name} execution failed",
                error=str(e),
                execution_time=execution_time,
            )

    def _validate_input(self, input_data: Dict[str, Any]) -> None:
        """
        Validate input data before execution.

        Can be overridden by subclasses for custom validation.

        Args:
            input_data: Input data to validate

        Raises:
            ValueError: If validation fails
        """
        if not isinstance(input_data, dict):
            raise ValueError(f"{self.name} requires dict input, got {type(input_data)}")

    async def _call_llm(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> str:
        """
        Call OpenAI LLM with standardized settings.

        Args:
            prompt: User prompt
            system_prompt: System prompt (optional)
            temperature: Temperature override (optional)
            max_tokens: Max tokens override (optional)

        Returns:
            str: LLM response text
        """
        messages = []
        
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        messages.append({"role": "user", "content": prompt})

        self.logger.debug(f"[{self.name}] Calling LLM with {len(prompt)} char prompt")

        response = await self.llm_client.chat.completions.create(
            model=self.settings.llm_model,
            messages=messages,
            temperature=temperature or self.settings.llm_temperature,
            max_tokens=max_tokens or self.settings.max_tokens,
        )

        result = response.choices[0].message.content
        self.logger.debug(f"[{self.name}] LLM returned {len(result)} characters")

        return result

    def log_info(self, message: str) -> None:
        """Log info message with agent name."""
        self.logger.info(f"[{self.name}] {message}")

    def log_debug(self, message: str) -> None:
        """Log debug message with agent name."""
        self.logger.debug(f"[{self.name}] {message}")

    def log_error(self, message: str) -> None:
        """Log error message with agent name."""
        self.logger.error(f"[{self.name}] {message}")

