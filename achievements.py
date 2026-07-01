"""Система достижений"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database import Database
from gamedata import ACHIEVEMENTS
from safety import guard_handler


async def check_achievements(db: Database, uid: int, player: dict) -> list[str]:
    """Проверить и выдать новые достижения. Возвращает список сообщений."""
    earned = await db.get_achievements(uid)
    msgs   = []

    checks = {
        "first_blood": player["wins"] >= 1,
        "wins_10":     player["wins"] >= 10,
        "wins_50":     player["wins"] >= 50,
        "wins_100":    player["wins"] >= 100,
        "streak_5":    player.get("streak", 0) >= 5,
        "streak_10":   player.get("streak", 0) >= 10,
        "rich":        player["gold"] >= 1000,
        "level_10":    player["level"] >= 10,
        "level_25":    player["level"] >= 25,
        "level_50":    player["level"] >= 50,
        "daily_7":     player.get("daily_streak", 0) >= 7,
        "mmr_1500":    player.get("mmr", 1000) >= 1500,
        "mmr_2000":    player.get("mmr", 1000) >= 2000,
    }

    for ach_id, condition in checks.items():
        if condition and ach_id not in earned:
            is_new = await db.grant_achievement(uid, ach_id)
            if is_new:
                ach = ACHIEVEMENTS[ach_id]
                reward = ach.get("reward_gold", 0)
                if reward > 0:
                    p = await db.get_player(uid)
                    await db.update_player(uid, gold=p["gold"] + reward)
                msgs.append(
                    f"🏅 *Достижение разблокировано!*\n"
                    f"{ach['name']}\n"
                    f"_{ach['desc']}_"
                    + (f"\n💰 +{reward} золота" if reward else "")
                )

    return msgs


class AchievementsHandler:

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


async def _build(db: Database, uid: int, player: dict) -> tuple[str, InlineKeyboardMarkup]:
    earned = await db.get_achievements(uid)
    total  = len(ACHIEVEMENTS)
    done   = len(earned)

    lines = [f"🏅 *ДОСТИЖЕНИЯ* {done}/{total}\n"]
    for ach_id, ach in ACHIEVEMENTS.items():
        if ach_id in earned:
            lines.append(f"✅ *{ach['name']}*\n_{ach['desc']}_")
        else:
            lines.append(f"🔒 {ach['name']}\n_{ach['desc']}_")

    kb = InlineKeyboardMarkup([[
        InlineKeyboardButton("◀️ Профиль", callback_data="profile")
    ]])
    return "\n\n".join(lines), kb
