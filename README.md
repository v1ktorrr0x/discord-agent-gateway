# Discord Agent Gateway

A lightweight, modular, and production-ready handler for running multiple AI agents on Discord. Built with Python, `discord.py`, and SQLAlchemy.

## 🚀 Key Features

*   **Multi-Agent Architecture**: Run dozens of distinct bot personalities from a single service.
*   **Per-User Memory**: Every agent maintains personalized conversation strings for each user.
*   **Hot-Reloading**: Add, update, or remove agents instantly without restarting the server.
*   **LLM Ready**: Native support for OpenAI and Anthropic agents out of the box.

## ⚡ 5-Second Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Configure environment
cp .env.example .env
# (Edit .env with your keys)

# 3. Create your first agent
python scripts/manage_agents.py

# 4. Run the server
python -m src.main
```

## 📚 Documentation

*   **[Quick Start Guide](QUICKSTART.md)**: Detailed step-by-step setup instructions.
*   **[Setup Wizard](scripts/manage_agents.py)**: Interactive tool to manage your bots.
*   **[Project Summary](PROJECT_SUMMARY.md)**: Deep dive into the architecture.

## 🛠️ Management

Use the interactive CLI to manage your fleet:

```bash
python scripts/manage_agents.py
```
*Create agents, update system prompts, and toggle bots on/off in real-time.*

## 🧪 Development

Run the test suite to ensure everything is working:

```bash
pip install -e ".[dev]"
pytest
```

---
MIT License.
