"""Детальная статистика игрока — /mystats"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database import Database
from gamedata import get_rank, CLASSES
from safety import guard_handler


class StatsHandler:

    @staticmethod
    @guard_handler()
    async def show(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        db: Database = ctx.bot_data["db"]
        uid = update.effective_user.id
        p = await db.get_player(uid)
        if not p:
            await update.message.reply_text("Сначала /start")
            return
        text = await _build(db, uid, p)
        kb = InlineKeyboardMarkup([[
            InlineKeyboardButton("◀️ Профиль", callback_data="profile")
        ]])
        await update.message.reply_text(text, parse_mode="Markdown", reply_markup=kb)

    @staticmethod
    @guard_handler()
    async def show_cb(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        q = update.callback_query
        await q.answer()
        db: Database = ctx.bot_data["db"]
        uid = q.from_user.id
        p = await db.get_player(uid)
        if not p:
            await q.edit_message_text("Сначала /start")
            return
        text = await _build(db, uid, p)
        kb = InlineKeyboardMarkup([[
            InlineKeyboardButton("◀️ Профиль", callback_data="profile")
        ]])
        await q.edit_message_text(text, parse_mode="Markdown", reply_markup=kb)

    @staticmethod
    @guard_handler()
    async def history(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        db: Database = ctx.bot_data["db"]
        uid = update.effective_user.id
        p = await db.get_player(uid)
        if not p:
            await update.message.reply_text("Сначала /start")
            return
        text = await _build_history(db, uid)
        kb = InlineKeyboardMarkup([[
            InlineKeyboardButton("◀️ Профиль", callback_data="profile")
        ]])
        await update.message.reply_text(text, parse_mode="Markdown", reply_markup=kb)

    @staticmethod
    @guard_handler()
    async def history_cb(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        q = update.callback_query
        await q.answer()
        db: Database = ctx.bot_data["db"]
        uid = q.from_user.id
        text = await _build_history(db, uid)
        kb = InlineKeyboardMarkup([[
            InlineKeyboardButton("◀️ Профиль", callback_data="profile")
        ]])
        await q.edit_message_text(text, parse_mode="Markdown", reply_markup=kb)


async def _build(db: Database, uid: int, p: dict) -> str:
    battles = await db.get_last_battles(uid, 100)
    total   = len(battles)
    wins    = p["wins"]
    losses  = p["losses"]
    wr      = round(wins / max(wins + losses, 1) * 100)
    rank    = get_rank(p.get("mmr", 1000))
    cls     = CLASSES[p["class_id"]]
    streak  = p.get("streak", 0)
    d_streak = p.get("daily_streak", 0)
    achs    = await db.get_achievements(uid)

    return (
        f"📊 *СТАТИСТИКА — {p['first_name']}*\n\n"
        f"⭐ Уровень: *{p['level']}*\n"
        f"{cls['emoji']} Класс: *{cls['name']}*\n"
        f"🏅 Ранг: *{rank}* ({p.get('mmr', 1000)} MMR)\n\n"
        f"*── Бои ──*\n"
        f"⚔️ Всего боёв: *{wins + losses}*\n"
        f"✅ Побед: *{wins}*\n"
        f"❌ Поражений: *{losses}*\n"
        f"📈 Винрейт: *{wr}%*\n"
        f"🔥 Текущая серия: *{streak}*\n\n"
        f"*── Прочее ──*\n"
        f"💰 Золото: *{p['gold']}*\n"
        f"📅 Серия входов: *{d_streak}* дней\n"
        f"🏅 Достижений: *{len(achs)}/14*\n"
    )


async def _build_history(db: Database, uid: int) -> str:
    battles = await db.get_last_battles(uid, 5)
    if not battles:
        return "📋 *История боёв*\n\n_Боёв ещё не было_"

    lines = ["📋 *Последние 5 боёв:*\n"]
    for b in battles:
        is_p1   = b["player1_id"] == uid
        opp_id  = b["player2_id"] if is_p1 else b["player1_id"]
        won     = b["winner_id"] == uid
        is_bot  = b["is_bot"]
        result  = "✅ Победа" if won else "❌ Поражение"

        if is_bot:
            opp_name = "🤖 Бот"
        else:
            opp = await db.get_player(opp_id)
            opp_name = opp["first_name"] if opp else f"ID:{opp_id}"

        lines.append(
            f"{result} vs *{opp_name}*\n"
            f"⚔️ {b['rounds']} раундов | {b['created_at'][:10]}"
        )

    return "\n\n".join(lines)
