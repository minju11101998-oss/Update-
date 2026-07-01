"""Зачарования экипировки — /enchant"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database import Database
from gamedata import ENCHANTMENTS, SLOTS, ITEMS
from safety import guard_handler


class EnchantHandler:

    @staticmethod
    @guard_handler()
    async def show(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        db: Database = ctx.bot_data["db"]
        uid = update.effective_user.id
        p   = await db.get_player(uid)
        if not p:
            await update.message.reply_text("Сначала /start"); return
        text, kb = await _build_menu(db, uid, p)
        await update.message.reply_text(text, parse_mode="Markdown", reply_markup=kb)

    @staticmethod
    @guard_handler()
    async def show_cb(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        q = update.callback_query; await q.answer()
        db: Database = ctx.bot_data["db"]
        uid = q.from_user.id
        p   = await db.get_player(uid)
        if not p:
            await q.edit_message_text("Сначала /start"); return
        text, kb = await _build_menu(db, uid, p)
        await q.edit_message_text(text, parse_mode="Markdown", reply_markup=kb)

    @staticmethod
    @guard_handler()
    async def choose_slot(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        q    = update.callback_query; await q.answer()
        db: Database = ctx.bot_data["db"]
        uid  = q.from_user.id
        slot = q.data.split(":")[1]
        p    = await db.get_player(uid)
        eq   = await db.get_equipped(uid)
        ench = await db.get_enchantments(uid)

        item_id = eq.get(slot)
        if not item_id:
            await q.answer("В этом слоте нет предмета!", show_alert=True); return

        item        = ITEMS[item_id]
        current_eid = ench.get(slot)
        current_e   = ENCHANTMENTS.get(current_eid)

        lines = [
            f"✨ *Зачарование — {SLOTS[slot]}*\n"
            f"Предмет: *{item['name']}*\n"
            f"Текущее: *{current_e['name'] if current_e else 'нет'}*\n\n"
            f"Выбери зачарование:"
        ]
        buttons = []
        for eid, ench_data in ENCHANTMENTS.items():
            mark = "✅ " if eid == current_eid else ""
            stat_txt = " | ".join(
                f"+{v} {k}" for k, v in ench_data["stats"].items())
            buttons.append([InlineKeyboardButton(
                f"{mark}{ench_data['name']} ({ench_data['price']}💰) — {stat_txt}",
                callback_data=f"enchant_apply:{slot}:{eid}"
            )])
        buttons.append([InlineKeyboardButton("◀️ Назад", callback_data="enchant_menu")])

        await q.edit_message_text(
            "\n".join(lines), parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(buttons)
        )

    @staticmethod
    @guard_handler()
    async def apply(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        q    = update.callback_query; await q.answer()
        db: Database = ctx.bot_data["db"]
        uid  = q.from_user.id
        _, slot, eid = q.data.split(":")

        p    = await db.get_player(uid)
        ench = ENCHANTMENTS.get(eid)
        if not ench:
            await q.answer("Зачарование не найдено!", show_alert=True); return

        if p["gold"] < ench["price"]:
            await q.answer(
                f"Нужно {ench['price']}💰, у тебя {p['gold']}", show_alert=True)
            return

        await db.update_player(uid, gold=p["gold"] - ench["price"])
        await db.set_enchantment(uid, slot, eid)

        await q.answer(f"✅ Применено: {ench['name']}!", show_alert=True)

        p_new = await db.get_player(uid)
        text, kb = await _build_menu(db, uid, p_new)
        await q.edit_message_text(text, parse_mode="Markdown", reply_markup=kb)


async def _build_menu(db: Database, uid: int, p: dict) -> tuple[str, InlineKeyboardMarkup]:
    eq   = await db.get_equipped(uid)
    ench = await db.get_enchantments(uid)

    lines = [
        f"✨ *ЗАЧАРОВАНИЯ*\n"
        f"💰 У тебя: *{p['gold']}* золота\n\n"
        f"Выбери слот для зачарования:"
    ]
    buttons = []
    for slot, slot_name in SLOTS.items():
        item_id  = eq.get(slot)
        ench_id  = ench.get(slot)
        if item_id:
            item_name = ITEMS[item_id]["name"]
            ench_name = ENCHANTMENTS[ench_id]["name"] if ench_id else "нет"
            label = f"{slot_name}: {item_name} [{ench_name}]"
            buttons.append([InlineKeyboardButton(label, callback_data=f"enchant_slot:{slot}")])
        else:
            lines.append(f"• {slot_name}: _пусто_")

    buttons.append([InlineKeyboardButton("◀️ Экипировка", callback_data="inventory")])
    return "\n".join(lines), InlineKeyboardMarkup(buttons)
