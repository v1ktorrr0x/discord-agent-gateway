"""
Load agents from YAML configuration file.
Simple, declarative agent setup.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import yaml
from src.database import SessionLocal, init_database, repository
from src.database.models import AgentTable
from src.utils.logger import get_logger

logger = get_logger(__name__)


def load_agents_from_yaml(yaml_file: str = "agents.yaml"):
    """
    Load and create agents from YAML configuration file.
    
    Args:
        yaml_file: Path to YAML config file
    """
    yaml_path = Path(yaml_file)
    
    if not yaml_path.exists():
        print(f"❌ Config file not found: {yaml_file}")
        print(f"\nCreate an {yaml_file} file with your agent configuration.")
        print("See agents.example.yaml for reference.")
        return
    
    try:
        with open(yaml_path, 'r') as f:
            config = yaml.safe_load(f)
        
        if not config or 'agents' not in config:
            print("❌ Invalid config: 'agents' key not found")
            return
        
        # Initialize database
        init_database()
        db = SessionLocal()
        
        try:
            agents_created = 0
            agents_skipped = 0
            
            for agent_config in config['agents']:
                name = agent_config.get('name')
                
                if not name:
                    print("⚠️  Skipping agent without name")
                    agents_skipped += 1
                    continue
                
                # Check if agent already exists
                existing = db.query(AgentTable).filter_by(name=name).first()
                if existing:
                    print(f"⏭️  Agent '{name}' already exists, skipping")
                    agents_skipped += 1
                    continue
                
                # Create agent
                try:
                    agent = repository.create_agent(
                        db,
                        name=name,
                        discord_token=agent_config['discord_token'],
                        agent_type=agent_config.get('type', 'echo'),
                        respond_to_dm=agent_config.get('respond_to_dm', True),
                        agent_config=agent_config.get('config', {}),
                        guild_whitelist=agent_config.get('guild_whitelist', []),
                        channel_whitelist=agent_config.get('channel_whitelist', []),
                    )
                    
                    print(f"✅ Created agent: {name} (ID: {agent.id}, Type: {agent.agent_type})")
                    agents_created += 1
                    
                    logger.info(f"Created agent from YAML: {name}", extra={"agent_id": agent.id})
                
                except Exception as e:
                    print(f"❌ Failed to create agent '{name}': {e}")
                    agents_skipped += 1
            
            print()
            print(f"📊 Summary: {agents_created} created, {agents_skipped} skipped")
            
            if agents_created > 0:
                print()
                print("🚀 Next steps:")
                print("   1. Run: python -m src.main")
                print("   2. Invite your bot(s) to Discord servers")
                print("   3. Start chatting!")
        
        finally:
            db.close()
    
    except yaml.YAMLError as e:
        print(f"❌ YAML parsing error: {e}")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Load Discord Agent Gateway agents from YAML configuration",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Example agents.yaml:

agents:
  - name: "Echo Bot"
    discord_token: "YOUR_BOT_TOKEN_HERE"
    type: "echo"
    respond_to_dm: true
    config:
      prefix: "🔊 "
  
  - name: "AI Assistant"
    discord_token: "YOUR_BOT_TOKEN_HERE"
    type: "llm"
    respond_to_dm: true
    config:
      provider: "openai"
      model: "gpt-4"
      system_prompt: "You are a helpful AI assistant."
      max_history: 10
      temperature: 0.7
      max_tokens: 1000

Note: Memory is now always per-user (personalized conversations).
        """
    )
    
    parser.add_argument(
        "config_file",
        nargs="?",
        default="agents.yaml",
        help="Path to YAML config file (default: agents.yaml)"
    )
    
    args = parser.parse_args()
    
    try:
        load_agents_from_yaml(args.config_file)
    except KeyboardInterrupt:
        print("\n\n❌ Cancelled by user")


if __name__ == "__main__":
    main()
