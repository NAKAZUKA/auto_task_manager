codex/design-personal-task-management-bot-ucw49n
import asyncio
import logging
import os

from .bot import build_application
from .db import init_db

logging.basicConfig(level=logging.INFO)


def main() -> None:
    token = os.getenv("BOT_TOKEN")
    if not token:
        raise RuntimeError("BOT_TOKEN environment variable not set")
    asyncio.run(init_db())
    app = build_application(token)
    app.run_polling()
=======
def main() -> None:
    print("Auto Task Manager skeleton")
main


if __name__ == "__main__":
    main()
