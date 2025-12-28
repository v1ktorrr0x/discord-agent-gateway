"""
Interactive Agent Manager
Manage your Discord AI bot agents with an easy-to-use CLI interface.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.database import SessionLocal, init_database, repository
from src.database.models import AgentTable
from src.config import settings
from src.utils.logger import get_logger

logger = get_logger(__name__)


def clear_screen():
    """Clear the terminal screen."""
    import os
    os.system('cls' if os.name == 'nt' else 'clear')


def print_header(title: str):
    """Print a formatted header."""
    print()
    print("=" * 70)
    print(f"  {title}")
    print("=" * 70)
    print()


def list_agents(db):
    """List all agents."""
    clear_screen()
    print_header("📋 Current Agents")
    
    agents = db.query(AgentTable).all()
    
    if not agents:
        print("No agents configured yet.")
        print()
        input("Press Enter to continue...")
        return
    
    for i, agent in enumerate(agents, 1):
        status = "🟢 Enabled" if agent.discord_enabled else "🔴 Disabled"
        print(f"{i}. {agent.name} ({status})")
        print(f"   ID: {agent.id}")
        print(f"   Type: {agent.agent_type}")
        print(f"   Memory: Per-user (personalized)")
        print(f"   DM Response: {'Yes' if agent.respond_to_dm else 'No'}")
        
        if agent.agent_type == "llm" and agent.agent_config:
            config = agent.agent_config
            if isinstance(config, dict):
                provider = config.get('provider', 'unknown')
                model = config.get('model', 'unknown')
                print(f"   Model: {provider}/{model}")
        
        print()
    
    input("Press Enter to continue...")


def create_agent(db):
    """Create a new agent interactively."""
    clear_screen()
    print_header("➕ Create New Agent")
    
    # Name
    name = input("Agent name: ").strip()
    if not name:
        print("❌ Name cannot be empty")
        input("Press Enter to continue...")
        return
    
    # Check if exists
    existing = db.query(AgentTable).filter_by(name=name).first()
    if existing:
        print(f"❌ Agent '{name}' already exists")
        input("Press Enter to continue...")
        return
    
    # Token
    print()
    discord_token = input("Discord bot token: ").strip()
    if not discord_token:
        print("❌ Token cannot be empty")
        input("Press Enter to continue...")
        return
    
    # Auto-detect API keys
    has_openai = bool(settings.openai_api_key)
    has_anthropic = bool(settings.anthropic_api_key)
    
    # Agent type
    print()
    print("Agent Type:")
    print("  1. Echo Agent (simple testing)")
    print("  2. LLM Agent (AI-powered)")
    
    if has_openai or has_anthropic:
        print()
        if has_openai:
            print("  💡 OpenAI API key detected")
        if has_anthropic:
            print("  💡 Anthropic API key detected")
        default_type = "2"
    else:
        print()
        print("  ℹ️  No API keys found. Set OPENAI_API_KEY or ANTHROPIC_API_KEY for LLM agents.")
        default_type = "1"
    
    print()
    choice = input(f"Choose type (1-2) [{default_type}]: ").strip() or default_type
    agent_type = "echo" if choice == "1" else "llm"
    
    # Memory is now always per-user (no configuration needed)
    print()
    print("ℹ️  Memory: Per-user (each user has their own conversation context)")
    
    # DM response
    print()
    respond_to_dm = input("Respond to DMs? (y/n) [y]: ").strip().lower() or "y"
    respond_to_dm = respond_to_dm == "y"
    
    # Agent config
    agent_config = {}
    
    if agent_type == "echo":
        print()
        prefix = input("Echo prefix [🤖 ]: ").strip() or "🤖 "
        agent_config = {"prefix": prefix}
    
    else:  # LLM
        print()
        print("LLM Configuration:")
        
        # Provider
        if has_openai and has_anthropic:
            print("  1. OpenAI")
            print("  2. Anthropic")
            provider_choice = input("Choose provider (1-2) [1]: ").strip() or "1"
            provider = "openai" if provider_choice == "1" else "anthropic"
        elif has_openai:
            provider = "openai"
            print(f"  Provider: {provider} (auto-detected)")
        elif has_anthropic:
            provider = "anthropic"
            print(f"  Provider: {provider} (auto-detected)")
        else:
            provider = input("  Provider (openai/anthropic) [openai]: ").strip() or "openai"
        
        # Model
        if provider == "openai":
            print()
            print("  Common models: gpt-4, gpt-4-turbo, gpt-3.5-turbo")
            model = input("  Model [gpt-4]: ").strip() or "gpt-4"
        else:
            print()
            print("  Common models: claude-3-opus-20240229, claude-3-sonnet-20240229")
            model = input("  Model [claude-3-opus-20240229]: ").strip() or "claude-3-opus-20240229"
        
        # System prompt
        print()
        system_prompt = input("  System prompt [You are a helpful AI assistant.]: ").strip()
        system_prompt = system_prompt or "You are a helpful AI assistant."
        
        agent_config = {
            "provider": provider,
            "model": model,
            "system_prompt": system_prompt,
            "max_history": 10,
            "temperature": 0.7,
            "max_tokens": 1000,
        }
    
    # Create
    print()
    print("Creating agent...")
    
    try:
        agent = repository.create_agent(
            db,
            name=name,
            discord_token=discord_token,
            agent_type=agent_type,
            respond_to_dm=respond_to_dm,
            agent_config=agent_config,
        )
        
        print()
        print("✅ Agent created successfully!")
        print(f"   ID: {agent.id}")
        print(f"   Name: {agent.name}")
        print(f"   Type: {agent.agent_type}")
        
        logger.info(f"Created agent via CLI: {name}", extra={"agent_id": agent.id})
    
    except Exception as e:
        print(f"❌ Error creating agent: {e}")
        logger.error(f"Failed to create agent: {e}", exc_info=True)
    
    print()
    input("Press Enter to continue...")


def update_agent(db):
    """Update an existing agent."""
    clear_screen()
    print_header("✏️  Update Agent")
    
    agents = db.query(AgentTable).all()
    
    if not agents:
        print("No agents to update.")
        input("Press Enter to continue...")
        return
    
    # List agents
    for i, agent in enumerate(agents, 1):
        print(f"{i}. {agent.name} ({agent.agent_type})")
    
    print()
    choice = input("Select agent number (or 0 to cancel): ").strip()
    
    if not choice.isdigit() or int(choice) < 1 or int(choice) > len(agents):
        return
    
    agent = agents[int(choice) - 1]
    
    print()
    print(f"Updating: {agent.name}")
    print()
    print("What would you like to update?")
    print("  1. Enable/Disable")
    print("  2. DM Response")
    print("  3. System Prompt (LLM only)")
    print("  0. Cancel")
    
    print()
    update_choice = input("Choose option: ").strip()
    
    if update_choice == "1":
        agent.discord_enabled = not agent.discord_enabled
        status = "enabled" if agent.discord_enabled else "disabled"
        print(f"✅ Agent {status}")
    
    elif update_choice == "2":
        agent.respond_to_dm = not agent.respond_to_dm
        status = "enabled" if agent.respond_to_dm else "disabled"
        print(f"✅ DM response {status}")
    
    elif update_choice == "3":
        if agent.agent_type == "llm" and isinstance(agent.agent_config, dict):
            print()
            new_prompt = input("New system prompt: ").strip()
            if new_prompt:
                agent.agent_config["system_prompt"] = new_prompt
                print("✅ System prompt updated")
        else:
            print("❌ Only available for LLM agents")
    
    db.commit()
    print()
    input("Press Enter to continue...")


def delete_agent(db):
    """Delete an agent."""
    clear_screen()
    print_header("🗑️  Delete Agent")
    
    agents = db.query(AgentTable).all()
    
    if not agents:
        print("No agents to delete.")
        input("Press Enter to continue...")
        return
    
    # List agents
    for i, agent in enumerate(agents, 1):
        print(f"{i}. {agent.name}")
    
    print()
    choice = input("Select agent number to delete (or 0 to cancel): ").strip()
    
    if not choice.isdigit() or int(choice) < 1 or int(choice) > len(agents):
        return
    
    agent = agents[int(choice) - 1]
    
    print()
    confirm = input(f"⚠️  Delete '{agent.name}'? This cannot be undone! (yes/no): ").strip().lower()
    
    if confirm == "yes":
        repository.delete_agent(db, agent.id)
        print(f"✅ Agent '{agent.name}' deleted")
        logger.info(f"Deleted agent via CLI: {agent.name}", extra={"agent_id": agent.id})
    else:
        print("❌ Cancelled")
    
    print()
    input("Press Enter to continue...")


def main_menu():
    """Display main menu and handle user choice."""
    init_database()
    db = SessionLocal()
    
    try:
        while True:
            clear_screen()
            print_header("🤖 Discord AI Bot - Agent Manager")
            
            print("What would you like to do?")
            print()
            print("  1. 📋 List all agents")
            print("  2. ➕ Create new agent")
            print("  3. ✏️  Update agent")
            print("  4. 🗑️  Delete agent")
            print("  0. 🚪 Exit")
            print()
            
            choice = input("Enter your choice: ").strip()
            
            if choice == "1":
                list_agents(db)
            elif choice == "2":
                create_agent(db)
            elif choice == "3":
                update_agent(db)
            elif choice == "4":
                delete_agent(db)
            elif choice == "0":
                print()
                print("👋 Goodbye!")
                break
            else:
                print("❌ Invalid choice")
                input("Press Enter to continue...")
    
    finally:
        db.close()


def main():
    """Main entry point."""
    try:
        main_menu()
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
