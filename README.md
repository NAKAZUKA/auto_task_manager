Personal Telegram task manager bot with PostgreSQL storage and simple gamification.

## Prerequisites
- [Docker](https://www.docker.com/) (optional)
- Python 3.12
- [uv](https://github.com/astral-sh/uv) for package management
- Telegram bot token from [@BotFather](https://t.me/BotFather)

## Development
Install dependencies:

```bash
uv sync
```

Run the bot (polling):

```bash
export BOT_TOKEN="<your token>"
uv run python src/auto_task_manager/main.py
```

## Docker
A `docker-compose.yml` is provided to run the bot together with PostgreSQL.

```bash
docker-compose up --build
```

The container expects the `BOT_TOKEN` variable. You can pass it with:

```bash
BOT_TOKEN="<your token>" docker-compose up --build
```
