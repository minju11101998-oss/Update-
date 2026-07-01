"""
Магазин расходников и зелий прокачки — /shop
"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database import Database
from config import CONSUMABLES
from safety import guard_handler

POTIONS = {
    "exp_potion": {
        "name": "📚 Зелье опыта",
        "desc": "+300 опыта немедленно",
        "price": 150,
        "emoji": "📚",
    },
    "gold_potion": {
        "name": "🍀 Зелье удачи",
        "desc": "+25% золота с боёв (5 боёв)",
        "price": 120,
        "emoji": "🍀",
    },
    "shield_scroll": {
        "name": "🛡️ Щит-свиток",
        "desc": "В бою: блокирует 1 удар полностью",
        "price": 100,
        "emoji": "🛡️",
    },
    "speed_rune": {
        "name": "⚡ Руна скорости",
        "desc": "В бою: гарантированный уворот в раунде",
        "price": 80,
        "emoji": "⚡",
    },
    "grenade": {
        "name": "💣 Граната",
        "desc": "В бою: 50-80 фиксированного урона",
        "price": 90,
        "emoji": "💣",
    },
    "mmr_shield": {
        "name": "🏅 Страховка MMR",
        "desc": "При поражении MMR не теряется (1 бой)",
        "price": 60,
        "emoji": "🏅",
    },
}

SHOP_ITEMS = {**CONSUMABLES, **POTIONS}


class ShopHandler:

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
    async def buy(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        q = update.callback_query
        await q.answer()
        db: Database = ctx.bot_data["db"]
        uid = q.from_user.id
        item_id = q.data.split(":")[1]

        item = SHOP_ITEMS.get(item_id)
        if not item:
            await q.answer("Товар не найден!", show_alert=True)
            return

        p = await db.get_player(uid)
        if p["gold"] < item["price"]:
            await q.answer(
                f"Нужно {item['price']}💰, у тебя {p['gold']}", show_alert=True)
            return

        await db.update_player(uid, gold=p["gold"] - item["price"])

        # Особые эффекты
        if item_id == "exp_potion":
            from config import EXP_BASE, EXP_SCALE, MAX_LEVEL
            new_exp = p["exp"] + 300
            needed = int(EXP_BASE * (p["level"] ** EXP_SCALE))
            new_lvl = p["level"]
            leveled = False
            if new_exp >= needed and new_lvl < MAX_LEVEL:
                new_exp -= needed
                new_lvl += 1
                leveled = True
            await db.update_player(uid, exp=new_exp, level=new_lvl)
            msg = f"📚 +300 опыта!" + ("\n🎉 Новый уровень!" if leveled else "")
            await q.answer(msg, show_alert=True)
        else:
            # Добавить в инвентарь расходников
            await db.add_consumable(uid, item_id)
            await q.answer(f"✅ Куплено: {item['name']}!", show_alert=True)

        p_new = await db.get_player(uid)
        text, kb = await _build(db, uid, p_new)
        await q.edit_message_text(text, parse_mode="Markdown", reply_markup=kb)

    @staticmethod
    @guard_handler()
    async def my_items(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        q = update.callback_query
        await q.answer()
        db: Database = ctx.bot_data["db"]
        uid = q.from_user.id
        cons = await db.get_consumables(uid)

        if not cons:
            text = "🎒 *Мои расходники*\n\n_Пусто. Купи что-нибудь в /shop_"
        else:
            lines = ["🎒 *Мои расходники:*\n"]
            for item_id, amount in cons.items():
                item = SHOP_ITEMS.get(item_id, {})
                name = item.get("name", item_id)
                lines.append(f"• {name} × *{amount}*")
            text = "\n".join(lines)

        kb = InlineKeyboardMarkup([[
            InlineKeyboardButton("🛒 В магазин", callback_data="shop_menu"),
            InlineKeyboardButton("◀️ Профиль",   callback_data="profile"),
        ]])
        await q.edit_message_text(text, parse_mode="Markdown", reply_markup=kb)


async def _build(db: Database, uid: int, p: dict) -> tuple[str, InlineKeyboardMarkup]:
    cons = await db.get_consumables(uid)
    lines = [
        f"🛒 *МАГАЗИН*\n"
        f"💰 У тебя: *{p['gold']}* золота\n\n"
    ]
    buttons = []

    for item_id, item in SHOP_ITEMS.items():
        owned = cons.get(item_id, 0)
        owned_txt = f" (×{owned})" if owned else ""
        lines.append(
            f"*{item['name']}*{owned_txt}\n"
            f"_{item['desc']}_\n"
            f"💰 {item['price']} золота"
        )
        buttons.append([InlineKeyboardButton(
            f"💰 Купить {item['name']} ({item['price']})",
            callback_data=f"shop_buy:{item_id}"
        )])

    buttons.append([InlineKeyboardButton("🎒 Мои расходники", callback_data="shop_items")])
    buttons.append([InlineKeyboardButton("◀️ Профиль", callback_data="profile")])
    return "\n\n".join(lines), InlineKeyboardMarkup(buttons)
