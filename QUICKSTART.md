# Quick Start Guide

Get your Discord AI bot running in 5 minutes.

## Prerequisites

- Python 3.10+
- Discord account

## Step 1: Get a Discord Bot Token

1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Click "New Application"
3. Go to "Bot" section → "Add Bot"
4. Copy the token
5. Enable these Privileged Gateway Intents:
   - ✅ Message Content Intent
   - ✅ Server Members Intent (optional)

## Step 2: Install

```bash
git clone <repository-url>
cd discord_agent
# Install dependencies (choose one method)
pip install -e ".[llm]"    # Recommended (requires correct build environment)
# OR
pip install -r requirements.txt
```

## Step 3: Configure

```bash
cp .env.example .env
```

Edit `.env` and add your API key (if using LLM):
```bash
OPENAI_API_KEY=sk-...
# or
ANTHROPIC_API_KEY=sk-ant-...
```

## Step 4: Create Agent

```bash
python scripts/manage_agents.py
```

Follow the prompts to create your first agent.

## Step 5: Start Bot

```bash
python -m src.main
```

## Step 6: Invite to Server

1. Go to Discord Developer Portal
2. OAuth2 → URL Generator
3. Select scopes: `bot`
4. Select permissions: `Send Messages`, `Read Messages`, `Read Message History`
5. Copy URL and open in browser
6. Select server and authorize

## Step 7: Test

In Discord:
- **DM the bot**: Just send a message
- **In server**: @mention the bot or reply to its message

## Next Steps

### Using LLM Agent

Make sure you have an API key set in `.env`:
```bash
OPENAI_API_KEY=sk-...
```

Then configure your agent with:
```yaml
type: "llm"
config:
  provider: "openai"
  model: "gpt-4"
  system_prompt: "You are a helpful assistant."
```

### Managing Multiple Bots

Run `python scripts/manage_agents.py` to:
- Create new agents
- Enable/disable agents
- Update configurations
- Delete agents

### Production Deployment

1. Use PostgreSQL instead of SQLite:
   ```bash
   DATABASE_URL=postgresql://user:pass@host/db
   ```

2. Set up as a service (systemd, Docker, etc.)

3. Configure logging:
   ```bash
   LOG_FORMAT=json
   LOG_FILE=logs/bot.log
   ```

## Troubleshooting

**Bot doesn't respond:**
- Check Message Content Intent is enabled
- Verify bot has message permissions
- Check logs for errors

**Can't find messages:**
- Enable Message Content Intent in Developer Portal
- Wait a few minutes for changes to propagate
- Restart your bot

**API errors:**
- Verify API key is correct
- Check account has credits/billing set up
- Review API provider's status page

## Help

- Check `README.md` for full documentation
- Review example configurations in `agents.example.yaml`
- Check logs in terminal output
