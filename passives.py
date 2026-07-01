"""Выбор пассивной способности каждые 5 уровней"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database import Database
from gamedata import PASSIVES, CLASSES
from safety import guard_handler


def passive_available(level: int) -> bool:
    return level % 5 == 0 and level > 0


class PassivesHandler:

    @staticmethod
    @guard_handler()
    async def show(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        db: Database = ctx.bot_data["db"]
        uid = update.effective_user.id
        p   = await db.get_player(uid)
        if not p:
            await update.message.reply_text("Сначала /start"); return
        text, kb = _build(p)
        await update.message.reply_text(text, parse_mode="Markdown", reply_markup=kb)

    @staticmethod
    @guard_handler()
    async def show_cb(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        q = update.callback_query; await q.answer()
        db: Database = ctx.bot_data["db"]
        p = await db.get_player(q.from_user.id)
        if not p:
            await q.edit_message_text("Сначала /start"); return
        text, kb = _build(p)
        await q.edit_message_text(text, parse_mode="Markdown", reply_markup=kb)

    @staticmethod
    @guard_handler()
    async def choose(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        q = update.callback_query; await q.answer()
        db: Database = ctx.bot_data["db"]
        uid        = q.from_user.id
        passive_id = q.data.split(":")[1]
        p          = await db.get_player(uid)

        if not p:
            await q.edit_message_text("Сначала /start"); return
        if passive_id not in PASSIVES:
            await q.answer("Неверная пассивка!", show_alert=True); return

        passive = PASSIVES[passive_id]
        await db.update_player(uid, passive_id=passive_id)

        await q.edit_message_text(
            f"✅ *Пассивная способность выбрана!*\n\n"
            f"*{passive['name']}*\n"
            f"_{passive['desc']}_\n\n"
            f"Она будет активна в каждом бою.",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("👤 Профиль", callback_data="profile")
            ]])
        )


def _build(p: dict) -> tuple[str, InlineKeyboardMarkup]:
    current = p.get("passive_id", "")
    cur_passive = PASSIVES.get(current)

    txt = "🔮 *ПАССИВНЫЕ СПОСОБНОСТИ*\n\n"
    if cur_passive:
        txt += f"Текущая: *{cur_passive['name']}*\n_{cur_passive['desc']}_\n\n"
    else:
        txt += "Текущая: _не выбрана_\n\n"

    if passive_available(p["level"]):
        txt += "✅ Доступна смена пассивки!\n\nВыбери:"
    else:
        next_lvl = ((p["level"] // 5) + 1) * 5
        txt += f"_Смена доступна на уровне {next_lvl}_\n\nДоступные способности:"

    buttons = []
    for pid, pas in PASSIVES.items():
        mark = "✅ " if pid == current else ""
        buttons.append([InlineKeyboardButton(
            f"{mark}{pas['name']} — {pas['desc']}",
            callback_data=f"passive_choose:{pid}"
        )])
    buttons.append([InlineKeyboardButton("◀️ Профиль", callback_data="profile")])
    return txt, InlineKeyboardMarkup(buttons)
