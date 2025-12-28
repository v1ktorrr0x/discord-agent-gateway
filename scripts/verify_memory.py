
import asyncio
import os
from unittest.mock import MagicMock, AsyncMock

# Set dummy API key to pass validation
os.environ["OPENAI_API_KEY"] = "sk-dummy-key"

from src.agents.llm_agent import LLMAgent

async def test_llm_memory():
    print("Testing LLMAgent Memory Logic...")
    
    # Mock config
    config = {
        "provider": "openai",
        "model": "gpt-4",
        "system_prompt": "You are a helpful assistant."
    }
    
    # Mock dependencies
    agent = LLMAgent(agent_id=1, config=config)
    agent.client = AsyncMock()
    
    # Mock OpenAI response
    mock_response = MagicMock()
    mock_response.choices = [MagicMock(message=MagicMock(content="Response"))]
    agent.client.chat.completions.create.return_value = mock_response
    
    chat_id = "test-user-1"
    
    # Test 1: Stateful Interaction (DM)
    print("\n--- Test 1: Stateful Interaction (DM) ---")
    await agent.execute("My name is Alice", chat_id, use_history=True)
    
    # Check history
    if len(agent.conversations[chat_id]) == 2: # User + Assistant
        print("✅ History stored correctly (2 messages)")
    else:
        print(f"❌ History failed: {len(agent.conversations.get(chat_id, []))} messages")
        
    # Test 2: Stateless Interaction (Server)
    print("\n--- Test 2: Stateless Interaction (Server) ---")
    await agent.execute("What is my name?", chat_id, use_history=False)
    
    # History should NOT increase
    if len(agent.conversations[chat_id]) == 2:
        print("✅ History unchanged (correct behavior)")
    else:
        print(f"❌ History incorrectly modified: {len(agent.conversations[chat_id])} messages")

    print("\nTests Completed.")

if __name__ == "__main__":
    asyncio.run(test_llm_memory())
