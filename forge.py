"""
Кузница — /forge
Улучшение предметов до +5, каждый уровень +10% к статам
Стоимость растёт экспоненциально
"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database import Database
from gamedata import SLOTS, ITEMS, get_item_stats
from safety import guard_handler

MAX_FORGE = 5

FORGE_COST = {1: 150, 2: 300, 3: 600, 4: 1200, 5: 2500}
FORGE_BONUS = {1: 0.10, 2: 0.20, 3: 0.35, 4: 0.55, 5: 0.80}  # % к базовым статам


def get_forge_level(uid_forges: dict, slot: str) -> int:
    return uid_forges.get(slot, 0)


def apply_forge(base_stats: dict, forge_lvl: int) -> dict:
    if forge_lvl <= 0:
        return base_stats
    mult = 1 + FORGE_BONUS[min(forge_lvl, MAX_FORGE)]
    return {k: round(v * mult, 1) if isinstance(v, (int, float)) else v
            for k, v in base_stats.items()}


class ForgeHandler:

    @staticmethod
    @guard_handler()
    async def show(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        db: Database = ctx.bot_data["db"]
        uid = update.effective_user.id
        p = await db.get_player(uid)
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
        p = await db.get_player(uid)
        if not p:
            await q.edit_message_text("Сначала /start")
            return
        text, kb = await _build(db, uid, p)
        await q.edit_message_text(text, parse_mode="Markdown", reply_markup=kb)

    @staticmethod
    @guard_handler()
    async def upgrade(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        q = update.callback_query
        await q.answer()
        db: Database = ctx.bot_data["db"]
        uid = q.from_user.id
        slot = q.data.split(":")[1]

        p = await db.get_player(uid)
        eq = await db.get_equipped(uid)
        item_id = eq.get(slot)

        if not item_id or item_id not in ITEMS:
            await q.answer("В этом слоте нет предмета!", show_alert=True)
            return

        forges = await db.get_forges(uid)
        cur_lvl = forges.get(slot, 0)

        if cur_lvl >= MAX_FORGE:
            await q.answer("Максимальный уровень улучшения!", show_alert=True)
            return

        next_lvl = cur_lvl + 1
        cost = FORGE_COST[next_lvl]

        if p["gold"] < cost:
            await q.answer(f"Нужно {cost}💰, у тебя {p['gold']}", show_alert=True)
            return

        await db.update_player(uid, gold=p["gold"] - cost)
        await db.set_forge(uid, slot, next_lvl)

        item = ITEMS[item_id]
        bonus_pct = int(FORGE_BONUS[next_lvl] * 100)
        stars = "⭐" * next_lvl

        await q.answer(f"✅ {item['name']} улучшен до +{next_lvl}!", show_alert=True)
        p_new = await db.get_player(uid)
        text, kb = await _build(db, uid, p_new)
        await q.edit_message_text(text, parse_mode="Markdown", reply_markup=kb)


async def _build(db: Database, uid: int, p: dict) -> tuple[str, InlineKeyboardMarkup]:
    eq = await db.get_equipped(uid)
    forges = await db.get_forges(uid)
    lvl = p["level"]

    lines = [
        f"🔨 *КУЗНИЦА*\n"
        f"💰 У тебя: *{p['gold']}* золота\n\n"
        f"Улучшай надетые предметы до +{MAX_FORGE}:\n"
    ]
    buttons = []

    for slot, slot_name in SLOTS.items():
        item_id = eq.get(slot)
        forge_lvl = forges.get(slot, 0)
        if not item_id or item_id not in ITEMS:
            continue
        item = ITEMS[item_id]
        stars = "⭐" * forge_lvl if forge_lvl else "—"
        next_lvl = forge_lvl + 1
        if forge_lvl < MAX_FORGE:
            cost = FORGE_COST[next_lvl]
            bonus = int(FORGE_BONUS[next_lvl] * 100)
            btn_label = f"🔨 {item['name']} {stars} → +{next_lvl} ({cost}💰, +{bonus}%)"
            lines.append(f"• {slot_name}: *{item['name']}* {stars} (+{int(FORGE_BONUS[forge_lvl]*100) if forge_lvl else 0}% к статам)")
            buttons.append([InlineKeyboardButton(btn_label, callback_data=f"forge_up:{slot}")])
        else:
            lines.append(f"• {slot_name}: *{item['name']}* {stars} ✅ МАКС")

    if not buttons:
        lines.append("\n_Надень экипировку чтобы улучшать её_")

    buttons.append([InlineKeyboardButton("◀️ Экипировка", callback_data="inventory")])
    return "\n".join(lines), InlineKeyboardMarkup(buttons)
