"""Ежедневная награда — /daily"""

import time
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database import Database
from config import DAILY_BASE_GOLD, DAILY_STREAK_GOLD, DAILY_MAX_STREAK
from handlers.achievements import check_achievements

SECONDS_IN_DAY = 86400


class DailyHandler:

    @staticmethod
    async def claim(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        db: Database = ctx.bot_data["db"]
        uid  = update.effective_user.id
        p    = await db.get_player(uid)
        if not p:
            await update.message.reply_text("Сначала /start")
            return

        now       = int(time.time())
        last      = p.get("last_daily") or 0
        streak    = p.get("daily_streak") or 0
        elapsed   = now - last
        cooldown  = SECONDS_IN_DAY - elapsed

        if cooldown > 0:
            h = cooldown // 3600
            m = (cooldown % 3600) // 60
            await update.message.reply_text(
                f"⏳ Ежедневная награда будет доступна через *{h}ч {m}мин*",
                parse_mode="Markdown"
            )
            return

        # Обновляем серию
        if elapsed < SECONDS_IN_DAY * 2:
            streak = min(streak + 1, DAILY_MAX_STREAK)
        else:
            streak = 1  # серия сброшена

        gold = DAILY_BASE_GOLD + DAILY_STREAK_GOLD * (streak - 1)
        new_gold = p["gold"] + gold

        await db.update_player(uid,
            gold=new_gold,
            last_daily=now,
            daily_streak=streak,
        )

        # Проверка квеста на серию
        await _update_daily_quest(db, uid, streak)

        ach_msgs = await check_achievements(db, uid, await db.get_player(uid))

        streak_bar = "🔥" * streak + "▪️" * (DAILY_MAX_STREAK - streak)
        kb = InlineKeyboardMarkup([[
            InlineKeyboardButton("👤 Профиль", callback_data="profile"),
            InlineKeyboardButton("⚔️ Арена",   callback_data="arena"),
        ]])
        msg = (
            f"🎁 *Ежедневная награда!*\n\n"
            f"💰 +*{gold}* золота\n"
            f"🔥 Серия: *{streak}/{DAILY_MAX_STREAK}* дней\n"
            f"{streak_bar}\n\n"
        )
        if streak < DAILY_MAX_STREAK:
            next_gold = DAILY_BASE_GOLD + DAILY_STREAK_GOLD * streak
            msg += f"_Завтра: +{next_gold} золота_\n"
        else:
            msg += f"_Максимальная серия! 🏆_\n"

        if ach_msgs:
            msg += "\n" + "\n".join(ach_msgs)

        await update.message.reply_text(msg, parse_mode="Markdown", reply_markup=kb)


async def _update_daily_quest(db: Database, uid: int, streak: int):
    quests = await db.get_quests(uid)
    q = quests.get("q_daily3", {})
    if not q.get("completed"):
        prog = min(streak, 3)
        done = 1 if prog >= 3 else 0
        await db.update_quest(uid, "q_daily3", prog, done)
