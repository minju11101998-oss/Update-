"""
Перековка навыков — /respec
Перераспределение очков Силы/Выносливости/Ловкости/Интуиции
Стоимость: 200 золота
"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database import Database
from gamedata import CLASSES, calc_stats, stats_text
from safety import guard_handler

RESPEC_COST = 200
SKILL_NAMES = {
    "strength":  "✊ Сила",
    "endurance": "♥️ Выносливость",
    "agility":   "💫 Ловкость",
    "intuition": "🧿 Интуиция",
}


class RespecHandler:

    @staticmethod
    @guard_handler()
    async def show(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        db: Database = ctx.bot_data["db"]
        uid = update.effective_user.id
        p = await db.get_player(uid)
        if not p:
            await update.message.reply_text("Сначала /start")
            return
        text, kb = await _build(db, uid, p, ctx)
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
        text, kb = await _build(db, uid, p, ctx)
        await q.edit_message_text(text, parse_mode="Markdown", reply_markup=kb)

    @staticmethod
    @guard_handler()
    async def add_point(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        q = update.callback_query
        await q.answer()
        uid = q.from_user.id
        skill = q.data.split(":")[1]

        # Получить текущее состояние из user_data
        points = ctx.user_data.get("respec_points", {})
        free = ctx.user_data.get("respec_free", 0)

        if free <= 0:
            await q.answer("Нет свободных очков!", show_alert=True)
            return

        points[skill] = points.get(skill, 0) + 1
        ctx.user_data["respec_points"] = points
        ctx.user_data["respec_free"] = free - 1

        db: Database = ctx.bot_data["db"]
        p = await db.get_player(uid)
        text, kb = await _build(db, uid, p, ctx)
        await q.edit_message_text(text, parse_mode="Markdown", reply_markup=kb)

    @staticmethod
    @guard_handler()
    async def remove_point(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        q = update.callback_query
        await q.answer()
        uid = q.from_user.id
        skill = q.data.split(":")[1]

        points = ctx.user_data.get("respec_points", {})
        free = ctx.user_data.get("respec_free", 0)

        if points.get(skill, 0) <= 0:
            await q.answer("Нельзя снять больше!", show_alert=True)
            return

        points[skill] = points.get(skill, 0) - 1
        ctx.user_data["respec_points"] = points
        ctx.user_data["respec_free"] = free + 1

        db: Database = ctx.bot_data["db"]
        p = await db.get_player(uid)
        text, kb = await _build(db, uid, p, ctx)
        await q.edit_message_text(text, parse_mode="Markdown", reply_markup=kb)

    @staticmethod
    @guard_handler()
    async def confirm(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        q = update.callback_query
        await q.answer()
        db: Database = ctx.bot_data["db"]
        uid = q.from_user.id
        p = await db.get_player(uid)

        if not p:
            await q.edit_message_text("Сначала /start")
            return

        free = ctx.user_data.get("respec_free", 0)
        if free > 0:
            await q.answer(f"Распредели все {free} очков!", show_alert=True)
            return

        if p["gold"] < RESPEC_COST:
            await q.answer(f"Нужно {RESPEC_COST}💰!", show_alert=True)
            return

        points = ctx.user_data.get("respec_points", {})
        if not points:
            await q.answer("Нечего применять!", show_alert=True)
            return

        # Применяем в bonus_stats (сохраняем отдельно в БД)
        await db.update_player(uid,
            gold=p["gold"] - RESPEC_COST,
            respec_str=points.get("strength", 0),
            respec_end=points.get("endurance", 0),
            respec_agi=points.get("agility", 0),
            respec_int=points.get("intuition", 0),
        )

        # Сброс user_data
        ctx.user_data.pop("respec_points", None)
        ctx.user_data.pop("respec_free", None)
        ctx.user_data.pop("respec_total", None)

        await q.edit_message_text(
            f"✅ *Навыки перераспределены!*\n\n"
            f"💰 Списано: *{RESPEC_COST}* золота\n\n"
            f"Изменения вступят в силу в следующем бою.",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("👤 Профиль", callback_data="profile")
            ]])
        )

    @staticmethod
    @guard_handler()
    async def reset(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        q = update.callback_query
        await q.answer()
        ctx.user_data.pop("respec_points", None)
        ctx.user_data.pop("respec_free", None)
        ctx.user_data.pop("respec_total", None)
        db: Database = ctx.bot_data["db"]
        p = await db.get_player(q.from_user.id)
        text, kb = await _build(db, q.from_user.id, p, ctx)
        await q.edit_message_text(text, parse_mode="Markdown", reply_markup=kb)


async def _build(db: Database, uid: int, p: dict, ctx) -> tuple[str, InlineKeyboardMarkup]:
    cls = CLASSES[p["class_id"]]

    # Бонусные очки = уровень // 3
    total_bonus = p["level"] // 3

    # Инициализация если первый раз
    if "respec_total" not in ctx.user_data or ctx.user_data.get("respec_total") != total_bonus:
        ctx.user_data["respec_total"] = total_bonus
        ctx.user_data["respec_free"] = total_bonus
        ctx.user_data["respec_points"] = {}

    points = ctx.user_data.get("respec_points", {})
    free = ctx.user_data.get("respec_free", 0)

    lines = [
        f"🔧 *ПЕРЕКОВКА НАВЫКОВ*\n"
        f"💰 Стоимость: *{RESPEC_COST}* | У тебя: *{p['gold']}*\n"
        f"🎯 Свободных очков: *{free}/{total_bonus}*\n\n"
        f"Распредели очки по навыкам:\n"
    ]

    buttons = []
    for skill, skill_name in SKILL_NAMES.items():
        cur = points.get(skill, 0)
        lines.append(f"{skill_name}: +*{cur}*")
        buttons.append([
            InlineKeyboardButton(f"➖ {skill_name}", callback_data=f"respec_rm:{skill}"),
            InlineKeyboardButton(f"➕ {skill_name}", callback_data=f"respec_add:{skill}"),
        ])

    lines.append(f"\n_Базовые навыки класса не меняются_")
    if free == 0 and total_bonus > 0:
        buttons.append([InlineKeyboardButton(
            f"✅ Применить ({RESPEC_COST}💰)", callback_data="respec_confirm"
        )])
    buttons.append([InlineKeyboardButton("🔄 Сбросить", callback_data="respec_reset")])
    buttons.append([InlineKeyboardButton("◀️ Профиль", callback_data="profile")])

    return "\n".join(lines), InlineKeyboardMarkup(buttons)
