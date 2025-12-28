# Discord AI Bot Handler

A lightweight, modular Discord AI bot handler for running AI agents. Built with Python, discord.py, and SQLAlchemy.

## Features

- 🤖 **Multi-Agent Support**: Run multiple Discord bots from a single service instance
- 🔄 **Dynamic Lifecycle**: Start, stop, and update agents on-the-fly without restarting
- 🎯 **Smart Response Logic**: DM responses, @mentions, and reply detection
- 🔐 **Whitelist Support**: Guild and channel-level access control
- 💬 **Per-User Memory**: Each user has their own conversation context
- 🤖 **AI Agents**: Built-in echo and LLM agents (OpenAI/Anthropic)
- 📊 **Database-Backed**: SQLAlchemy with SQLite, PostgreSQL, or MySQL support
- ⚡ **Async/Await**: Fully asynchronous for high performance

## Quick Start

### Prerequisites

- Python 3.10 or higher
- Discord bot token ([Get one here](https://discord.com/developers/applications))

### Installation

1. **Clone and install:**
   ```bash
   git clone <repository-url>
   cd discord_agent
   pip install -e .
   ```

   For LLM support:
   ```bash
   pip install -e ".[llm]"
   ```

2. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

3. **Create your first agent:**
   ```bash
   python scripts/manage_agents.py
   ```

4. **Start the bot:**
   ```bash
   python -m src.main
   ```

## Configuration

### Creating Agents

**Option A: Interactive Manager (Recommended)**
```bash
python scripts/manage_agents.py
```

**Option B: YAML Configuration**

Create `agents.yaml`:
```yaml
agents:
  - name: "My Bot"
    discord_token: "YOUR_BOT_TOKEN"
    type: "llm"  # or "echo"
    respond_to_dm: true
    config:
      provider: "openai"
      model: "gpt-4"
      system_prompt: "You are a helpful assistant."
```

Load agents:
```bash
python scripts/create_agent.py
```

### Agent Settings

| Setting | Type | Description |
|---------|------|-------------|
| `name` | string | Display name for the agent |
| `discord_token` | string | Discord bot token |
| `discord_enabled` | boolean | Enable/disable the bot |
| `respond_to_dm` | boolean | Respond to direct messages |
| `guild_whitelist` | array | Allowed guild IDs (empty = all) |
| `channel_whitelist` | array | Allowed channel IDs (empty = all) |
| `agent_type` | string | `echo` or `llm` |
| `agent_config` | object | Agent-specific configuration |

## Response Behavior

### Direct Messages
- Responds to all DM messages (if `respond_to_dm` is enabled)

### Server Messages
- Responds when **@mentioned**
- Responds when someone **replies** to the bot's message
- Respects guild and channel whitelists

## Agent Types

### Echo Agent
Simple agent that echoes messages with optional prefix/suffix.

```yaml
config:
  prefix: "🤖 "
  suffix: ""
```

### LLM Agent
AI-powered agent using OpenAI or Anthropic.

```yaml
config:
  provider: "openai"  # or "anthropic"
  model: "gpt-4"
  system_prompt: "You are a helpful AI assistant."
  max_history: 10
  temperature: 0.7
  max_tokens: 1000
```

Set your API key in `.env`:
```bash
OPENAI_API_KEY=sk-...
# or
ANTHROPIC_API_KEY=sk-ant-...
```

## Environment Variables

See `.env.example` for all available options:

```bash
# Database
DATABASE_URL=sqlite:///./discord_agents.db

# Discord
DISCORD_NEW_AGENT_POLL_INTERVAL=10
DISCORD_MAX_MESSAGE_LENGTH=2000

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=text  # or json
LOG_FILE=logs/discord_bot.log

# AI Providers
OPENAI_API_KEY=
ANTHROPIC_API_KEY=
```

## Project Structure

```
discord_agent/
├── src/
│   ├── agents/              # Agent implementations
│   │   ├── echo_agent.py
│   │   └── llm_agent.py
│   ├── database/            # Database models and functions
│   ├── services/discord/    # Discord bot pool and handlers
│   ├── utils/               # Logging, message splitting
│   └── main.py              # Entry point
├── scripts/                 # Helper scripts
│   ├── manage_agents.py     # Interactive manager
│   └── create_agent.py      # YAML loader
└── agents.example.yaml      # Example configuration
```

## Development

### Running Tests
```bash
pip install -e ".[dev]"
pytest
```

### Code Formatting
```bash
black src/
ruff check src/
```

## Troubleshooting

### Bot doesn't respond
1. Enable **Message Content Intent** in Discord Developer Portal
2. Verify bot has permission to read/send messages
3. Check logs for errors
4. Verify agent is enabled in database

### Connection issues
1. Verify bot token is correct
2. Check internet connection
3. Review logs for specific errors

## License

MIT License - see LICENSE file for details

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request
