"""
Base agent class for all GSTSaathi AI agents.
Uses smolagents CodeAgent with Gemini API.
"""
from typing import Any, Dict, List, Optional, Callable
from smolagents import CodeAgent, tool, InferenceClientModel
from langchain_google_genai import ChatGoogleGenerativeAI

from ..config import settings


class BaseAgent:
    """
    Base class for all GSTSaathi agents using smolagents CodeAgent.
    
    Each agent wraps smolagents CodeAgent with custom tools for specific tasks.
    """
    
    def __init__(self, name: str, description: str, tools: List[Callable] = None):
        """
        Initialize base agent with smolagents CodeAgent.
        
        Args:
            name: Agent name
            description: Agent description
            tools: List of tool functions (decorated with @tool)
        """
        self.name = name
        self.description = description
        self.tools: List[Callable] = tools or []
        self._agent: Optional[CodeAgent] = None
    
    def _create_agent(self) -> CodeAgent:
        """
        Create smolagents CodeAgent with registered tools.
        
        Returns:
            Configured CodeAgent instance
        """
        if not self.tools:
            raise ValueError(f"No tools registered for {self.name}")
        
        # Create CodeAgent with Gemini model
        self._agent = CodeAgent(
            tools=self.tools,
            model=InferenceClientModel(
                model_id="google/gemma-2b",  # Fallback model
                token=settings.GEMINI_API_KEY if settings.GEMINI_API_KEY else None,
            ),
            max_steps=5,
            verbosity_level=1,
        )
        
        return self._agent
    
    def add_tool(self, tool_func: Callable) -> None:
        """
        Add a tool to the agent.
        
        Args:
            tool_func: Tool function decorated with @tool
        """
        self.tools.append(tool_func)
        # Reset agent so it picks up new tools
        self._agent = None
    
    def get_tools(self) -> List[Callable]:
        """
        Get all agent tools.
        
        Returns:
            List of tool functions
        """
        return self.tools
    
    def run(self, task: str, additional_context: Optional[Dict] = None) -> Any:
        """
        Run agent task using smolagents CodeAgent.
        
        Args:
            task: Task description/prompt for the agent
            additional_context: Optional context dictionary
            
        Returns:
            Agent execution result
        """
        if self._agent is None:
            self._create_agent()
        
        # Build prompt with context
        prompt = task
        if additional_context:
            prompt += f"\n\nContext:\n{additional_context}"
        
        # Run the agent
        result = self._agent.run(prompt)
        return result
    
    def execute(self, task: str, context: Dict = None) -> Any:
        """
        Execute agent task.
        Subclasses should override this for custom execution logic.
        
        Args:
            task: Task description
            context: Optional context dictionary
            
        Returns:
            Task result
        """
        # Default: use smolagents CodeAgent
        return self.run(task, context)
