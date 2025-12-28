# Creating a Discord Bot

This guide walks you through creating a Discord bot application and getting your bot token.

## Prerequisites

- A Discord account
- A web browser

## Step-by-Step Guide

### 1. Go to Discord Developer Portal

Visit: https://discord.com/developers/applications

Log in with your Discord account if prompted.

### 2. Create a New Application

1. Click the **"New Application"** button (top right)
2. Enter a name for your application (e.g., "My AI Bot")
3. Read and accept the Discord Developer Terms of Service
4. Click **"Create"**

> **Note**: The application name is what users will see when they add your bot to their server.

### 3. Configure Your Application (Optional)

On the **General Information** page, you can:
- Add an app icon (shows up in Discord)
- Add a description
- Add tags

These are optional but make your bot look more professional.

### 4. Create a Bot User

1. Click **"Bot"** in the left sidebar
2. Click **"Add Bot"**
3. Confirm by clicking **"Yes, do it!"**

Your bot user is now created!

### 5. Get Your Bot Token

> **⚠️ IMPORTANT**: Your bot token is like a password. Never share it publicly or commit it to GitHub!

1. Under the **TOKEN** section, click **"Reset Token"**
2. Confirm by clicking **"Yes, do it!"**
3. Click **"Copy"** to copy your token
4. Save it somewhere safe (you'll need it for configuration)

> **Note**: If you lose your token, you can always reset it and get a new one.

### 6. Configure Bot Settings

Still on the **Bot** page, configure these settings:

#### Required Settings

**Privileged Gateway Intents** (scroll down):
- ✅ **MESSAGE CONTENT INTENT** - **REQUIRED** for the bot to read messages
- ✅ Server Members Intent (optional, but recommended)
- ✅ Presence Intent (optional)

> **⚠️ CRITICAL**: Without "Message Content Intent", your bot cannot read message content and won't work!

#### Optional Settings

- **Public Bot**: Toggle OFF if you want only you to be able to add the bot
- **Requires OAuth2 Code Grant**: Leave OFF (not needed)

### 7. Get Your Application ID

1. Click **"General Information"** in the left sidebar
2. Under **APPLICATION ID**, click **"Copy"**
3. Save this ID (you'll need it to invite the bot)

### 8. Generate Bot Invite URL

You can use Discord's URL generator or create it manually:

#### Option A: Use OAuth2 URL Generator

1. Click **"OAuth2"** → **"URL Generator"** in the left sidebar
2. Under **SCOPES**, select:
   - ✅ `bot`
3. Under **BOT PERMISSIONS**, select:
   - ✅ Send Messages
   - ✅ Read Messages/View Channels
   - ✅ Read Message History
   - ✅ Add Reactions (optional)
   - ✅ Attach Files (optional)
   - ✅ Embed Links (optional)
4. Copy the **GENERATED URL** at the bottom

#### Option B: Manual URL

Replace `YOUR_CLIENT_ID` with your Application ID:

```
https://discord.com/api/oauth2/authorize?client_id=YOUR_CLIENT_ID&permissions=274877908992&scope=bot
```

**Permission value `274877908992` includes**:
- View Channels
- Send Messages
- Read Message History
- Add Reactions
- Attach Files
- Embed Links

### 9. Invite Bot to Your Server

1. Open the invite URL in your browser
2. Select a server from the dropdown (you must have "Manage Server" permission)
3. Click **"Continue"**
4. Review the permissions
5. Click **"Authorize"**
6. Complete the CAPTCHA if prompted

Your bot will now appear in your server (offline until you run the code).

## Summary

You now have:
- ✅ Discord bot application created
- ✅ Bot token (keep it secret!)
- ✅ Application ID
- ✅ Message Content Intent enabled
- ✅ Bot invited to your server

## Next Steps

Use your bot token to configure your agent:

### Interactive Manager

```bash
python scripts/manage_agents.py
```

When prompted for "Discord bot token", paste your token.

### YAML Configuration

Add to `agents.yaml`:

```yaml
agents:
  - name: "My Bot"
    discord_token: "YOUR_BOT_TOKEN_HERE"  # Paste your token here
    type: "echo"
    respond_to_dm: true
    memory_scope: "CHANNEL"
    config:
      prefix: "🤖 "
```

Then run:

```bash
python scripts/create_agent.py
python -m src.main
```

## Troubleshooting

### Bot appears offline

**Cause**: The bot code isn't running yet.

**Solution**: Run `python -m src.main` to start the bot server.

### Bot doesn't respond to messages

**Possible causes**:
1. **Message Content Intent not enabled**
   - Go to Bot settings → Enable "Message Content Intent"
   - Restart your bot

2. **Bot lacks permissions**
   - Check the bot has "Send Messages" permission in the channel
   - Check the bot can "View Channel"

3. **Bot is in wrong server**
   - Make sure you invited it to the right server
   - Check the bot appears in the member list

### "Invalid Token" error

**Cause**: Token was copied incorrectly or has been reset.

**Solution**:
1. Go to Bot settings
2. Click "Reset Token"
3. Copy the new token
4. Update your configuration
5. Restart the bot

### Can't find Message Content Intent

**Location**: Bot settings → Scroll down to "Privileged Gateway Intents"

**Note**: This is different from regular permissions!

## Security Best Practices

### ✅ DO

- Keep your token in `.env` file (not in code)
- Add `.env` to `.gitignore`
- Reset your token if it's accidentally exposed
- Use environment variables for tokens

### ❌ DON'T

- Commit tokens to GitHub
- Share tokens publicly
- Hardcode tokens in your code
- Post tokens in Discord or forums

## Additional Resources

- [Discord Developer Portal](https://discord.com/developers/applications)
- [Discord Developer Documentation](https://discord.com/developers/docs)
- [Discord.py Documentation](https://discordpy.readthedocs.io/)

## Quick Reference

| What | Where |
|------|-------|
| Create bot | https://discord.com/developers/applications |
| Get token | Bot settings → Reset Token |
| Enable intents | Bot settings → Privileged Gateway Intents |
| Get Application ID | General Information → Application ID |
| Invite bot | OAuth2 → URL Generator |

---

**Need help?** Check the [README.md](README.md) or [QUICKSTART.md](QUICKSTART.md) for more information.
