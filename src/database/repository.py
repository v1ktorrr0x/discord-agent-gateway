"""
Database operations for agents.
Simple function-based access to agent data.
"""

from typing import List, Optional
from sqlalchemy.orm import Session

from src.database.models import AgentTable


def get_all_enabled(db: Session) -> List[AgentTable]:
    """Get all agents with Discord enabled."""
    return db.query(AgentTable).filter(AgentTable.discord_enabled == True).all()


def get_by_id(db: Session, agent_id: int) -> Optional[AgentTable]:
    """Get agent by ID."""
    return db.query(AgentTable).filter(AgentTable.id == agent_id).first()


def create_agent(
    db: Session,
    name: str,
    discord_token: str,
    agent_type: str = "echo",
    respond_to_dm: bool = True,
    agent_config: dict = None,
    guild_whitelist: list = None,
    channel_whitelist: list = None,
) -> AgentTable:
    """Create a new agent with per-user memory."""
    agent = AgentTable(
        name=name,
        discord_token=discord_token,
        discord_enabled=True,
        respond_to_dm=respond_to_dm,
        guild_whitelist=guild_whitelist or [],
        channel_whitelist=channel_whitelist or [],
        agent_type=agent_type,
        agent_config=agent_config or {},
    )
    
    db.add(agent)
    db.commit()
    db.refresh(agent)
    return agent


def update_bot_info(
    db: Session,
    agent_id: int,
    user_id: str,
    username: str,
    display_name: str = None,
) -> Optional[AgentTable]:
    """Update bot identity information."""
    agent = get_by_id(db, agent_id)
    if not agent:
        return None
    
    agent.discord_bot_user_id = user_id
    agent.discord_bot_username = username
    agent.discord_bot_display_name = display_name
    
    db.commit()
    db.refresh(agent)
    return agent


def delete_agent(db: Session, agent_id: int) -> bool:
    """Delete an agent."""
    agent = get_by_id(db, agent_id)
    if not agent:
        return False
    
    db.delete(agent)
    db.commit()
    return True
