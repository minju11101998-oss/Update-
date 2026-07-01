"""
Система крафта — /craft
Рецепты: комбинируй предметы + материалы → новый предмет
Материалы дропают из боёв (отдельная таблица)
"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database import Database
from gamedata import ITEMS
from safety import guard_handler

# ─── МАТЕРИАЛЫ ────────────────────────────────────────────────────────────────
# Дропают из боёв, используются в рецептах

MATERIALS = {
    "iron_ore": {
        "name": "⛏️ Железная руда",
        "desc": "Добывается из големов и стражей",
        "rarity": "common",
    },
    "shadow_dust": {
        "name": "🌑 Пыль теней",
        "desc": "Остаётся от теневых существ",
        "rarity": "uncommon",
    },
    "dragon_scale_frag": {
        "name": "🐉 Осколок чешуи",
        "desc": "Фрагмент брони дракона",
        "rarity": "rare",
    },
    "void_crystal": {
        "name": "🌀 Кристалл пустоты",
        "desc": "Сгусток магии пустоты",
        "rarity": "epic",
    },
    "dragon_flame": {
        "name": "🔥 Пламя дракона",
        "desc": "Горит вечно. Редчайший материал",
        "rarity": "legendary",
    },
    "bone_fragment": {
        "name": "🦴 Фрагмент кости",
        "desc": "Остатки поверженных врагов",
        "rarity": "common",
    },
    "mana_crystal": {
        "name": "💎 Кристалл маны",
        "desc": "Концентрированная магическая энергия",
        "rarity": "uncommon",
    },
    "steel_ingot": {
        "name": "🔩 Стальной слиток",
        "desc": "Переплавленная сталь высшего качества",
        "rarity": "uncommon",
    },
    "enchanted_thread": {
        "name": "🧵 Зачарованная нить",
        "desc": "Нить, пропитанная магией",
        "rarity": "rare",
    },
    "titan_ore": {
        "name": "⚙️ Руда титана",
        "desc": "Тяжелейший металл известный миру",
        "rarity": "epic",
    },

    # ── Уникальные материалы для эксклюзивных крафтовых вещей ────────────────
    "beast_fang": {
        "name": "🦴 Клык зверя",
        "desc": "Выпадает с диких существ Арены",
        "rarity": "common",
    },
    "victory_token": {
        "name": "🏆 Жетон победы",
        "desc": "Дают только за честную победу в бою",
        "rarity": "uncommon",
    },
    "wolf_fur": {
        "name": "🐺 Шерсть волка",
        "desc": "Тёплая и пропитанная силой дикой природы",
        "rarity": "uncommon",
    },
    "executioner_cloth": {
        "name": "🩸 Ткань палача",
        "desc": "Пропитана кровью тысяч поединков",
        "rarity": "rare",
    },
    "storm_essence": {
        "name": "⚡ Эссенция бури",
        "desc": "Сгусток чистой энергии шторма",
        "rarity": "rare",
    },
    "path_dust": {
        "name": "🌪️ Пыль странствий",
        "desc": "Собирается на подошвах путников Арены",
        "rarity": "rare",
    },
    "abyss_shard": {
        "name": "🌌 Осколок Бездны", 
        "desc": "Частица уничтоженного мира",
        "rarity": "epic",
    },
    "eternal_ember": {
        "name": "🔥 Вечный уголёк",
        "desc": "Никогда не остывает",
        "rarity": "epic",
    },
    "kings_seal": {
        "name": "👑 Печать короля",
        "desc": "Принадлежала правителю до Катастрофы",
        "rarity": "legendary",
    },
    "world_fragment": {
        "name": "🌍 Фрагмент мира",
        "desc": "Кусочек реальности до распада",
        "rarity": "legendary",
    },
}

# ─── ШАНС ДРОПА МАТЕРИАЛОВ ────────────────────────────────────────────────────
# drop_chance — базовый % после любого боя (победа/поражение)

MATERIAL_DROP = {
    "iron_ore":          {"drop_chance": 45, "min_level": 1},
    "bone_fragment":     {"drop_chance": 40, "min_level": 1},
    "shadow_dust":       {"drop_chance": 25, "min_level": 5},
    "mana_crystal":      {"drop_chance": 20, "min_level": 7},
    "steel_ingot":       {"drop_chance": 18, "min_level": 8},
    "enchanted_thread":  {"drop_chance": 12, "min_level": 10},
    "dragon_scale_frag": {"drop_chance": 8,  "min_level": 15},
    "void_crystal":      {"drop_chance": 5,  "min_level": 18},
    "titan_ore":         {"drop_chance": 4,  "min_level": 20},
    "dragon_flame":      {"drop_chance": 1,  "min_level": 25},

    # ── Уникальные материалы для эксклюзивных вещей ──────────────────────────
    "beast_fang":        {"drop_chance": 30, "min_level": 1},
    "victory_token":     {"drop_chance": 0,  "min_level": 1},   # выдаётся только за победу, не рандомом
    "wolf_fur":          {"drop_chance": 22, "min_level": 8},
    "executioner_cloth": {"drop_chance": 14, "min_level": 13},
    "storm_essence":     {"drop_chance": 12, "min_level": 18},
    "path_dust":         {"drop_chance": 10, "min_level": 23},
    "abyss_shard":       {"drop_chance": 6,  "min_level": 28},
    "eternal_ember":     {"drop_chance": 5,  "min_level": 33},
    "kings_seal":        {"drop_chance": 2,  "min_level": 38},
    "world_fragment":    {"drop_chance": 1,  "min_level": 43},
}

# ─── РЕЦЕПТЫ КРАФТА ───────────────────────────────────────────────────────────
# result       : item_id из ITEMS — что получаем
# materials    : {material_id: количество}
# base_items   : {item_id: количество} — предметы из инвентаря (расходуются!)
# gold_cost    : стоимость крафта в золоте
# req_level    : минимальный уровень игрока
# result_count : сколько штук получаем (по умолч. 1)

RECIPES = {
    # ── ОРУЖИЕ ──────────────────────────────────────────────────────────────
    "r_steel_sword": {
        "name": "Крафт Стального меча",
        "result": "steel_sword",
        "materials": {"iron_ore": 3, "steel_ingot": 2},
        "base_items": {},
        "gold_cost": 80,
        "req_level": 4,
    },
    "r_shadow_blade": {
        "name": "Крафт Клинка тени",
        "result": "shadow_blade",
        "materials": {"shadow_dust": 4, "steel_ingot": 3, "void_crystal": 1},
        "base_items": {"steel_sword": 1},
        "gold_cost": 200,
        "req_level": 9,
    },
    "r_void_dagger": {
        "name": "Крафт Кинжала пустоты",
        "result": "void_dagger",
        "materials": {"void_crystal": 3, "shadow_dust": 5, "mana_crystal": 2},
        "base_items": {"shadow_blade": 1},
        "gold_cost": 350,
        "req_level": 14,
    },
    "r_dragon_sword": {
        "name": "Крафт Меча дракона",
        "result": "dragon_sword",
        "materials": {"dragon_flame": 2, "dragon_scale_frag": 5, "void_crystal": 4},
        "base_items": {"void_dagger": 1},
        "gold_cost": 800,
        "req_level": 19,
    },
    "r_arcane_staff": {
        "name": "Крафт Магического посоха",
        "result": "arcane_staff",
        "materials": {"mana_crystal": 4, "enchanted_thread": 2},
        "base_items": {},
        "gold_cost": 150,
        "req_level": 6,
    },
    "r_titan_hammer": {
        "name": "Крафт Молота титана",
        "result": "titan_hammer",
        "materials": {"titan_ore": 5, "steel_ingot": 4, "iron_ore": 6},
        "base_items": {"war_axe": 1},
        "gold_cost": 500,
        "req_level": 17,
    },

    # ── БРОНЯ ───────────────────────────────────────────────────────────────
    "r_chain_mail": {
        "name": "Крафт Кольчуги",
        "result": "chain_mail",
        "materials": {"iron_ore": 5, "steel_ingot": 2},
        "base_items": {"leather_armor": 1},
        "gold_cost": 60,
        "req_level": 4,
    },
    "r_plate_armor": {
        "name": "Крафт Латных доспехов",
        "result": "plate_armor",
        "materials": {"steel_ingot": 5, "iron_ore": 4},
        "base_items": {"chain_mail": 1},
        "gold_cost": 180,
        "req_level": 9,
    },
    "r_shadow_cloak": {
        "name": "Крафт Плаща теней",
        "result": "shadow_cloak",
        "materials": {"shadow_dust": 6, "enchanted_thread": 3},
        "base_items": {},
        "gold_cost": 220,
        "req_level": 11,
    },
    "r_dragon_scale": {
        "name": "Крафт Чешуи дракона",
        "result": "dragon_scale",
        "materials": {"dragon_scale_frag": 8, "dragon_flame": 1, "titan_ore": 3},
        "base_items": {"plate_armor": 1},
        "gold_cost": 700,
        "req_level": 19,
    },
    "r_void_shroud": {
        "name": "Крафт Покрова пустоты",
        "result": "void_shroud",
        "materials": {"void_crystal": 5, "shadow_dust": 8, "enchanted_thread": 4},
        "base_items": {"shadow_cloak": 1},
        "gold_cost": 900,
        "req_level": 24,
    },

    # ── ШЛЕМ ────────────────────────────────────────────────────────────────
    "r_iron_helm": {
        "name": "Крафт Железного шлема",
        "result": "iron_helm",
        "materials": {"iron_ore": 4, "bone_fragment": 2},
        "base_items": {},
        "gold_cost": 50,
        "req_level": 4,
    },
    "r_war_crown": {
        "name": "Крафт Боевой короны",
        "result": "war_crown",
        "materials": {"steel_ingot": 4, "mana_crystal": 3, "enchanted_thread": 2},
        "base_items": {"iron_helm": 1},
        "gold_cost": 300,
        "req_level": 14,
    },
    "r_titan_helm": {
        "name": "Крафт Шлема титана",
        "result": "titan_helm",
        "materials": {"titan_ore": 4, "steel_ingot": 3, "void_crystal": 2},
        "base_items": {"war_crown": 1},
        "gold_cost": 600,
        "req_level": 21,
    },

    # ── САПОГИ ──────────────────────────────────────────────────────────────
    "r_iron_boots": {
        "name": "Крафт Железных сапог",
        "result": "iron_boots",
        "materials": {"iron_ore": 3, "bone_fragment": 3},
        "base_items": {},
        "gold_cost": 55,
        "req_level": 5,
    },
    "r_phantom_boots": {
        "name": "Крафт Сапог призрака",
        "result": "phantom_boots",
        "materials": {"shadow_dust": 5, "enchanted_thread": 3, "mana_crystal": 2},
        "base_items": {},
        "gold_cost": 280,
        "req_level": 13,
    },
    "r_void_steps": {
        "name": "Крафт Шагов пустоты",
        "result": "void_steps",
        "materials": {"void_crystal": 3, "shadow_dust": 6},
        "base_items": {"phantom_boots": 1},
        "gold_cost": 450,
        "req_level": 19,
    },

    # ── КОЛЬЦО ──────────────────────────────────────────────────────────────
    "r_berserker_ring": {
        "name": "Крафт Кольца берсерка",
        "result": "berserker_ring",
        "materials": {"iron_ore": 2, "bone_fragment": 4, "dragon_scale_frag": 1},
        "base_items": {"iron_ring": 1},
        "gold_cost": 120,
        "req_level": 7,
    },
    "r_oracle_ring": {
        "name": "Крафт Кольца оракула",
        "result": "oracle_ring",
        "materials": {"mana_crystal": 4, "enchanted_thread": 2},
        "base_items": {},
        "gold_cost": 140,
        "req_level": 9,
    },
    "r_titan_ring": {
        "name": "Крафт Кольца титана",
        "result": "titan_ring",
        "materials": {"titan_ore": 3, "steel_ingot": 2, "void_crystal": 1},
        "base_items": {},
        "gold_cost": 300,
        "req_level": 17,
    },

    # ── АМУЛЕТ ──────────────────────────────────────────────────────────────
    "r_war_amulet": {
        "name": "Крафт Амулета войны",
        "result": "war_amulet",
        "materials": {"iron_ore": 3, "bone_fragment": 3, "mana_crystal": 1},
        "base_items": {},
        "gold_cost": 100,
        "req_level": 8,
    },
    "r_shadow_amulet": {
        "name": "Крафт Амулета теней",
        "result": "shadow_amulet",
        "materials": {"shadow_dust": 6, "void_crystal": 2, "enchanted_thread": 2},
        "base_items": {},
        "gold_cost": 300,
        "req_level": 14,
    },
    "r_dragon_heart": {
        "name": "Крафт Сердца дракона",
        "result": "dragon_heart",
        "materials": {"dragon_flame": 3, "dragon_scale_frag": 6, "void_crystal": 5},
        "base_items": {},
        "gold_cost": 1200,
        "req_level": 24,
    },

    # ── ЭКСКЛЮЗИВНЫЕ КРАФТОВЫЕ ПРЕДМЕТЫ (только через крафт!) ────────────────
    "r_novice_fang": {
        "name": "🦷 Клык новичка (ЭКСКЛЮЗИВ)",
        "result": "novice_fang",
        "materials": {"beast_fang": 5, "bone_fragment": 3},
        "base_items": {},
        "gold_cost": 50,
        "req_level": 1,
    },
    "r_first_blood_gauntlet": {
        "name": "🥊 Перчатка Первой крови (ЭКСКЛЮЗИВ)",
        "result": "first_blood_gauntlet",
        "materials": {"victory_token": 3, "iron_ore": 4},
        "base_items": {},
        "gold_cost": 120,
        "req_level": 5,
    },
    "r_wolf_heart": {
        "name": "🐺 Сердце волка (ЭКСКЛЮЗИВ)",
        "result": "wolf_heart",
        "materials": {"wolf_fur": 6, "beast_fang": 4, "mana_crystal": 2},
        "base_items": {},
        "gold_cost": 220,
        "req_level": 10,
    },
    "r_executioner_mask": {
        "name": "💀 Маска палача (ЭКСКЛЮЗИВ)",
        "result": "executioner_mask",
        "materials": {"executioner_cloth": 5, "steel_ingot": 4, "victory_token": 3},
        "base_items": {},
        "gold_cost": 380,
        "req_level": 15,
    },
    "r_storm_cuirass": {
        "name": "⛈️ Кираса бури (ЭКСКЛЮЗИВ)",
        "result": "storm_cuirass",
        "materials": {"storm_essence": 6, "steel_ingot": 5, "mana_crystal": 4},
        "base_items": {"plate_armor": 1},
        "gold_cost": 550,
        "req_level": 20,
    },
    "r_pathdevourer_boots": {
        "name": "🌪️ Сапоги Пожирателя Пути (ЭКСКЛЮЗИВ)",
        "result": "pathdevourer_boots",
        "materials": {"path_dust": 6, "shadow_dust": 6, "enchanted_thread": 3},
        "base_items": {"phantom_boots": 1},
        "gold_cost": 700,
        "req_level": 25,
    },
    "r_abyss_blade": {
        "name": "🌌 Клинок Бездны (ЭКСКЛЮЗИВ)",
        "result": "abyss_blade",
        "materials": {"abyss_shard": 5, "void_crystal": 4, "dragon_scale_frag": 3},
        "base_items": {"void_dagger": 1},
        "gold_cost": 1000,
        "req_level": 30,
    },
    "r_eternal_flame_ring": {
        "name": "🔥 Кольцо Вечного Пламени (ЭКСКЛЮЗИВ)",
        "result": "eternal_flame_ring",
        "materials": {"eternal_ember": 5, "dragon_flame": 1, "void_crystal": 3},
        "base_items": {},
        "gold_cost": 1300,
        "req_level": 35,
    },
    "r_fallen_king_crown": {
        "name": "👑 Корона Падшего Короля (ЭКСКЛЮЗИВ)",
        "result": "fallen_king_crown",
        "materials": {"kings_seal": 4, "titan_ore": 6, "dragon_scale_frag": 4},
        "base_items": {"war_crown": 1},
        "gold_cost": 1800,
        "req_level": 40,
    },
    "r_worldmaker_amulet": {
        "name": "🌍 Амулет Творца Миров (ЭКСКЛЮЗИВ)",
        "result": "worldmaker_amulet",
        "materials": {
            "world_fragment": 3, "dragon_flame": 3,
            "kings_seal": 2, "abyss_shard": 4, "void_crystal": 5,
        },
        "base_items": {"dragon_heart": 1},
        "gold_cost": 3000,
        "req_level": 45,
    },

    # ── СПЕЦ. РЕЦЕПТЫ ────────────────────────────────────────────────────────
    "r_upgrade_kit": {
        "name": "Набор улучшения (кузница +1 бесплатно)",
        "result": "upgrade_kit",
        "materials": {"steel_ingot": 3, "mana_crystal": 2, "iron_ore": 5},
        "base_items": {},
        "gold_cost": 200,
        "req_level": 10,
        "special": "forge_free",
    },
}

# Специальные предметы крафта (не из ITEMS)
CRAFT_SPECIALS = {
    "upgrade_kit": {
        "name": "🔧 Набор улучшения",
        "desc": "Даёт один бесплатный уровень кузницы для любого предмета",
    },
}


# ─── ХЕНДЛЕР ──────────────────────────────────────────────────────────────────

class CraftHandler:

    @staticmethod
    @guard_handler()
    async def show(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        db: Database = ctx.bot_data["db"]
        uid = update.effective_user.id
        p = await db.get_player(uid)
        if not p:
            await update.message.reply_text("Сначала /start")
            return
        text, kb = await _build_menu(db, uid, p)
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
        text, kb = await _build_menu(db, uid, p)
        await q.edit_message_text(text, parse_mode="Markdown", reply_markup=kb)

    @staticmethod
    @guard_handler()
    async def view_recipe(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        q = update.callback_query
        await q.answer()
        db: Database = ctx.bot_data["db"]
        uid = q.from_user.id
        recipe_id = q.data.split(":")[1]

        recipe = RECIPES.get(recipe_id)
        if not recipe:
            await q.answer("Рецепт не найден!", show_alert=True)
            return

        p = await db.get_player(uid)
        mats = await db.get_materials(uid)
        inv = await db.get_inventory(uid)

        can_craft, missing = _check_recipe(recipe, mats, inv, p)

        # Результат
        result_id = recipe["result"]
        if result_id in ITEMS:
            result_name = ITEMS[result_id]["name"]
            result_desc = ITEMS[result_id]["desc"]
        else:
            spec = CRAFT_SPECIALS.get(result_id, {})
            result_name = spec.get("name", result_id)
            result_desc = spec.get("desc", "")

        lines = [
            f"🔨 *{recipe['name']}*\n",
            f"📦 *Результат:* {result_name}",
            f"_{result_desc}_\n",
            f"*Требуется:*",
        ]

        # Материалы
        for mat_id, need in recipe["materials"].items():
            have = mats.get(mat_id, 0)
            mat = MATERIALS.get(mat_id, {})
            icon = "✅" if have >= need else "❌"
            lines.append(f"{icon} {mat.get('name', mat_id)}: {have}/{need}")

        # Предметы из инвентаря
        for item_id, need in recipe.get("base_items", {}).items():
            have = inv.count(item_id) if isinstance(inv, list) else (1 if item_id in inv else 0)
            item = ITEMS.get(item_id, {})
            icon = "✅" if have >= need else "❌"
            lines.append(f"{icon} {item.get('name', item_id)} (из инвентаря)")

        # Золото
        gold_ok = p["gold"] >= recipe["gold_cost"]
        icon = "✅" if gold_ok else "❌"
        lines.append(f"{icon} 💰 Золото: {p['gold']}/{recipe['gold_cost']}")

        # Уровень
        if p["level"] < recipe["req_level"]:
            lines.append(f"❌ 📊 Уровень: {p['level']}/{recipe['req_level']}")
        else:
            lines.append(f"✅ 📊 Уровень: {p['level']}/{recipe['req_level']}")

        if missing:
            lines.append(f"\n⚠️ *Не хватает:*\n" + "\n".join(missing))

        buttons = []
        if can_craft:
            buttons.append([InlineKeyboardButton(
                f"🔨 Скрафтить ({recipe['gold_cost']}💰)",
                callback_data=f"craft_do:{recipe_id}"
            )])
        buttons.append([InlineKeyboardButton("◀️ Все рецепты", callback_data="craft_menu")])

        await q.edit_message_text(
            "\n".join(lines),
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(buttons)
        )

    @staticmethod
    @guard_handler()
    async def do_craft(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        q = update.callback_query
        await q.answer()
        db: Database = ctx.bot_data["db"]
        uid = q.from_user.id
        recipe_id = q.data.split(":")[1]

        recipe = RECIPES.get(recipe_id)
        if not recipe:
            await q.answer("Рецепт не найден!", show_alert=True)
            return

        p = await db.get_player(uid)
        mats = await db.get_materials(uid)
        inv = await db.get_inventory(uid)

        can_craft, missing = _check_recipe(recipe, mats, inv, p)
        if not can_craft:
            await q.answer("Не хватает ресурсов!", show_alert=True)
            return

        # Списать золото
        await db.update_player(uid, gold=p["gold"] - recipe["gold_cost"])

        # Списать материалы
        for mat_id, need in recipe["materials"].items():
            await db.remove_material(uid, mat_id, need)

        # Списать предметы из инвентаря (если нужны)
        for item_id, need in recipe.get("base_items", {}).items():
            await db.remove_from_inventory(uid, item_id)

        # Выдать результат
        result_id = recipe["result"]
        special = recipe.get("special")

        if special == "forge_free":
            await db.add_consumable(uid, "forge_ticket")
            result_name = CRAFT_SPECIALS[result_id]["name"]
            result_msg  = f"📦 Добавлен в расходники"
        elif result_id in ITEMS:
            already = await db.has_item(uid, result_id)
            if already:
                # Продать за 50% — не должно часто случаться в крафте
                sell = int(ITEMS[result_id]["price"] * 0.5)
                p2 = await db.get_player(uid)
                await db.update_player(uid, gold=p2["gold"] + sell)
                result_name = ITEMS[result_id]["name"]
                result_msg  = f"_Уже есть в инвентаре — продан за {sell}💰_"
            else:
                await db.add_to_inventory(uid, result_id)
                result_name = ITEMS[result_id]["name"]
                result_msg  = "📦 Добавлен в инвентарь!"
        else:
            result_name = result_id
            result_msg  = ""

        await q.edit_message_text(
            f"✅ *Крафт завершён!*\n\n"
            f"🔨 *{recipe['name']}*\n\n"
            f"📦 Получено: *{result_name}*\n"
            f"{result_msg}\n\n"
            f"💰 Потрачено: *{recipe['gold_cost']}* золота",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔨 Ещё крафт", callback_data="craft_menu")],
                [InlineKeyboardButton("🎒 Инвентарь", callback_data="inventory")],
            ])
        )

    @staticmethod
    @guard_handler()
    async def show_materials_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        """Версия для команды /materials"""
        db: Database = ctx.bot_data["db"]
        uid = update.effective_user.id
        mats = await db.get_materials(uid)
        if not mats:
            text = (
                "🧪 *Мои материалы*\n\n"
                "_Пусто. Материалы выпадают после боёв._\n\n"
                "Чем больше боёв — тем больше материалов!"
            )
        else:
            lines = ["🧪 *Мои материалы:*\n"]
            for mat_id, amount in mats.items():
                mat = MATERIALS.get(mat_id, {})
                rarity = mat.get("rarity", "common")
                icons = {"common":"⬜","uncommon":"🟩","rare":"🟦","epic":"🟪","legendary":"🟨"}
                lines.append(f"{icons.get(rarity,'⬜')} *{mat.get('name', mat_id)}* × {amount}")
            text = "\n".join(lines)
        kb = InlineKeyboardMarkup([[
            InlineKeyboardButton("🔨 Верстак", callback_data="craft_menu"),
            InlineKeyboardButton("◀️ Профиль", callback_data="profile"),
        ]])
        await update.message.reply_text(text, parse_mode="Markdown", reply_markup=kb)

    @staticmethod
    @guard_handler()
    async def show_materials(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        q = update.callback_query
        await q.answer()
        db: Database = ctx.bot_data["db"]
        uid = q.from_user.id
        mats = await db.get_materials(uid)

        if not mats:
            text = (
                "🧪 *Мои материалы*\n\n"
                "_Пусто. Материалы выпадают после боёв._\n\n"
                "Чем больше боёв — тем больше материалов!"
            )
        else:
            lines = ["🧪 *Мои материалы:*\n"]
            for mat_id, amount in mats.items():
                mat = MATERIALS.get(mat_id, {})
                rarity = mat.get("rarity", "common")
                icons  = {"common": "⬜", "uncommon": "🟩",
                          "rare": "🟦", "epic": "🟪", "legendary": "🟨"}
                lines.append(
                    f"{icons.get(rarity, '⬜')} *{mat.get('name', mat_id)}* × {amount}"
                )
            text = "\n".join(lines)

        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔨 К рецептам", callback_data="craft_menu")],
            [InlineKeyboardButton("◀️ Профиль", callback_data="profile")],
        ])
        await q.edit_message_text(text, parse_mode="Markdown", reply_markup=kb)


# ─── ДРОП МАТЕРИАЛОВ ──────────────────────────────────────────────────────────

import random
from safety import guard_handler

async def roll_materials(db: Database, uid: int, player_level: int) -> list[str]:
    """
    Попытка дропа материалов после боя (победа или поражение).
    Возвращает список названий полученных материалов.
    """
    obtained = []
    for mat_id, data in MATERIAL_DROP.items():
        if player_level < data["min_level"]:
            continue
        if random.uniform(0, 100) <= data["drop_chance"]:
            await db.add_material(uid, mat_id, 1)
            mat = MATERIALS[mat_id]
            obtained.append(mat["name"])
    return obtained


def format_materials(mats: list[str]) -> str:
    if not mats:
        return ""
    return "\n\n🧪 *Получены материалы:*\n" + "\n".join(f"• {m}" for m in mats)


# ─── ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ──────────────────────────────────────────────────

def _check_recipe(
    recipe: dict, mats: dict, inv: list, p: dict
) -> tuple[bool, list[str]]:
    missing = []

    # Уровень
    if p["level"] < recipe["req_level"]:
        missing.append(f"Уровень {recipe['req_level']} (у тебя {p['level']})")

    # Материалы
    for mat_id, need in recipe["materials"].items():
        have = mats.get(mat_id, 0)
        if have < need:
            mat = MATERIALS.get(mat_id, {})
            missing.append(f"{mat.get('name', mat_id)}: {have}/{need}")

    # Предметы
    for item_id, need in recipe.get("base_items", {}).items():
        have = inv.count(item_id) if isinstance(inv, list) else (1 if item_id in inv else 0)
        if have < need:
            item = ITEMS.get(item_id, {})
            missing.append(f"{item.get('name', item_id)} (из инвентаря)")

    # Золото
    if p["gold"] < recipe["gold_cost"]:
        missing.append(f"Золото: {p['gold']}/{recipe['gold_cost']}")

    return len(missing) == 0, missing


async def _build_menu(
    db: Database, uid: int, p: dict
) -> tuple[str, InlineKeyboardMarkup]:
    mats = await db.get_materials(uid)
    inv  = await db.get_inventory(uid)

    # Группируем рецепты по слотам
    groups = {
        "🗡️ Оружие":  [],
        "🛡️ Броня":   [],
        "⛑️ Шлем":    [],
        "👢 Сапоги":  [],
        "💍 Кольцо":  [],
        "📿 Амулет":  [],
        "⚙️ Спец":    [],
    }
    slot_map = {
        "weapon": "🗡️ Оружие", "armor": "🛡️ Броня",
        "helmet": "⛑️ Шлем",   "boots": "👢 Сапоги",
        "ring":   "💍 Кольцо", "amulet": "📿 Амулет",
    }

    for rid, recipe in RECIPES.items():
        result_id = recipe["result"]
        if result_id in ITEMS:
            slot = ITEMS[result_id]["slot"]
            group = slot_map.get(slot, "⚙️ Спец")
        else:
            group = "⚙️ Спец"
        can, _ = _check_recipe(recipe, mats, inv, p)
        groups[group].append((rid, recipe, can))

    lines = [
        f"🔨 *ВЕРСТАК*\n"
        f"💰 Золото: *{p['gold']}*  |  Ур. *{p['level']}*\n"
        f"Выбери рецепт:"
    ]
    buttons = []

    for group_name, items in groups.items():
        if not items:
            continue
        ready = sum(1 for _, _, can in items if can)
        buttons.append([InlineKeyboardButton(
            f"{group_name} ({ready}/{len(items)} доступно)",
            callback_data=f"craft_group:{group_name}"
        )])

    buttons.append([InlineKeyboardButton(
        "🧪 Мои материалы", callback_data="craft_mats"
    )])
    buttons.append([InlineKeyboardButton("◀️ Профиль", callback_data="profile")])

    return "\n".join(lines), InlineKeyboardMarkup(buttons)


class CraftGroupHandler:

    @staticmethod
    async def show(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        q = update.callback_query
        await q.answer()
        db: Database = ctx.bot_data["db"]
        uid = q.from_user.id
        group_name = q.data.split(":", 1)[1]

        p    = await db.get_player(uid)
        mats = await db.get_materials(uid)
        inv  = await db.get_inventory(uid)

        slot_map = {
            "🗡️ Оружие": "weapon", "🛡️ Броня": "armor",
            "⛑️ Шлем":   "helmet", "👢 Сапоги": "boots",
            "💍 Кольцо": "ring",   "📿 Амулет": "amulet",
        }

        slot = slot_map.get(group_name)
        buttons = []
        lines = [f"*{group_name} — рецепты:*\n"]

        for rid, recipe in RECIPES.items():
            result_id = recipe["result"]
            if result_id in ITEMS:
                if ITEMS[result_id]["slot"] != slot and group_name != "⚙️ Спец":
                    continue
            elif group_name != "⚙️ Спец":
                continue

            can, missing = _check_recipe(recipe, mats, inv, p)
            icon = "✅" if can else "🔒"
            req  = recipe["req_level"]
            locked = p["level"] < req

            if result_id in ITEMS:
                res_name = ITEMS[result_id]["name"]
            else:
                res_name = CRAFT_SPECIALS.get(result_id, {}).get("name", result_id)

            label = f"{icon} {res_name} ({recipe['gold_cost']}💰)"
            if locked:
                label = f"🔒 {res_name} (Ур.{req})"

            buttons.append([InlineKeyboardButton(
                label, callback_data=f"craft_view:{rid}"
            )])

        buttons.append([InlineKeyboardButton("◀️ Верстак", callback_data="craft_menu")])
        await q.edit_message_text(
            "\n".join(lines),
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(buttons)
        )


# ─── РЕЦЕПТЫ ДЛЯ УНИКАЛЬНЫХ КРАФТОВЫХ ПРЕДМЕТОВ ──────────────────────────────
# Добавляем в RECIPES

CRAFT_ONLY_RECIPES = {

    # ══ ТИР 1 (1-10) ══════════════════════════════════════════════════════════
    "r_bone_dagger": {
        "name": "Крафт Костяного кинжала",
        "result": "bone_dagger",
        "materials": {"bone_fragment": 5, "iron_ore": 2},
        "base_items": {},
        "gold_cost": 30,
        "req_level": 1,
    },
    "r_rusted_cleaver": {
        "name": "Крафт Ржавого тесака",
        "result": "rusted_cleaver",
        "materials": {"iron_ore": 4, "bone_fragment": 3},
        "base_items": {},
        "gold_cost": 50,
        "req_level": 3,
    },
    "r_soldiers_sword": {
        "name": "Крафт Меча солдата",
        "result": "soldiers_sword",
        "materials": {"steel_ingot": 2, "iron_ore": 3, "bone_fragment": 2},
        "base_items": {},
        "gold_cost": 80,
        "req_level": 5,
    },
    "r_hunters_bow_blade": {
        "name": "Крафт Клинка охотника",
        "result": "hunters_bow_blade",
        "materials": {"steel_ingot": 2, "shadow_dust": 2, "bone_fragment": 3},
        "base_items": {},
        "gold_cost": 120,
        "req_level": 8,
    },
    "r_bone_armor": {
        "name": "Крафт Костяной брони",
        "result": "bone_armor",
        "materials": {"bone_fragment": 8, "iron_ore": 3},
        "base_items": {},
        "gold_cost": 40,
        "req_level": 2,
    },
    "r_scout_vest": {
        "name": "Крафт Жилета разведчика",
        "result": "scout_vest",
        "materials": {"shadow_dust": 3, "bone_fragment": 4},
        "base_items": {},
        "gold_cost": 100,
        "req_level": 6,
    },
    "r_iron_crown": {
        "name": "Крафт Железного венца",
        "result": "iron_crown",
        "materials": {"iron_ore": 5, "bone_fragment": 2},
        "base_items": {},
        "gold_cost": 60,
        "req_level": 4,
    },
    "r_shadow_hood": {
        "name": "Крафт Капюшона тени",
        "result": "shadow_hood",
        "materials": {"shadow_dust": 4, "bone_fragment": 2},
        "base_items": {},
        "gold_cost": 90,
        "req_level": 7,
    },
    "r_traveler_boots": {
        "name": "Крафт Сапог странника",
        "result": "traveler_boots",
        "materials": {"bone_fragment": 4, "iron_ore": 2},
        "base_items": {},
        "gold_cost": 45,
        "req_level": 3,
    },
    "r_swift_sandals": {
        "name": "Крафт Быстрых сандалий",
        "result": "swift_sandals",
        "materials": {"shadow_dust": 3, "bone_fragment": 3},
        "base_items": {},
        "gold_cost": 90,
        "req_level": 6,
    },
    "r_blood_ring": {
        "name": "Крафт Кольца крови",
        "result": "blood_ring",
        "materials": {"bone_fragment": 5, "iron_ore": 2},
        "base_items": {},
        "gold_cost": 55,
        "req_level": 4,
    },
    "r_bone_ring": {
        "name": "Крафт Костяного кольца",
        "result": "bone_ring",
        "materials": {"bone_fragment": 4, "mana_crystal": 2},
        "base_items": {},
        "gold_cost": 110,
        "req_level": 8,
    },
    "r_warrior_pendant": {
        "name": "Крафт Кулона воина",
        "result": "warrior_pendant",
        "materials": {"bone_fragment": 3, "iron_ore": 3},
        "base_items": {},
        "gold_cost": 35,
        "req_level": 2,
    },
    "r_shard_amulet": {
        "name": "Крафт Амулета осколка",
        "result": "shard_amulet",
        "materials": {"mana_crystal": 3, "bone_fragment": 2},
        "base_items": {},
        "gold_cost": 95,
        "req_level": 6,
    },

    # ══ ТИР 2 (11-20) ═════════════════════════════════════════════════════════
    "r_cursed_blade": {
        "name": "Крафт Проклятого клинка",
        "result": "cursed_blade",
        "materials": {"shadow_dust": 6, "steel_ingot": 4, "mana_crystal": 2},
        "base_items": {},
        "gold_cost": 250,
        "req_level": 11,
    },
    "r_venom_fang": {
        "name": "Крафт Ядовитого клыка",
        "result": "venom_fang",
        "materials": {"shadow_dust": 5, "enchanted_thread": 3, "bone_fragment": 4},
        "base_items": {},
        "gold_cost": 300,
        "req_level": 13,
    },
    "r_storm_axe": {
        "name": "Крафт Топора бури",
        "result": "storm_axe",
        "materials": {"steel_ingot": 6, "mana_crystal": 3, "iron_ore": 5},
        "base_items": {"war_axe": 1},
        "gold_cost": 400,
        "req_level": 15,
    },
    "r_soul_reaper": {
        "name": "Крафт Жнеца душ",
        "result": "soul_reaper",
        "materials": {"void_crystal": 2, "shadow_dust": 8, "enchanted_thread": 4},
        "base_items": {"cursed_blade": 1},
        "gold_cost": 550,
        "req_level": 18,
    },
    "r_cursed_armor": {
        "name": "Крафт Проклятой брони",
        "result": "cursed_armor",
        "materials": {"shadow_dust": 7, "steel_ingot": 4, "bone_fragment": 5},
        "base_items": {},
        "gold_cost": 270,
        "req_level": 11,
    },
    "r_storm_mail": {
        "name": "Крафт Брони бури",
        "result": "storm_mail",
        "materials": {"steel_ingot": 5, "mana_crystal": 4},
        "base_items": {"chain_mail": 1},
        "gold_cost": 350,
        "req_level": 14,
    },
    "r_berserker_hide": {
        "name": "Крафт Шкуры берсерка",
        "result": "berserker_hide",
        "materials": {"bone_fragment": 8, "shadow_dust": 4, "steel_ingot": 3},
        "base_items": {},
        "gold_cost": 380,
        "req_level": 16,
    },
    "r_mage_robe": {
        "name": "Крафт Мантии мага",
        "result": "mage_robe",
        "materials": {"enchanted_thread": 6, "mana_crystal": 5},
        "base_items": {},
        "gold_cost": 420,
        "req_level": 17,
    },
    "r_cursed_helm": {
        "name": "Крафт Проклятого шлема",
        "result": "cursed_helm",
        "materials": {"shadow_dust": 5, "steel_ingot": 3, "bone_fragment": 4},
        "base_items": {},
        "gold_cost": 260,
        "req_level": 12,
    },
    "r_berserker_skull": {
        "name": "Крафт Черепа берсерка",
        "result": "berserker_skull",
        "materials": {"bone_fragment": 10, "steel_ingot": 3, "shadow_dust": 3},
        "base_items": {},
        "gold_cost": 360,
        "req_level": 16,
    },
    "r_storm_boots": {
        "name": "Крафт Сапог бури",
        "result": "storm_boots",
        "materials": {"steel_ingot": 3, "mana_crystal": 2, "enchanted_thread": 2},
        "base_items": {},
        "gold_cost": 290,
        "req_level": 13,
    },
    "r_shadow_dancer": {
        "name": "Крафт Танцора теней",
        "result": "shadow_dancer",
        "materials": {"shadow_dust": 6, "enchanted_thread": 3},
        "base_items": {"phantom_boots": 1},
        "gold_cost": 400,
        "req_level": 17,
    },
    "r_cursed_ring": {
        "name": "Крафт Проклятого кольца",
        "result": "cursed_ring",
        "materials": {"shadow_dust": 5, "mana_crystal": 2},
        "base_items": {},
        "gold_cost": 240,
        "req_level": 12,
    },
    "r_storm_ring": {
        "name": "Крафт Кольца бури",
        "result": "storm_ring",
        "materials": {"steel_ingot": 4, "mana_crystal": 3},
        "base_items": {},
        "gold_cost": 360,
        "req_level": 16,
    },
    "r_soul_stone": {
        "name": "Крафт Камня душ",
        "result": "soul_stone",
        "materials": {"shadow_dust": 6, "mana_crystal": 3, "bone_fragment": 4},
        "base_items": {},
        "gold_cost": 320,
        "req_level": 14,
    },
    "r_storm_heart": {
        "name": "Крафт Сердца бури",
        "result": "storm_heart",
        "materials": {"steel_ingot": 4, "mana_crystal": 4, "enchanted_thread": 3},
        "base_items": {},
        "gold_cost": 450,
        "req_level": 18,
    },

    # ══ ТИР 3 (21-30) ═════════════════════════════════════════════════════════
    "r_void_reaper": {
        "name": "Крафт Жнеца пустоты",
        "result": "void_reaper",
        "materials": {"void_crystal": 4, "shadow_dust": 8, "enchanted_thread": 4},
        "base_items": {"soul_reaper": 1},
        "gold_cost": 700,
        "req_level": 21,
    },
    "r_titan_blade": {
        "name": "Крафт Клинка титана",
        "result": "titan_blade",
        "materials": {"titan_ore": 4, "steel_ingot": 6, "void_crystal": 2},
        "base_items": {},
        "gold_cost": 800,
        "req_level": 23,
    },
    "r_eclipse_sword": {
        "name": "Крафт Меча затмения",
        "result": "eclipse_sword",
        "materials": {"void_crystal": 3, "shadow_dust": 10, "mana_crystal": 5},
        "base_items": {"shadow_blade": 1},
        "gold_cost": 750,
        "req_level": 25,
    },
    "r_inferno_axe": {
        "name": "Крафт Топора инферно",
        "result": "inferno_axe",
        "materials": {"dragon_flame": 1, "titan_ore": 3, "steel_ingot": 6},
        "base_items": {"storm_axe": 1},
        "gold_cost": 900,
        "req_level": 27,
    },
    "r_void_armor": {
        "name": "Крафт Доспеха пустоты",
        "result": "void_armor",
        "materials": {"void_crystal": 5, "enchanted_thread": 5, "shadow_dust": 8},
        "base_items": {},
        "gold_cost": 750,
        "req_level": 21,
    },
    "r_titan_fortress": {
        "name": "Крафт Крепости титана",
        "result": "titan_fortress",
        "materials": {"titan_ore": 6, "steel_ingot": 6},
        "base_items": {"plate_armor": 1},
        "gold_cost": 950,
        "req_level": 24,
    },
    "r_eclipse_cloak": {
        "name": "Крафт Плаща затмения",
        "result": "eclipse_cloak",
        "materials": {"void_crystal": 3, "shadow_dust": 10, "enchanted_thread": 4},
        "base_items": {"shadow_cloak": 1},
        "gold_cost": 850,
        "req_level": 26,
    },
    "r_inferno_plate": {
        "name": "Крафт Лат инферно",
        "result": "inferno_plate",
        "materials": {"dragon_flame": 2, "titan_ore": 4, "void_crystal": 3},
        "base_items": {},
        "gold_cost": 1000,
        "req_level": 28,
    },
    "r_void_crown": {
        "name": "Крафт Короны пустоты",
        "result": "void_crown",
        "materials": {"void_crystal": 3, "mana_crystal": 5, "enchanted_thread": 3},
        "base_items": {"war_crown": 1},
        "gold_cost": 700,
        "req_level": 22,
    },
    "r_inferno_helm": {
        "name": "Крафт Шлема инферно",
        "result": "inferno_helm",
        "materials": {"dragon_flame": 1, "titan_ore": 3, "steel_ingot": 4},
        "base_items": {},
        "gold_cost": 850,
        "req_level": 26,
    },
    "r_void_walker": {
        "name": "Крафт Ходока пустоты",
        "result": "void_walker",
        "materials": {"void_crystal": 3, "shadow_dust": 6, "enchanted_thread": 3},
        "base_items": {"phantom_boots": 1},
        "gold_cost": 700,
        "req_level": 22,
    },
    "r_titan_stompers": {
        "name": "Крафт Поступи титана",
        "result": "titan_stompers",
        "materials": {"titan_ore": 4, "steel_ingot": 4},
        "base_items": {},
        "gold_cost": 850,
        "req_level": 27,
    },
    "r_void_sigil": {
        "name": "Крафт Перстня пустоты",
        "result": "void_sigil",
        "materials": {"void_crystal": 3, "mana_crystal": 3},
        "base_items": {},
        "gold_cost": 680,
        "req_level": 23,
    },
    "r_inferno_seal": {
        "name": "Крафт Печати инферно",
        "result": "inferno_seal",
        "materials": {"dragon_flame": 1, "titan_ore": 2, "void_crystal": 2},
        "base_items": {},
        "gold_cost": 900,
        "req_level": 28,
    },
    "r_void_eye": {
        "name": "Крафт Глаза пустоты",
        "result": "void_eye",
        "materials": {"void_crystal": 4, "mana_crystal": 4, "enchanted_thread": 3},
        "base_items": {},
        "gold_cost": 750,
        "req_level": 24,
    },
    "r_inferno_core": {
        "name": "Крафт Ядра инферно",
        "result": "inferno_core",
        "materials": {"dragon_flame": 2, "titan_ore": 3, "void_crystal": 3},
        "base_items": {},
        "gold_cost": 1000,
        "req_level": 28,
    },

    # ══ ТИР 4 (31-40) ═════════════════════════════════════════════════════════
    "r_celestial_blade": {
        "name": "Крафт Небесного клинка",
        "result": "celestial_blade",
        "materials": {"dragon_flame": 3, "dragon_scale_frag": 6, "void_crystal": 5},
        "base_items": {"void_reaper": 1},
        "gold_cost": 1500,
        "req_level": 31,
    },
    "r_abyssal_scythe": {
        "name": "Крафт Косы бездны",
        "result": "abyssal_scythe",
        "materials": {"dragon_flame": 3, "titan_ore": 6, "void_crystal": 5},
        "base_items": {"titan_blade": 1},
        "gold_cost": 1700,
        "req_level": 34,
    },
    "r_chaos_sword": {
        "name": "Крафт Меча хаоса",
        "result": "chaos_sword",
        "materials": {"dragon_flame": 2, "void_crystal": 6, "dragon_scale_frag": 5},
        "base_items": {"eclipse_sword": 1},
        "gold_cost": 1600,
        "req_level": 36,
    },
    "r_god_slayer": {
        "name": "Крафт Убийцы богов",
        "result": "god_slayer",
        "materials": {"dragon_flame": 4, "dragon_scale_frag": 8, "void_crystal": 6},
        "base_items": {"celestial_blade": 1},
        "gold_cost": 2000,
        "req_level": 39,
    },
    "r_celestial_plate": {
        "name": "Крафт Небесных лат",
        "result": "celestial_plate",
        "materials": {"dragon_scale_frag": 8, "dragon_flame": 2, "void_crystal": 5},
        "base_items": {"void_armor": 1},
        "gold_cost": 1600,
        "req_level": 31,
    },
    "r_abyssal_shell": {
        "name": "Крафт Панциря бездны",
        "result": "abyssal_shell",
        "materials": {"titan_ore": 8, "dragon_scale_frag": 6, "dragon_flame": 2},
        "base_items": {"titan_fortress": 1},
        "gold_cost": 1800,
        "req_level": 34,
    },
    "r_chaos_hide": {
        "name": "Крафт Шкуры хаоса",
        "result": "chaos_hide",
        "materials": {"dragon_flame": 3, "void_crystal": 6, "enchanted_thread": 6},
        "base_items": {},
        "gold_cost": 1700,
        "req_level": 37,
    },
    "r_celestial_crown": {
        "name": "Крафт Небесной короны",
        "result": "celestial_crown",
        "materials": {"dragon_scale_frag": 5, "dragon_flame": 2, "mana_crystal": 6},
        "base_items": {"void_crown": 1},
        "gold_cost": 1500,
        "req_level": 32,
    },
    "r_chaos_mask": {
        "name": "Крафт Маски хаоса",
        "result": "chaos_mask",
        "materials": {"void_crystal": 5, "dragon_flame": 2, "shadow_dust": 10},
        "base_items": {},
        "gold_cost": 1700,
        "req_level": 37,
    },
    "r_celestial_steps": {
        "name": "Крафт Небесной поступи",
        "result": "celestial_steps",
        "materials": {"dragon_scale_frag": 4, "void_crystal": 4, "enchanted_thread": 4},
        "base_items": {"void_walker": 1},
        "gold_cost": 1500,
        "req_level": 33,
    },
    "r_abyssal_treads": {
        "name": "Крафт Ступней бездны",
        "result": "abyssal_treads",
        "materials": {"titan_ore": 5, "dragon_scale_frag": 4},
        "base_items": {"titan_stompers": 1},
        "gold_cost": 1700,
        "req_level": 37,
    },
    "r_celestial_band": {
        "name": "Крафт Небесного обруча",
        "result": "celestial_band",
        "materials": {"dragon_scale_frag": 4, "dragon_flame": 1, "void_crystal": 3},
        "base_items": {},
        "gold_cost": 1500,
        "req_level": 33,
    },
    "r_chaos_signet": {
        "name": "Крафт Перстня хаоса",
        "result": "chaos_signet",
        "materials": {"dragon_flame": 2, "void_crystal": 5, "dragon_scale_frag": 4},
        "base_items": {},
        "gold_cost": 1800,
        "req_level": 38,
    },
    "r_star_fragment": {
        "name": "Крафт Осколка звезды",
        "result": "star_fragment",
        "materials": {"dragon_scale_frag": 5, "dragon_flame": 2, "mana_crystal": 6},
        "base_items": {"void_eye": 1},
        "gold_cost": 1500,
        "req_level": 32,
    },
    "r_abyss_heart": {
        "name": "Крафт Сердца бездны",
        "result": "abyss_heart",
        "materials": {"titan_ore": 5, "dragon_flame": 2, "void_crystal": 4},
        "base_items": {"inferno_core": 1},
        "gold_cost": 1800,
        "req_level": 38,
    },

    # ══ ТИР 5 (41-50) ═════════════════════════════════════════════════════════
    "r_eternity_blade": {
        "name": "Крафт Клинка вечности",
        "result": "eternity_blade",
        "materials": {"dragon_flame": 6, "dragon_scale_frag": 10, "void_crystal": 8},
        "base_items": {"god_slayer": 1},
        "gold_cost": 3000,
        "req_level": 41,
    },
    "r_world_ender": {
        "name": "Крафт Конца света",
        "result": "world_ender",
        "materials": {"dragon_flame": 8, "void_crystal": 10, "titan_ore": 8},
        "base_items": {"eternity_blade": 1},
        "gold_cost": 3500,
        "req_level": 44,
    },
    "r_genesis_spear": {
        "name": "Крафт Копья Генезиса",
        "result": "genesis_spear",
        "materials": {"dragon_flame": 7, "dragon_scale_frag": 12, "void_crystal": 8},
        "base_items": {"abyssal_scythe": 1},
        "gold_cost": 3200,
        "req_level": 46,
    },
    "r_omega_scythe": {
        "name": "Крафт Косы Омега",
        "result": "omega_scythe",
        "materials": {"dragon_flame": 10, "dragon_scale_frag": 15, "void_crystal": 12},
        "base_items": {"world_ender": 1, "genesis_spear": 1},
        "gold_cost": 5000,
        "req_level": 49,
    },
    "r_eternity_armor": {
        "name": "Крафт Доспеха вечности",
        "result": "eternity_armor",
        "materials": {"dragon_flame": 6, "dragon_scale_frag": 10, "titan_ore": 8},
        "base_items": {"celestial_plate": 1},
        "gold_cost": 3000,
        "req_level": 41,
    },
    "r_world_shell": {
        "name": "Крафт Панциря мира",
        "result": "world_shell",
        "materials": {"dragon_flame": 8, "titan_ore": 10, "void_crystal": 8},
        "base_items": {"abyssal_shell": 1},
        "gold_cost": 3800,
        "req_level": 45,
    },
    "r_genesis_robe": {
        "name": "Крафт Мантии Генезиса",
        "result": "genesis_robe",
        "materials": {"dragon_flame": 7, "void_crystal": 10, "enchanted_thread": 10},
        "base_items": {"chaos_hide": 1},
        "gold_cost": 3500,
        "req_level": 47,
    },
    "r_omega_fortress": {
        "name": "Крафт Крепости Омега",
        "result": "omega_fortress",
        "materials": {"dragon_flame": 10, "titan_ore": 12, "void_crystal": 10, "dragon_scale_frag": 12},
        "base_items": {"world_shell": 1, "genesis_robe": 1},
        "gold_cost": 6000,
        "req_level": 50,
    },
    "r_eternity_crown": {
        "name": "Крафт Короны вечности",
        "result": "eternity_crown",
        "materials": {"dragon_flame": 5, "dragon_scale_frag": 8, "mana_crystal": 8},
        "base_items": {"celestial_crown": 1},
        "gold_cost": 2800,
        "req_level": 42,
    },
    "r_omega_helm": {
        "name": "Крафт Шлема Омега",
        "result": "omega_helm",
        "materials": {"dragon_flame": 8, "void_crystal": 8, "dragon_scale_frag": 10},
        "base_items": {"chaos_mask": 1, "eternity_crown": 1},
        "gold_cost": 4500,
        "req_level": 48,
    },
    "r_eternity_steps": {
        "name": "Крафт Шагов вечности",
        "result": "eternity_steps",
        "materials": {"dragon_flame": 5, "void_crystal": 7, "dragon_scale_frag": 6},
        "base_items": {"celestial_steps": 1},
        "gold_cost": 2800,
        "req_level": 42,
    },
    "r_omega_treads": {
        "name": "Крафт Поступи Омега",
        "result": "omega_treads",
        "materials": {"dragon_flame": 8, "titan_ore": 8, "void_crystal": 7},
        "base_items": {"abyssal_treads": 1, "eternity_steps": 1},
        "gold_cost": 4500,
        "req_level": 48,
    },
    "r_eternity_ring": {
        "name": "Крафт Кольца вечности",
        "result": "eternity_ring",
        "materials": {"dragon_flame": 5, "dragon_scale_frag": 7, "void_crystal": 5},
        "base_items": {"celestial_band": 1},
        "gold_cost": 2800,
        "req_level": 43,
    },
    "r_omega_signet": {
        "name": "Крафт Перстня Омега",
        "result": "omega_signet",
        "materials": {"dragon_flame": 8, "void_crystal": 9, "dragon_scale_frag": 9},
        "base_items": {"chaos_signet": 1, "eternity_ring": 1},
        "gold_cost": 4800,
        "req_level": 49,
    },
    "r_eternity_core": {
        "name": "Крафт Ядра вечности",
        "result": "eternity_core",
        "materials": {"dragon_flame": 5, "dragon_scale_frag": 8, "void_crystal": 6},
        "base_items": {"star_fragment": 1},
        "gold_cost": 2800,
        "req_level": 43,
    },
    "r_omega_heart": {
        "name": "Ω Крафт Сердца Омега",
        "result": "omega_heart",
        "materials": {"dragon_flame": 12, "dragon_scale_frag": 15, "void_crystal": 12, "titan_ore": 10},
        "base_items": {"abyss_heart": 1, "eternity_core": 1},
        "gold_cost": 7000,
        "req_level": 50,
    },
}

# Объединяем с основными рецептами
RECIPES.update(CRAFT_ONLY_RECIPES)
