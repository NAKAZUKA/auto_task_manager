codex/design-personal-task-management-bot-ucw49n
Personal Telegram task manager bot with PostgreSQL storage and simple gamification.

## Prerequisites
- [Docker](https://www.docker.com/) (optional)
- Python 3.12
- [uv](https://github.com/astral-sh/uv) for package management
- Telegram bot token from [@BotFather](https://t.me/BotFather)
# Auto Task Manager

Prototype for a personal task manager bot.

## Prerequisites
- [Docker](https://www.docker.com/)
- Python 3.12
- [uv](https://github.com/astral-sh/uv) for package management
main

## Development
Install dependencies:

```bash
uv sync
```

codex/design-personal-task-management-bot-ucw49n
Run the bot (polling):

```bash
export BOT_TOKEN="<your token>"
=======
Run the placeholder application:

```bash
main
uv run python src/auto_task_manager/main.py
```

## Docker
codex/design-personal-task-management-bot-ucw49n
A `docker-compose.yml` is provided to run the bot together with PostgreSQL.
To start the app with a PostgreSQL database:
main

```bash
docker-compose up --build
```
codex/design-personal-task-management-bot-ucw49n

The container expects the `BOT_TOKEN` variable. You can pass it with:

```bash
BOT_TOKEN="<your token>" docker-compose up --build
```
main
