"""
Система дропа предметов после боя
Вызывается из battle.py после каждого боя
"""

import random
from database import Database
from gamedata import ITEMS

# ── Редкость ──────────────────────────────────────────────────────────────────

RARITY = {
    "common":    {"label": "⬜ Обычный",     "base_chance": 55},
    "uncommon":  {"label": "🟩 Необычный",   "base_chance": 28},
    "rare":      {"label": "🟦 Редкий",      "base_chance": 12},
    "epic":      {"label": "🟪 Эпический",   "base_chance": 4},
    "legendary": {"label": "🟨 Легендарный", "base_chance": 1},
}

ITEM_RARITY = {
    "iron_sword":     "common",
    "leather_armor":  "common",
    "leather_helm":   "common",
    "light_boots":    "common",
    "iron_ring":      "common",
    "life_amulet":    "common",
    "steel_sword":    "uncommon",
    "chain_mail":     "uncommon",
    "iron_helm":      "uncommon",
    "iron_boots":     "uncommon",
    "defense_ring":   "uncommon",
    "shield_amulet":  "uncommon",
    "shadow_blade":   "rare",
    "war_axe":        "rare",
    "arcane_staff":   "rare",
    "plate_armor":    "rare",
    "shadow_cloak":   "rare",
    "war_crown":      "rare",
    "phantom_boots":  "rare",
    "berserker_ring": "rare",
    "oracle_ring":    "rare",
    "war_amulet":     "rare",
    "void_dagger":    "epic",
    "titan_hammer":   "epic",
    "void_shroud":    "epic",
    "titan_helm":     "epic",
    "void_steps":     "epic",
    "titan_ring":     "epic",
    "shadow_amulet":  "epic",
    "dragon_sword":   "legendary",
    "dragon_scale":   "legendary",
    "dragon_heart":   "legendary",
}

# Базовый шанс дропа (%)
BASE_DROP_CHANCE = 40
# Шанс второго предмета при победе над живым игроком
BONUS_DROP_CHANCE = 15


async def roll_drop(
    db: Database,
    uid: int,
    player_level: int,
    is_winner: bool,
    is_bot_fight: bool,
) -> list[dict]:
    """
    Попытка получить предмет(ы) после боя.
    Возвращает список дропнувших предметов (может быть пустым).
    """
    if not is_winner:
        return []  # Только победитель получает дроп

    results = []

    # Первый дроп
    if random.uniform(0, 100) <= BASE_DROP_CHANCE:
        item = _pick_item(player_level)
        if item:
            drop = await _process_item(db, uid, item, player_level)
            results.append(drop)

    # Бонусный дроп при победе над реальным игроком
    if not is_bot_fight and random.uniform(0, 100) <= BONUS_DROP_CHANCE:
        item = _pick_item(player_level, min_rarity="uncommon")
        if item:
            drop = await _process_item(db, uid, item, player_level)
            results.append(drop)

    return results


def _pick_rarity(player_level: int, min_rarity: str = "common") -> str:
    """Выбрать редкость с учётом уровня игрока"""
    order = ["common", "uncommon", "rare", "epic", "legendary"]
    min_idx = order.index(min_rarity)

    weights = {}
    for i, r in enumerate(order):
        if i < min_idx:
            weights[r] = 0
            continue
        base = RARITY[r]["base_chance"]
        # Высокий уровень повышает шанс редких предметов
        if r == "rare"      and player_level >= 10: base += 5
        if r == "epic"      and player_level >= 15: base += 3
        if r == "legendary" and player_level >= 20: base += 1
        # Низкий уровень — только common/uncommon
        if r == "rare"      and player_level < 8:  base = 0
        if r == "epic"      and player_level < 13: base = 0
        if r == "legendary" and player_level < 18: base = 0
        weights[r] = max(0, base)

    total = sum(weights.values())
    if total == 0:
        return "common"

    rarities = list(weights.keys())
    probs    = [weights[r] / total for r in rarities]
    return random.choices(rarities, weights=probs, k=1)[0]


def _pick_item(player_level: int, min_rarity: str = "common") -> dict | None:
    """Выбрать конкретный предмет"""
    rarity = _pick_rarity(player_level, min_rarity)

    candidates = [
        (iid, ITEMS[iid]) for iid, r in ITEM_RARITY.items()
        if r == rarity
        and iid in ITEMS
        and ITEMS[iid]["req_level"] <= player_level + 2
    ]

    if not candidates:
        # Откат на common
        candidates = [
            (iid, ITEMS[iid]) for iid, r in ITEM_RARITY.items()
            if r == "common" and iid in ITEMS
            and ITEMS[iid]["req_level"] <= player_level + 2
        ]

    if not candidates:
        return None

    iid, item = random.choice(candidates)
    return {"id": iid, "item": item, "rarity": rarity}


async def _process_item(
    db: Database, uid: int, drop: dict, player_level: int
) -> dict:
    """
    Выдать предмет или золото если уже есть.
    Возвращает dict с результатом.
    """
    item_id = drop["id"]
    item    = drop["item"]
    rarity  = drop["rarity"]

    already = await db.has_item(uid, item_id)
    if already:
        # Продаём за 25-40% цены (зависит от редкости)
        sell_pct = {"common": 0.20, "uncommon": 0.25,
                    "rare": 0.30, "epic": 0.35, "legendary": 0.40}
        gold = max(5, int(item["price"] * sell_pct.get(rarity, 0.25)))
        p = await db.get_player(uid)
        await db.update_player(uid, gold=p["gold"] + gold)
        return {
            "type":   "gold",
            "item":   item,
            "rarity": rarity,
            "gold":   gold,
        }
    else:
        await db.add_to_inventory(uid, item_id)
        return {
            "type":   "item",
            "item":   item,
            "rarity": rarity,
        }


def format_drop(drops: list[dict]) -> str:
    """Форматировать дроп для сообщения в бою"""
    if not drops:
        return ""

    lines = ["\n\n🎁 *ДРОП:*"]
    for d in drops:
        rar_label = RARITY[d["rarity"]]["label"]
        item_name = d["item"]["name"]
        if d["type"] == "item":
            lines.append(f"{rar_label} *{item_name}*\n📦 Добавлен в инвентарь")
        else:
            lines.append(
                f"{rar_label} *{item_name}*\n"
                f"_Уже есть — продан за {d['gold']}💰_"
            )
    return "\n".join(lines)

