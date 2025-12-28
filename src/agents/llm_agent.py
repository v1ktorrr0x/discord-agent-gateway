"""
LLM-powered agent using OpenAI or Anthropic.
"""

from typing import Dict, Any


class LLMAgent:
    """AI agent powered by Large Language Models."""
    
    def __init__(self, agent_id: int, config: Dict[str, Any]):
        """
        Initialize LLM agent.
        
        Args:
            agent_id: Database ID of the agent
            config: Configuration dict with provider, model, etc.
        """
        self.agent_id = agent_id
        self.provider = config.get("provider", "openai")
        self.model = config.get("model", "gpt-4")
        self.system_prompt = config.get("system_prompt", "You are a helpful AI assistant.")
        self.max_history = config.get("max_history", 10)
        self.temperature = config.get("temperature", 0.7)
        self.max_tokens = config.get("max_tokens", 1000)
        
        # Conversation history per chat_id
        self.conversations: Dict[str, list] = {}
        
        # Initialize API client
        self._init_client()
    
    def _init_client(self) -> None:
        """Initialize the LLM API client."""
        try:
            if self.provider == "openai":
                from openai import AsyncOpenAI
                from src.config import settings
                self.client = AsyncOpenAI(api_key=settings.openai_api_key)
            
            elif self.provider == "anthropic":
                from anthropic import AsyncAnthropic
                from src.config import settings
                self.client = AsyncAnthropic(api_key=settings.anthropic_api_key)
            
            else:
                raise ValueError(f"Unsupported provider: {self.provider}")
        
        except ImportError:
            raise ImportError(
                f"Failed to import {self.provider} library. "
                f"Install with: pip install discord-ai-bot-handler[llm]"
            )
    
    async def execute(self, content: str, chat_id: str, use_history: bool = True) -> str:
        """
        Process message using LLM.
        
        Args:
            content: Message content
            chat_id: Chat/conversation ID for history
            use_history: Whether to use conversation history (default: True)
        
        Returns:
            AI-generated response string
        """
        # If history is disabled, just generate response without context
        if not use_history:
            return await self._generate_stateless(content)

        # Initialize conversation history if needed
        # Initialize conversation history if needed
        if chat_id not in self.conversations:
            self.conversations[chat_id] = []
        
        # Add user message to history
        self.conversations[chat_id].append({
            "role": "user",
            "content": content
        })
        
        # Trim history if too long
        if len(self.conversations[chat_id]) > self.max_history * 2:
            self.conversations[chat_id] = self.conversations[chat_id][-(self.max_history * 2):]
        
        # Generate response
        try:
            if self.provider == "openai":
                response_text = await self._generate_openai(chat_id)
            elif self.provider == "anthropic":
                response_text = await self._generate_anthropic(chat_id)
            else:
                response_text = "Error: Unsupported LLM provider"
            
            # Add assistant response to history
            self.conversations[chat_id].append({
                "role": "assistant",
                "content": response_text
            })
            
            return response_text
        
        except Exception as e:
            return f"Sorry, I encountered an error: {str(e)}"
    
    async def _generate_openai(self, chat_id: str) -> str:
        """Generate response using OpenAI API."""
        messages = [
            {"role": "system", "content": self.system_prompt}
        ] + self.conversations[chat_id]
        
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
        )
        
        return response.choices[0].message.content or ""
    
    async def _generate_anthropic(self, chat_id: str) -> str:
        """Generate response using Anthropic API."""
        response = await self.client.messages.create(
            model=self.model,
            system=self.system_prompt,
            messages=self.conversations[chat_id],
            temperature=self.temperature,
            max_tokens=self.max_tokens,
        )
        
        return response.content[0].text if response.content else ""
        return response.content[0].text if response.content else ""

    async def _generate_stateless(self, content: str) -> str:
        """Generate response without history."""
        try:
            if self.provider == "openai":
                messages = [
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": content}
                ]
                response = await self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=self.temperature,
                    max_tokens=self.max_tokens,
                )
                return response.choices[0].message.content or ""
            
            elif self.provider == "anthropic":
                response = await self.client.messages.create(
                    model=self.model,
                    system=self.system_prompt,
                    messages=[{"role": "user", "content": content}],
                    temperature=self.temperature,
                    max_tokens=self.max_tokens,
                )
                return response.content[0].text if response.content else ""
                
            else:
                return "Error: Unsupported LLM provider"
                
        except Exception as e:
            return f"Sorry, I encountered an error: {str(e)}"
