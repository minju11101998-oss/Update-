"""Магазин экипировки — /equipment"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database import Database
from gamedata import SLOTS, ITEMS, items_by_slot_all, get_item_stats
from safety import guard_handler

# Иконки статов
STAT_ICONS = {
    "hp":          "❤️",
    "atk":         "🗡",
    "def":         "🔰",
    "crit_chance": "🥊",
    "crit_power":  "💥",
    "foresight":   "👁",
    "dodge":       "⚡️",
    "counter":     "🤺",
    "accuracy":    "🎯",
}


def _stats_full(item: dict, lvl: int) -> str:
    """Подробный блок статов с учётом уровня игрока"""
    scaled = get_item_stats(item, lvl)
    if not scaled:
        return "_Нет бонусов_"
    lines = []
    for k, v in scaled.items():
        icon = STAT_ICONS.get(k, k)
        sign = "+" if v >= 0 else ""
        lines.append(f"{icon} {sign}{round(v, 1)}")
    return "  ".join(lines)


def _equip_tag(item: dict, lvl: int) -> str:
    """Короткий тег ключевых статов рядом с названием предмета"""
    scaled = get_item_stats(item, lvl)
    parts = []
    for k in ("hp", "def", "atk"):
        v = scaled.get(k, 0)
        if v:
            parts.append(f"{STAT_ICONS[k]}+{int(v)}")
    return f" `[{' '.join(parts)}]`" if parts else ""


class EquipmentHandler:

    @staticmethod
    @guard_handler()
    async def show_shop(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        db: Database = ctx.bot_data["db"]
        uid = update.effective_user.id
        player = await db.get_player(uid)
        if not player:
            await update.message.reply_text("Сначала /start")
            return
        text, kb = _slot_menu(player)
        await update.message.reply_text(text, parse_mode="Markdown", reply_markup=kb)

    @staticmethod
    @guard_handler()
    async def show_inventory(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        db: Database = ctx.bot_data["db"]
        uid = query.from_user.id
        player = await db.get_player(uid)
        if not player:
            await query.edit_message_text("Сначала /start")
            return
        text, kb = _slot_menu(player)
        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=kb)

    @staticmethod
    @guard_handler()
    async def show_slot(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        db: Database = ctx.bot_data["db"]
        uid = query.from_user.id
        slot = query.data.split(":")[1]

        player   = await db.get_player(uid)
        inventory = await db.get_inventory(uid)
        equipped  = await db.get_equipped(uid)
        lvl = player["level"]

        items = items_by_slot_all(slot)
        lines = [f"*{SLOTS[slot]}* — предметы:\n"]
        buttons = []

        for iid, item in items:
            owned      = iid in inventory
            is_eq      = equipped.get(slot) == iid
            locked     = item["req_level"] > lvl

            if is_eq:
                status = "✅ *НАДЕТО*"
            elif owned:
                status = "📦 Есть"
            elif locked:
                status = f"🔒 Ур.{item['req_level']}"
            else:
                status = f"💰 {item['price']}"

            stats_line = _stats_full(item, lvl)
            lines.append(
                f"{'🔒 ' if locked else ''}"
                f"*{item['name']}*  {status}\n"
                f"_{item['desc']}_\n"
                f"{stats_line}\n"
            )

            row = []
            if is_eq:
                row.append(InlineKeyboardButton("❌ Снять", callback_data=f"unequip:{slot}"))
            elif owned and not locked:
                row.append(InlineKeyboardButton("✅ Надеть", callback_data=f"equip:{iid}"))
            elif not owned and not locked:
                row.append(InlineKeyboardButton(
                    f"💰 Купить ({item['price']})", callback_data=f"buy:{iid}"))
            if row:
                buttons.append(row)

        buttons.append([InlineKeyboardButton("◀️ Назад", callback_data="inventory")])

        await query.edit_message_text(
            "\n".join(lines),
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(buttons)
        )

    @staticmethod
    @guard_handler()
    async def buy_item(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        db: Database = ctx.bot_data["db"]
        uid = query.from_user.id
        item_id = query.data.split(":")[1]

        if item_id not in ITEMS:
            await query.answer("Предмет не найден.", show_alert=True)
            return

        item   = ITEMS[item_id]
        player = await db.get_player(uid)

        if player["level"] < item["req_level"]:
            await query.answer(f"Нужен уровень {item['req_level']}!", show_alert=True)
            return
        if await db.has_item(uid, item_id):
            await query.answer("Уже куплено!", show_alert=True)
            return
        if player["gold"] < item["price"]:
            await query.answer(f"Нужно {item['price']}💰, у тебя {player['gold']}", show_alert=True)
            return

        await db.update_player(uid, gold=player["gold"] - item["price"])
        await db.add_to_inventory(uid, item_id)
        await query.answer(f"✅ Куплено: {item['name']}!", show_alert=True)

        # Обновить экран слота
        query.data = f"slot:{item['slot']}"
        await EquipmentHandler.show_slot(update, ctx)

    @staticmethod
    @guard_handler()
    async def equip_item(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        db: Database = ctx.bot_data["db"]
        uid = query.from_user.id
        item_id = query.data.split(":")[1]

        if item_id not in ITEMS:
            await query.answer("Предмет не найден.", show_alert=True)
            return
        if not await db.has_item(uid, item_id):
            await query.answer("Нет в инвентаре!", show_alert=True)
            return

        item = ITEMS[item_id]
        await db.equip_item(uid, item["slot"], item_id)
        await query.answer(f"✅ Надето: {item['name']}")

        query.data = f"slot:{item['slot']}"
        await EquipmentHandler.show_slot(update, ctx)

    @staticmethod
    @guard_handler()
    async def unequip_item(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        db: Database = ctx.bot_data["db"]
        uid = query.from_user.id
        slot = query.data.split(":")[1]

        await db.unequip_item(uid, slot)
        await query.answer(f"❌ Снято с {SLOTS.get(slot, slot)}")

        query.data = f"slot:{slot}"
        await EquipmentHandler.show_slot(update, ctx)


def _slot_menu(player: dict) -> tuple[str, InlineKeyboardMarkup]:
    text = (
        f"🛒 *МАГАЗИН ЭКИПИРОВКИ*\n"
        f"Ур. {player['level']} | 💰 {player['gold']} золота\n\n"
        f"Выбери слот:"
    )
    buttons = [
        [InlineKeyboardButton(name, callback_data=f"slot:{slot}")]
        for slot, name in SLOTS.items()
    ]
    buttons.append([InlineKeyboardButton("👤 Профиль", callback_data="profile")])
    return text, InlineKeyboardMarkup(buttons)
