# Discord AI Bot Handler - Project Overview

A lightweight Discord AI bot handler for running multiple AI agents from a single service.

## What It Does

This project provides a complete Discord bot framework that:
- Runs multiple Discord bots from one service
- Manages AI-powered conversations with per-user memory
- Supports both OpenAI and Anthropic language models
- Handles bot lifecycle management automatically
- Provides easy agent configuration via CLI or YAML

## Architecture

### System Overview

```
Discord Messages → Bot Pool → Message Handler → AI Agent → Response
                       ↓
                  Scheduler ← Database
```

### Core Components

- **Bot Pool**: Manages multiple Discord bot instances concurrently
- **Agent Scheduler**: Polls database and syncs bot states
- **Message Handler**: Processes incoming messages and determines responses
- **AI Agents**: Execute message processing (echo or LLM-based)
- **Database**: Stores agent configurations and bot information

## Technology Stack

- **Language**: Python 3.10+
- **Discord**: discord.py 2.3+
- **Database**: SQLAlchemy 2.0+
- **AI**: OpenAI, Anthropic (optional)
- **Config**: python-dotenv, PyYAML
- **Async**: asyncio, aiohttp

## Project Statistics

- **Python Modules**: 15
- **Lines of Code**: ~1,500
- **Components**: 5 major subsystems
- **Agent Types**: 2 built-in (echo, LLM)
- **Setup Methods**: 2 (interactive + YAML)

## Key Features

### Multi-Agent Support
- Single service manages multiple Discord bots
- Each bot runs independently with isolated state
- Up to 50 concurrent bots (configurable)

### Per-User Memory
- Each user has their own conversation context
- Memory persists across channels and DMs
- Prevents cross-talk between users

### Smart Response Logic
- Responds to @mentions
- Responds to message replies
- Configurable DM responses
- Guild/channel whitelists

### Dynamic Lifecycle
- Automatic bot startup for enabled agents
- Hot-reload configuration changes
- Token changes trigger restart
- Graceful shutdown with timeout

### Database-Backed
- SQLAlchemy ORM
- Support for SQLite, PostgreSQL, MySQL
- Automatic schema creation
- Simple function-based operations

## Configuration

Agents are configured with:
- Name and Discord token
- Agent type (echo or LLM)
- Response settings (DM, whitelists)
- Agent-specific config (model, prompts, etc.)

## Usage Patterns

### Development
1. Create agent via interactive manager
2. Test with echo agent first
3. Configure LLM agent with API key
4. Deploy to server

### Production
1. Define agents in YAML
2. Use PostgreSQL for database
3. Configure logging to files
4. Monitor via structured logs

## File Organization

```
src/
├── agents/              # AI agent implementations
├── database/            # Models and DB operations
├── services/discord/    # Discord integration
├── utils/               # Logging, utilities
└── main.py              # Application entry

scripts/
├── manage_agents.py     # Interactive CLI
└── create_agent.py      # YAML loader
```

## Agent Types

### Echo Agent
- Simple testing agent
- Echoes messages with prefix/suffix
- No external dependencies
- Useful for testing bot connectivity

### LLM Agent
- AI-powered conversations
- OpenAI or Anthropic support
- Configurable model and parameters
- Per-user conversation history

## Development Workflow

1. **Setup**: Install dependencies, configure .env
2. **Create**: Use interactive manager or YAML
3. **Test**: Run locally with echo agent
4. **Deploy**: Add LLM agent with API keys
5. **Monitor**: Check logs and database

## Next Steps

### Getting Started
1. Clone repository
2. Install dependencies: `pip install -e .`
3. Create .env file
4. Create first agent: `python scripts/manage_agents.py`
5. Start bot: `python -m src.main`

### For LLM Support
1. Install LLM extras: `pip install -e ".[llm]"`
2. Get API key from OpenAI or Anthropic
3. Add to .env file
4. Configure agent with provider and model

### For Production
1. Use PostgreSQL instead of SQLite
2. Configure structured logging (JSON)
3. Set up log rotation
4. Monitor database and bot pool

## License

MIT License

## Status

**Version**: 0.1.0  
**Status**: Production Ready  
**Last Updated**: 2025-12-28
