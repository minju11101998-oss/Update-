"""Система квестов — /quests"""

import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database import Database
from gamedata import QUESTS
from config import EXP_BASE, EXP_SCALE, MAX_LEVEL
from safety import guard_handler

logger = logging.getLogger(__name__)


def exp_for_level(lvl: int) -> int:
    return int(EXP_BASE * (lvl ** EXP_SCALE))


class QuestsHandler:

    @staticmethod
    @guard_handler()
    async def show(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        db: Database = ctx.bot_data["db"]
        uid = update.effective_user.id
        p   = await db.get_player(uid)
        if not p:
            await update.message.reply_text("Сначала /start")
            return
        text, kb = await _build(db, uid, p)
        await update.message.reply_text(text, parse_mode="Markdown", reply_markup=kb)

    @staticmethod
    @guard_handler()
    async def show_cb(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        q = update.callback_query
        await q.answer()
        db: Database = ctx.bot_data["db"]
        uid = q.from_user.id
        p   = await db.get_player(uid)
        if not p:
            await q.edit_message_text("Сначала /start")
            return
        text, kb = await _build(db, uid, p)
        await q.edit_message_text(text, parse_mode="Markdown", reply_markup=kb)

    @staticmethod
    @guard_handler("⚠️ Не удалось забрать награду. Попробуй снова.")
    async def claim(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        q = update.callback_query
        await q.answer()
        db: Database = ctx.bot_data["db"]
        uid = q.from_user.id

        parts = q.data.split(":")
        if len(parts) < 2:
            await q.answer("Некорректный запрос.", show_alert=True)
            return
        quest_id = parts[1]

        p = await db.get_player(uid)
        if not p:
            await q.edit_message_text("Сначала /start")
            return

        quests = await db.get_quests(uid)
        qdata  = quests.get(quest_id)
        quest  = QUESTS.get(quest_id)

        if not quest or not qdata:
            await q.answer("Квест не найден!", show_alert=True)
            return
        if not qdata["completed"]:
            await q.answer("Квест ещё не выполнен!", show_alert=True)
            return
        if qdata["claimed"]:
            await q.answer("Награда уже получена!", show_alert=True)
            return

        # Выдать награду
        gold = quest["reward_gold"]
        exp  = quest["reward_exp"]
        new_gold = p["gold"] + gold
        new_exp  = p["exp"] + exp

        # Проверка повышения уровня
        leveled = False
        new_lvl = p["level"]
        if new_lvl < MAX_LEVEL and new_exp >= exp_for_level(new_lvl):
            new_exp -= exp_for_level(new_lvl)
            new_lvl += 1
            leveled = True

        await db.update_player(uid, gold=new_gold, exp=new_exp, level=new_lvl)
        await db.claim_quest(uid, quest_id)

        msg = (
            f"✅ *Квест выполнен!*\n\n"
            f"*{quest['name']}*\n\n"
            f"💰 +{gold} золота\n"
            f"✨ +{exp} опыта"
            + ("\n🎉 *Повышение уровня!*" if leveled else "")
        )
        p_new = await db.get_player(uid)
        text, kb = await _build(db, uid, p_new)
        await q.edit_message_text(
            msg + "\n\n" + text,
            parse_mode="Markdown", reply_markup=kb
        )


async def _build(db: Database, uid: int, p: dict) -> tuple[str, InlineKeyboardMarkup]:
    quests     = await db.get_quests(uid)
    lines      = ["📜 *ЗАДАНИЯ*\n"]
    buttons    = []

    for qid, quest in QUESTS.items():
        qdata    = quests.get(qid, {"progress": 0, "completed": 0, "claimed": 0})
        progress = qdata["progress"]
        target   = quest["target"]
        done     = qdata["completed"]
        claimed  = qdata["claimed"]

        # Обновить прогресс из текущих данных игрока
        current_val = _get_progress(p, quest["type"])
        if current_val > progress and not done:
            progress = min(current_val, target)
            done = 1 if progress >= target else 0

        bar = _bar(progress, target)

        if claimed:
            status = "✅ Получено"
            icon   = "✅"
        elif done:
            status = "🎁 Забрать"
            icon   = "🎁"
        else:
            status = f"{progress}/{target}"
            icon   = "📋"

        lines.append(
            f"{icon} *{quest['name']}*\n"
            f"_{quest['desc']}_\n"
            f"`{bar}` {status}\n"
            f"💰 {quest['reward_gold']}  ✨ {quest['reward_exp']}"
        )

        if done and not claimed:
            buttons.append([InlineKeyboardButton(
                f"🎁 Забрать: {quest['name']}",
                callback_data=f"quest_claim:{qid}"
            )])

    buttons.append([InlineKeyboardButton("◀️ Профиль", callback_data="profile")])
    return "\n\n".join(lines), InlineKeyboardMarkup(buttons)


def _get_progress(p: dict, quest_type: str) -> int:
    return {
        "wins":         p.get("wins", 0),
        "battles":      p.get("wins", 0) + p.get("losses", 0),
        "daily_streak": p.get("daily_streak", 0),
        "level":        p.get("level", 1),
        "gold":         p.get("gold", 0),
    }.get(quest_type, 0)


def _bar(val: int, total: int, n: int = 8) -> str:
    f = round(min(val, total) / max(total, 1) * n)
    return "█" * f + "░" * (n - f)


async def update_battle_quests(db: Database, uid: int, won: bool):
    """Вызывать после каждого боя"""
    p      = await db.get_player(uid)
    quests = await db.get_quests(uid)

    for qid, quest in QUESTS.items():
        qdata = quests.get(qid, {"progress": 0, "completed": 0, "claimed": 0})
        if qdata["completed"]:
            continue
        current = _get_progress(p, quest["type"])
        if current >= quest["target"]:
            await db.update_quest(uid, qid, current, 1)
