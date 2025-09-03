# Auto Task Manager

Prototype for a personal task manager bot.

## Prerequisites
- [Docker](https://www.docker.com/)
- Python 3.12
- [uv](https://github.com/astral-sh/uv) for package management

## Development
Install dependencies:

```bash
uv sync
```

Run the placeholder application:

```bash
uv run python src/auto_task_manager/main.py
```

## Docker
To start the app with a PostgreSQL database:

```bash
docker-compose up --build
```
