"""Ежедневная награда — /daily"""

import time
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database import Database
from config import DAILY_BASE_GOLD, DAILY_STREAK_GOLD, DAILY_MAX_STREAK
from safety import safe_notify_achievements, safe_call

logger = logging.getLogger(__name__)

SECONDS_IN_DAY = 86400


class DailyHandler:

    @staticmethod
    async def claim(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        try:
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

            # ── КРИТИЧНЫЙ ШАГ: награда должна записаться в БД ────────────────
            await db.update_player(uid,
                gold=new_gold,
                last_daily=now,
                daily_streak=streak,
            )

            # ── НЕОБЯЗАТЕЛЬНЫЕ ШАГИ: не должны блокировать ответ юзеру ───────
            await safe_call(_update_daily_quest, db, uid, streak,
                            label="daily_quest_update")

            p_fresh  = await db.get_player(uid) or p
            ach_text = await safe_notify_achievements(db, uid, p_fresh)

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

            msg += ach_text

            await update.message.reply_text(msg, parse_mode="Markdown", reply_markup=kb)

        except Exception as e:
            logger.error(f"DailyHandler.claim critical error: {e}")
            try:
                await update.message.reply_text(
                    "⚠️ Не удалось выдать награду. Если золото не пришло — "
                    "напиши администратору."
                )
            except Exception:
                pass


async def _update_daily_quest(db: Database, uid: int, streak: int):
    quests = await db.get_quests(uid)
    q = quests.get("q_daily3", {})
    if not q.get("completed"):
        prog = min(streak, 3)
        done = 1 if prog >= 3 else 0
        await db.update_quest(uid, "q_daily3", prog, done)
