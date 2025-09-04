from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from dateutil import parser
from sqlalchemy import select
from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    Update,
)
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

from .db import async_session
from .gamification import calculate_level
from .models import Task, User

logger = logging.getLogger(__name__)

(
    TITLE,
    DESCRIPTION,
    IMPORTANCE,
    START_DATE,
    DUE_DATE,
    PHOTO,
) = range(6)


def parse_datetime(text: str) -> Optional[datetime]:
    """Parse user supplied datetime string."""
    try:
        dt = parser.parse(text)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except Exception:
        return None


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    async with async_session() as session:
        user = await session.scalar(
            select(User).where(User.tg_id == update.effective_user.id)
        )
        if not user:
            user = User(
                tg_id=update.effective_user.id,
                name=update.effective_user.full_name or "",
            )
            session.add(user)
            await session.commit()
        await update.message.reply_text(
            f"Привет, {user.name}! Уровень {user.level}, очки {user.points}"
        )


async def add_task(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(
        "Введите название задачи", reply_markup=ReplyKeyboardRemove()
    )
    return TITLE


async def title(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["title"] = update.message.text
    await update.message.reply_text("Добавьте описание задачи или /skip")
    return DESCRIPTION


async def description(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["description"] = update.message.text
    keyboard = ReplyKeyboardMarkup(
        [["1", "2", "3", "4", "5"]], one_time_keyboard=True
    )
    await update.message.reply_text(
        "Оцените важность от 1 до 5", reply_markup=keyboard
    )
    return IMPORTANCE


async def skip_description(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["description"] = ""
    keyboard = ReplyKeyboardMarkup(
        [["1", "2", "3", "4", "5"]], one_time_keyboard=True
    )
    await update.message.reply_text(
        "Оцените важность от 1 до 5", reply_markup=keyboard
    )
    return IMPORTANCE


async def importance(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["importance"] = int(update.message.text)
    await update.message.reply_text(
        "Введите дату начала (YYYY-MM-DD HH:MM) или /skip"
    )
    return START_DATE


async def start_date(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    dt = parse_datetime(update.message.text)
    if not dt:
        await update.message.reply_text("Не удалось распознать дату, попробуйте снова")
        return START_DATE
    context.user_data["start_date"] = dt
    await update.message.reply_text(
        "Введите дедлайн (YYYY-MM-DD HH:MM) или /skip"
    )
    return DUE_DATE


async def skip_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["start_date"] = None
    await update.message.reply_text(
        "Введите дедлайн (YYYY-MM-DD HH:MM) или /skip"
    )
    return DUE_DATE


async def due_date(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    dt = parse_datetime(update.message.text)
    if not dt:
        await update.message.reply_text("Не удалось распознать дату, попробуйте снова")
        return DUE_DATE
    context.user_data["due_date"] = dt
    await update.message.reply_text("Отправьте фото или /skip")
    return PHOTO


async def skip_due(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["due_date"] = None
    await update.message.reply_text("Отправьте фото или /skip")
    return PHOTO


async def photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    photo = update.message.photo[-1]
    context.user_data["photo_file_id"] = photo.file_id
    await save_task(update, context)
    return ConversationHandler.END


async def skip_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["photo_file_id"] = None
    await save_task(update, context)
    return ConversationHandler.END


async def save_task(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    data = context.user_data
    async with async_session() as session:
        user = await session.scalar(
            select(User).where(User.tg_id == update.effective_user.id)
        )
        if not user:
            user = User(
                tg_id=update.effective_user.id,
                name=update.effective_user.full_name or "",
            )
            session.add(user)
            await session.commit()
        task = Task(
            user_id=user.id,
            title=data["title"],
            description=data.get("description", ""),
            importance=data.get("importance", 1),
            start_date=data.get("start_date"),
            due_date=data.get("due_date"),
            photo_file_id=data.get("photo_file_id"),
        )
        session.add(task)
        await session.commit()
        if task.start_date:
            context.job_queue.run_once(
                reminder,
                when=task.start_date,
                chat_id=update.effective_chat.id,
                data={"title": task.title, "kind": "start"},
            )
        if task.due_date:
            context.job_queue.run_once(
                reminder,
                when=task.due_date,
                chat_id=update.effective_chat.id,
                data={"title": task.title, "kind": "due"},
                data={"title": task.title},
            )
    await update.message.reply_text("Задача сохранена")


async def reminder(context: ContextTypes.DEFAULT_TYPE) -> None:
    job = context.job
    kind = job.data.get("kind", "due")
    if kind == "start":
        text = f"Пора начать: {job.data['title']}"
    else:
        text = f"Дедлайн: {job.data['title']}"
    await context.bot.send_message(job.chat_id, text)
    await context.bot.send_message(job.chat_id, f"Напоминание: {job.data['title']}")


async def list_tasks(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    async with async_session() as session:
        user = await session.scalar(
            select(User).where(User.tg_id == update.effective_user.id)
        )
        if not user:
            await update.message.reply_text("Нет задач")
            return
        result = await session.scalars(
            select(Task).where(Task.user_id == user.id, Task.completed.is_(False))
        )
        tasks = result.all()
        if not tasks:
            await update.message.reply_text("Нет задач")
            return
        for t in tasks:
            buttons = InlineKeyboardMarkup(
                [[InlineKeyboardButton("✅ Выполнено", callback_data=f"done_{t.id}")]]
            )
            lines = [f"{t.title}"]
            if t.due_date:
                lines.append(f"Дедлайн: {t.due_date:%Y-%m-%d %H:%M}")
            await update.message.reply_text("\n".join(lines), reply_markup=buttons)


async def complete_task(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    task_id = int(query.data.split("_")[1])
    async with async_session() as session:
        task = await session.get(Task, task_id)
        if not task or task.completed:
            await query.edit_message_text("Задача не найдена")
            return
        task.completed = True
        user = await session.get(User, task.user_id)
        points = 10 * task.importance
        user.points += points
        user.level = calculate_level(user.points)
        await session.commit()
    await query.edit_message_text(
        f"Задача выполнена! +{points} очков. Уровень {user.level}"
    )


def build_application(token: str) -> Application:
    app = Application.builder().token(token).build()
    conv = ConversationHandler(
        entry_points=[CommandHandler("add", add_task)],
        states={
            TITLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, title)],
            DESCRIPTION: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, description),
                CommandHandler("skip", skip_description),
            ],
            IMPORTANCE: [MessageHandler(filters.TEXT & ~filters.COMMAND, importance)],
            START_DATE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, start_date),
                CommandHandler("skip", skip_start),
            ],
            DUE_DATE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, due_date),
                CommandHandler("skip", skip_due),
            ],
            PHOTO: [
                MessageHandler(filters.PHOTO, photo),
                CommandHandler("skip", skip_photo),
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    app.add_handler(CommandHandler("start", start))
    app.add_handler(conv)
    app.add_handler(CommandHandler("tasks", list_tasks))
    app.add_handler(CallbackQueryHandler(complete_task, pattern=r"^done_"))
    return app


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Отмена", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END
