"""Игровые данные: классы, экипировка, достижения, пассивки, квесты, зачарования"""

# ─── КЛАССЫ ────────────────────────────────────────────────────────────────────
CLASSES = {
    "warrior": {
        "name": "⚔️ Воин", "emoji": "⚔️",
        "desc": "Танк. Высокий HP/защита. Умение: гарантированный блок.",
        "strength": 7, "endurance": 9, "agility": 3, "intuition": 3,
        "str_growth": 1.8, "end_growth": 2.2, "agi_growth": 0.6, "int_growth": 0.5,
        "skill": "🛡️ Железный блок",
        "skill_desc": "50% блок + 20% шанс полного отражения удара",
    },
    "assassin": {
        "name": "🗡️ Ассасин", "emoji": "🗡️",
        "desc": "Стёкло-пушка. Гарантированный крит, высокий уворот.",
        "strength": 6, "endurance": 3, "agility": 10, "intuition": 4,
        "str_growth": 1.6, "end_growth": 0.7, "agi_growth": 2.4, "int_growth": 0.9,
        "skill": "⚡ Смертельный удар",
        "skill_desc": "Гарантированный крит ×1.8, игнорирует 30% защиты врага",
    },
    "mage": {
        "name": "🔮 Маг", "emoji": "🔮",
        "desc": "Контроль через предвидение. Умение удваивает предвидение и контрудар.",
        "strength": 5, "endurance": 5, "agility": 5, "intuition": 9,
        "str_growth": 1.3, "end_growth": 1.1, "agi_growth": 1.0, "int_growth": 2.3,
        "skill": "🧿 Предчувствие",
        "skill_desc": "Предвидение ×2, контрудар ×2 на этот раунд",
    },
    "berserker": {
        "name": "💢 Берсерк", "emoji": "💢",
        "desc": "Огромный урон в ярости, но теряет защиту.",
        "strength": 11, "endurance": 5, "agility": 4, "intuition": 2,
        "str_growth": 2.8, "end_growth": 1.0, "agi_growth": 0.9, "int_growth": 0.4,
        "skill": "💥 Ярость",
        "skill_desc": "Гарантированный крит, атака ×1.5, защита -30% в раунде",
    },
}

# ─── ПАССИВНЫЕ СПОСОБНОСТИ ─────────────────────────────────────────────────────
# Выбираются каждые 5 уровней (5, 10, 15, 20...)
PASSIVES = {
    "iron_skin": {
        "name": "🦾 Железная кожа",
        "desc": "+15% к защите",
        "stat_bonus": {"def_pct": 0.15},
    },
    "berserker_heart": {
        "name": "❤️‍🔥 Сердце берсерка",
        "desc": "+10% к атаке",
        "stat_bonus": {"atk_pct": 0.10},
    },
    "shadow_step": {
        "name": "👁️ Теневой шаг",
        "desc": "+8% к увороту",
        "stat_bonus": {"dodge": 8},
    },
    "oracle_eye": {
        "name": "🔮 Глаз оракула",
        "desc": "+10% к предвидению",
        "stat_bonus": {"foresight": 10},
    },
    "blood_thirst": {
        "name": "🩸 Жажда крови",
        "desc": "+6% к шансу крита",
        "stat_bonus": {"crit_chance": 6},
    },
    "titan_will": {
        "name": "⚙️ Воля титана",
        "desc": "+15% к максимальному HP",
        "stat_bonus": {"hp_pct": 0.15},
    },
    "counter_master": {
        "name": "🤺 Мастер контрудара",
        "desc": "+10% к контрудару",
        "stat_bonus": {"counter": 10},
    },
    "deadly_precision": {
        "name": "🎯 Смертельная точность",
        "desc": "+8% к точности и +15% к силе крита",
        "stat_bonus": {"accuracy": 8, "crit_power": 15},
    },
}

# ─── ДОСТИЖЕНИЯ ────────────────────────────────────────────────────────────────
ACHIEVEMENTS = {
    "first_blood": {
        "name": "🩸 Первая кровь",
        "desc": "Победи в первом бою",
        "reward_gold": 50,
        "title": "Дебютант",
    },
    "wins_10": {
        "name": "⚔️ Десять побед",
        "desc": "Одержи 10 побед",
        "reward_gold": 100,
        "title": "Боец",
    },
    "wins_50": {
        "name": "🏆 Пятьдесят побед",
        "desc": "Одержи 50 побед",
        "reward_gold": 300,
        "title": "Ветеран",
    },
    "wins_100": {
        "name": "👑 Сотня побед",
        "desc": "Одержи 100 побед",
        "reward_gold": 700,
        "title": "Легенда",
    },
    "streak_5": {
        "name": "🔥 Серия из 5",
        "desc": "Победи 5 раз подряд без поражений",
        "reward_gold": 150,
        "title": "Огонь",
    },
    "streak_10": {
        "name": "⚡ Серия из 10",
        "desc": "Победи 10 раз подряд",
        "reward_gold": 400,
        "title": "Молния",
    },
    "rich": {
        "name": "💰 Богач",
        "desc": "Накопи 1000 золота",
        "reward_gold": 0,
        "title": "Торговец",
    },
    "level_10": {
        "name": "⭐ Опытный",
        "desc": "Достигни 10 уровня",
        "reward_gold": 200,
        "title": "Опытный",
    },
    "level_25": {
        "name": "🌟 Мастер",
        "desc": "Достигни 25 уровня",
        "reward_gold": 500,
        "title": "Мастер",
    },
    "level_50": {
        "name": "💫 Максимум",
        "desc": "Достигни 50 уровня",
        "reward_gold": 1000,
        "title": "Непобедимый",
    },
    "guild_founder": {
        "name": "🏰 Основатель",
        "desc": "Создай гильдию",
        "reward_gold": 100,
        "title": "Основатель",
    },
    "daily_7": {
        "name": "📅 Неделя подряд",
        "desc": "Заходи 7 дней подряд",
        "reward_gold": 250,
        "title": "Постоянный",
    },
    "mmr_1500": {
        "name": "💎 Алмазный ранг",
        "desc": "Достигни 1500 MMR",
        "reward_gold": 350,
        "title": "Алмаз",
    },
    "mmr_2000": {
        "name": "👑 Легенда арены",
        "desc": "Достигни 2000 MMR",
        "reward_gold": 1000,
        "title": "Легенда Арены",
    },
}

# ─── КВЕСТЫ ────────────────────────────────────────────────────────────────────
QUESTS = {
    "q_win3": {
        "name": "⚔️ Победи 3 раза",
        "desc": "Одержи 3 победы в Арене",
        "type": "wins", "target": 3,
        "reward_gold": 80, "reward_exp": 60,
    },
    "q_win10": {
        "name": "🏆 Победи 10 раз",
        "desc": "Одержи 10 побед в Арене",
        "type": "wins", "target": 10,
        "reward_gold": 200, "reward_exp": 150,
    },
    "q_play10": {
        "name": "⚔️ Сыграй 10 боёв",
        "desc": "Прими участие в 10 боях",
        "type": "battles", "target": 10,
        "reward_gold": 120, "reward_exp": 80,
    },
    "q_play30": {
        "name": "🎯 Сыграй 30 боёв",
        "desc": "Прими участие в 30 боях",
        "type": "battles", "target": 30,
        "reward_gold": 300, "reward_exp": 200,
    },
    "q_daily3": {
        "name": "📅 3 дня подряд",
        "desc": "Заходи 3 дня подряд",
        "type": "daily_streak", "target": 3,
        "reward_gold": 100, "reward_exp": 50,
    },
    "q_level5": {
        "name": "⭐ Достигни 5 уровня",
        "desc": "Прокачайся до 5 уровня",
        "type": "level", "target": 5,
        "reward_gold": 150, "reward_exp": 0,
    },
    "q_level15": {
        "name": "🌟 Достигни 15 уровня",
        "desc": "Прокачайся до 15 уровня",
        "type": "level", "target": 15,
        "reward_gold": 400, "reward_exp": 0,
    },
    "q_gold500": {
        "name": "💰 Накопи 500 золота",
        "desc": "Имей 500 монет одновременно",
        "type": "gold", "target": 500,
        "reward_gold": 100, "reward_exp": 50,
    },
}

# ─── ЗАЧАРОВАНИЯ ───────────────────────────────────────────────────────────────
ENCHANTMENTS = {
    "fire": {
        "name": "🔥 Огненное",
        "desc": "+12 к атаке",
        "price": 150,
        "stats": {"atk": 12},
    },
    "frost": {
        "name": "❄️ Ледяное",
        "desc": "+10 к защите",
        "price": 150,
        "stats": {"def": 10},
    },
    "shadow": {
        "name": "🌑 Теневое",
        "desc": "+8% к увороту",
        "price": 180,
        "stats": {"dodge": 8},
    },
    "holy": {
        "name": "✨ Святое",
        "desc": "+60 к HP",
        "price": 160,
        "stats": {"hp": 60},
    },
    "void": {
        "name": "🌀 Пустотное",
        "desc": "+8% к крит шансу",
        "price": 200,
        "stats": {"crit_chance": 8},
    },
    "thunder": {
        "name": "⚡ Громовое",
        "desc": "+20% к силе крита",
        "price": 220,
        "stats": {"crit_power": 20},
    },
}

# ─── СЛОТЫ И ПРЕДМЕТЫ ──────────────────────────────────────────────────────────
SLOTS = {
    "weapon": "🗡️ Оружие",
    "armor":  "🛡️ Броня",
    "helmet": "⛑️ Шлем",
    "boots":  "👢 Сапоги",
    "ring":   "💍 Кольцо",
    "amulet": "📿 Амулет",
}

ITEMS = {
    "iron_sword":    {"name":"⚔️ Железный меч","slot":"weapon","desc":"Простое оружие.","req_level":1,"price":80,"stats":{"atk":8,"accuracy":2},"scale_per_level":{"atk":1.0}},
    "steel_sword":   {"name":"⚔️ Стальной меч","slot":"weapon","desc":"Сбалансированный клинок.","req_level":5,"price":220,"stats":{"atk":20,"crit_chance":3,"accuracy":3},"scale_per_level":{"atk":2.0,"crit_chance":0.2}},
    "shadow_blade":  {"name":"🗡️ Клинок тени","slot":"weapon","desc":"Мечта ассасина.","req_level":10,"price":480,"stats":{"atk":30,"crit_chance":8,"crit_power":20,"dodge":3},"scale_per_level":{"atk":2.5,"crit_chance":0.3,"crit_power":1.5}},
    "war_axe":       {"name":"🪓 Боевой топор","slot":"weapon","desc":"Медленный, но сокрушительный.","req_level":8,"price":350,"stats":{"atk":38,"crit_power":35,"accuracy":-8},"scale_per_level":{"atk":3.0,"crit_power":2.0}},
    "arcane_staff":  {"name":"🪄 Магический посох","slot":"weapon","desc":"Усиливает предвидение.","req_level":7,"price":400,"stats":{"atk":18,"foresight":10,"counter":6},"scale_per_level":{"atk":1.5,"foresight":0.6,"counter":0.4}},
    "void_dagger":   {"name":"🌑 Кинжал пустоты","slot":"weapon","desc":"Пронзает любую броню.","req_level":15,"price":780,"stats":{"atk":35,"crit_chance":14,"crit_power":25,"dodge":4},"scale_per_level":{"atk":3.0,"crit_chance":0.4,"crit_power":2.0}},
    "titan_hammer":  {"name":"🔨 Молот титана","slot":"weapon","desc":"Сокрушает щиты.","req_level":18,"price":1000,"stats":{"atk":55,"crit_power":45,"def":8,"accuracy":-10},"scale_per_level":{"atk":4.0,"crit_power":2.5,"def":0.5}},
    "dragon_sword":  {"name":"🔥 Меч дракона","slot":"weapon","desc":"Легендарное оружие.","req_level":20,"price":1400,"stats":{"atk":60,"crit_chance":12,"crit_power":40,"accuracy":5},"scale_per_level":{"atk":4.5,"crit_chance":0.4,"crit_power":2.5}},
    "leather_armor": {"name":"🧥 Кожаная броня","slot":"armor","desc":"Лёгкая защита.","req_level":1,"price":70,"stats":{"def":6,"dodge":2,"hp":25},"scale_per_level":{"def":1.0,"hp":6}},
    "chain_mail":    {"name":"⛓️ Кольчуга","slot":"armor","desc":"Баланс защиты.","req_level":5,"price":200,"stats":{"def":14,"hp":55},"scale_per_level":{"def":1.5,"hp":9}},
    "plate_armor":   {"name":"🛡️ Латные доспехи","slot":"armor","desc":"Непробиваемая защита.","req_level":10,"price":450,"stats":{"def":28,"hp":110,"dodge":-4},"scale_per_level":{"def":2.5,"hp":14}},
    "shadow_cloak":  {"name":"🌑 Плащ теней","slot":"armor","desc":"Сливается с темнотой.","req_level":12,"price":530,"stats":{"def":12,"dodge":14,"hp":45},"scale_per_level":{"def":1.0,"dodge":0.5,"hp":7}},
    "dragon_scale":  {"name":"🐉 Чешуя дракона","slot":"armor","desc":"Практически непробиваема.","req_level":20,"price":1500,"stats":{"def":50,"hp":200,"counter":8},"scale_per_level":{"def":3.0,"hp":18,"counter":0.4}},
    "void_shroud":   {"name":"🌀 Покров пустоты","slot":"armor","desc":"Поглощает всё.","req_level":25,"price":2000,"stats":{"def":60,"hp":240,"foresight":12,"dodge":5},"scale_per_level":{"def":3.5,"hp":20,"foresight":0.5}},
    "leather_helm":  {"name":"⛑️ Кожаный шлем","slot":"helmet","desc":"Базовая защита.","req_level":1,"price":50,"stats":{"def":4,"hp":18},"scale_per_level":{"def":0.6,"hp":4}},
    "iron_helm":     {"name":"🪖 Железный шлем","slot":"helmet","desc":"Надёжная защита.","req_level":5,"price":150,"stats":{"def":10,"hp":35,"foresight":3},"scale_per_level":{"def":1.0,"hp":6,"foresight":0.2}},
    "war_crown":     {"name":"👑 Боевая корона","slot":"helmet","desc":"Символ власти.","req_level":15,"price":750,"stats":{"def":18,"hp":70,"atk":12,"foresight":6},"scale_per_level":{"def":1.5,"hp":9,"atk":1.0,"foresight":0.3}},
    "titan_helm":    {"name":"⚙️ Шлем титана","slot":"helmet","desc":"Удары отскакивают.","req_level":22,"price":1200,"stats":{"def":30,"hp":110,"counter":7},"scale_per_level":{"def":2.0,"hp":12,"counter":0.4}},
    "light_boots":   {"name":"👟 Лёгкие сапоги","slot":"boots","desc":"Быстро и точно.","req_level":1,"price":60,"stats":{"dodge":5,"accuracy":4},"scale_per_level":{"dodge":0.3,"accuracy":0.2}},
    "iron_boots":    {"name":"🥾 Железные сапоги","slot":"boots","desc":"Надёжные.","req_level":6,"price":170,"stats":{"def":8,"hp":28,"dodge":-2},"scale_per_level":{"def":1.0,"hp":5}},
    "phantom_boots": {"name":"💨 Сапоги призрака","slot":"boots","desc":"Ты почти невидим.","req_level":14,"price":650,"stats":{"dodge":18,"accuracy":9,"counter":4},"scale_per_level":{"dodge":0.5,"accuracy":0.3,"counter":0.2}},
    "void_steps":    {"name":"🌑 Шаги пустоты","slot":"boots","desc":"След из теней.","req_level":20,"price":950,"stats":{"dodge":22,"accuracy":10,"def":6,"hp":35},"scale_per_level":{"dodge":0.6,"accuracy":0.4,"def":0.5,"hp":6}},
    "iron_ring":     {"name":"💍 Железное кольцо","slot":"ring","desc":"Бонус к атаке.","req_level":3,"price":90,"stats":{"atk":6},"scale_per_level":{"atk":0.5}},
    "defense_ring":  {"name":"🔵 Кольцо стража","slot":"ring","desc":"Щит на пальце.","req_level":5,"price":160,"stats":{"def":7,"hp":22},"scale_per_level":{"def":0.8,"hp":4}},
    "berserker_ring":{"name":"🔴 Кольцо берсерка","slot":"ring","desc":"Сила крита.","req_level":8,"price":270,"stats":{"crit_chance":7,"crit_power":25,"def":-4},"scale_per_level":{"crit_chance":0.4,"crit_power":1.5}},
    "oracle_ring":   {"name":"🟣 Кольцо оракула","slot":"ring","desc":"Видит скрытое.","req_level":10,"price":320,"stats":{"foresight":12,"counter":7},"scale_per_level":{"foresight":0.5,"counter":0.3}},
    "titan_ring":    {"name":"⚙️ Кольцо титана","slot":"ring","desc":"Мощь.","req_level":18,"price":650,"stats":{"def":14,"hp":55,"atk":9},"scale_per_level":{"def":1.0,"hp":6,"atk":0.6}},
    "life_amulet":   {"name":"❤️ Амулет жизни","slot":"amulet","desc":"Запас HP.","req_level":4,"price":120,"stats":{"hp":70},"scale_per_level":{"hp":10}},
    "shield_amulet": {"name":"🛡️ Амулет защитника","slot":"amulet","desc":"Невидимый щит.","req_level":7,"price":240,"stats":{"def":9,"hp":40},"scale_per_level":{"def":0.8,"hp":7}},
    "war_amulet":    {"name":"⚔️ Амулет войны","slot":"amulet","desc":"Всё ради победы.","req_level":9,"price":300,"stats":{"atk":14,"crit_chance":5},"scale_per_level":{"atk":1.2,"crit_chance":0.3}},
    "shadow_amulet": {"name":"🌑 Амулет теней","slot":"amulet","desc":"Ты — тень.","req_level":15,"price":700,"stats":{"dodge":12,"counter":9,"foresight":7},"scale_per_level":{"dodge":0.5,"counter":0.3,"foresight":0.3}},
    "dragon_heart":  {"name":"🔥 Сердце дракона","slot":"amulet","desc":"Сила дракона.","req_level":25,"price":2200,"stats":{"hp":220,"atk":22,"def":18,"crit_power":35},"scale_per_level":{"hp":18,"atk":1.8,"def":1.2,"crit_power":1.5}},
}


def items_by_slot_all(slot: str) -> list[tuple[str, dict]]:
    return [(iid, item) for iid, item in ITEMS.items() if item["slot"] == slot]


# ─── ФОРМУЛЫ ───────────────────────────────────────────────────────────────────

def calc_skills(player: dict, cls: dict) -> dict:
    lvl = player["level"]
    return {
        "strength":  cls["strength"]  + int(cls["str_growth"] * (lvl - 1)),
        "endurance": cls["endurance"] + int(cls["end_growth"]  * (lvl - 1)),
        "agility":   cls["agility"]   + int(cls["agi_growth"]  * (lvl - 1)),
        "intuition": cls["intuition"] + int(cls["int_growth"]  * (lvl - 1)),
    }


def get_item_stats(item: dict, player_level: int) -> dict:
    base  = dict(item.get("stats", {}))
    scale = item.get("scale_per_level", {})
    bonus = max(0, player_level - item.get("req_level", 1))
    return {k: round(v + scale.get(k, 0) * bonus, 1) for k, v in base.items()}


def calc_stats(player: dict, equipped: dict,
               enchantments: dict = None, passive_id: str = "") -> tuple[dict, dict]:
    cls    = CLASSES[player["class_id"]]
    skills = calc_skills(player, cls)
    lvl    = player["level"]
    s, e, a, i = (skills["strength"], skills["endurance"],
                  skills["agility"],  skills["intuition"])

    stats = {
        "hp":          100 + e * 14,
        "atk":           8 + s * 3,
        "def":           3 + e * 2,
        "crit_chance":   2 + a * 1.5,
        "crit_power":  150 + s * 3,
        "foresight":     1 + i * 1.8,
        "dodge":         1 + a * 1.5,
        "counter":       0 + i * 1.0,
        "accuracy":     80 + a * 0.6,
    }

    # Экипировка
    for slot, item_id in equipped.items():
        if item_id and item_id in ITEMS:
            for stat, val in get_item_stats(ITEMS[item_id], lvl).items():
                if stat in stats:
                    stats[stat] += val

    # Зачарования
    if enchantments:
        for slot, ench_id in enchantments.items():
            if ench_id in ENCHANTMENTS:
                for stat, val in ENCHANTMENTS[ench_id]["stats"].items():
                    if stat in stats:
                        stats[stat] += val

    # Пассивка
    if passive_id and passive_id in PASSIVES:
        bonus = PASSIVES[passive_id]["stat_bonus"]
        if "hp_pct" in bonus:
            stats["hp"] = int(stats["hp"] * (1 + bonus["hp_pct"]))
        if "atk_pct" in bonus:
            stats["atk"] = int(stats["atk"] * (1 + bonus["atk_pct"]))
        if "def_pct" in bonus:
            stats["def"] = int(stats["def"] * (1 + bonus["def_pct"]))
        for k in ("dodge", "foresight", "counter", "crit_chance",
                  "accuracy", "crit_power"):
            if k in bonus:
                stats[k] += bonus[k]

    # Округление и ограничения
    for k in ("crit_chance", "foresight", "dodge", "counter", "accuracy"):
        stats[k] = round(stats[k], 1)
    for k in ("hp", "atk", "def", "crit_power"):
        stats[k] = int(stats[k])

    stats["hp"]          = max(1,   stats["hp"])
    stats["atk"]         = max(1,   stats["atk"])
    stats["def"]         = max(0,   stats["def"])
    stats["accuracy"]    = min(98,  max(20, stats["accuracy"]))
    stats["dodge"]       = min(55,  max(0,  stats["dodge"]))
    stats["crit_chance"] = min(70,  max(0,  stats["crit_chance"]))
    stats["foresight"]   = min(40,  max(0,  stats["foresight"]))
    stats["counter"]     = min(35,  max(0,  stats["counter"]))
    stats["crit_power"]  = min(400, max(110,stats["crit_power"]))

    return stats, skills


def def_reduction(def_val: int) -> float:
    return def_val / (def_val + 50)


def get_rank(mmr: int) -> str:
    from config import RANKS
    rank = RANKS[0][1]
    for threshold, name in RANKS:
        if mmr >= threshold:
            rank = name
    return rank


def stats_text(stats: dict, skills: dict) -> str:
    dr = round(def_reduction(stats["def"]) * 100, 1)
    return (
        f"❤️ Здоровье: *{stats['hp']}*\n"
        f"🗡 Атака: *{stats['atk']}*\n"
        f"🔰 Защита: *{stats['def']}* _(-{dr}% урона)_\n"
        f"🥊 Крит: *{stats['crit_chance']}%*\n"
        f"💥 Сила крита: *{stats['crit_power']}%*\n"
        f"👁 Предвидение: *{stats['foresight']}%*\n"
        f"⚡️ Уворот: *{stats['dodge']}%*\n"
        f"🤺 Контрудар: *{stats['counter']}%*\n"
        f"🎯 Точность: *{stats['accuracy']}%*\n\n"
        f"*Навыки:*\n"
        f"✊ Сила: *{skills['strength']}*  "
        f"♥️ Выносливость: *{skills['endurance']}*\n"
        f"💫 Ловкость: *{skills['agility']}*  "
        f"🧿 Интуиция: *{skills['intuition']}*"
    )


# ─── УНИКАЛЬНЫЕ КРАФТОВЫЕ ПРЕДМЕТЫ ────────────────────────────────────────────
# Получить ТОЛЬКО через крафт, нельзя купить или дропнуть
# Тир 1 (1-10):   Новичок познаёт силу
# Тир 2 (11-20):  Воин набирает мощь
# Тир 3 (21-30):  Мастер боя
# Тир 4 (31-40):  Легендарный путь
# Тир 5 (41-50):  Абсолютная сила

CRAFT_ONLY_ITEMS = {

    # ══════════════════════════════════════════════════════════════════════════
    # ТИР 1 — УРОВНИ 1-10 — «Первые шаги»
    # ══════════════════════════════════════════════════════════════════════════

    # Оружие
    "bone_dagger": {
        "name": "🦴 Костяной кинжал", "slot": "weapon",
        "desc": "Скован из костей первого врага. Острее чем кажется.",
        "req_level": 1, "price": 0, "craft_only": True,
        "stats": {"atk": 12, "crit_chance": 5, "accuracy": 5},
        "scale_per_level": {"atk": 1.2, "crit_chance": 0.3},
    },
    "rusted_cleaver": {
        "name": "🗡️ Ржавый тесак", "slot": "weapon",
        "desc": "Грубый, но мощный. Наносит рваные раны.",
        "req_level": 3, "price": 0, "craft_only": True,
        "stats": {"atk": 18, "crit_power": 25, "accuracy": -3},
        "scale_per_level": {"atk": 1.5, "crit_power": 1.5},
    },
    "soldiers_sword": {
        "name": "⚔️ Меч солдата", "slot": "weapon",
        "desc": "Простой, надёжный меч ветерана. Никогда не подводит.",
        "req_level": 5, "price": 0, "craft_only": True,
        "stats": {"atk": 22, "accuracy": 6, "def": 3},
        "scale_per_level": {"atk": 2.0, "accuracy": 0.3, "def": 0.3},
    },
    "hunters_bow_blade": {
        "name": "🏹 Клинок охотника", "slot": "weapon",
        "desc": "Изогнутый как лук — быстрый и смертоносный.",
        "req_level": 8, "price": 0, "craft_only": True,
        "stats": {"atk": 20, "crit_chance": 10, "dodge": 5, "accuracy": 4},
        "scale_per_level": {"atk": 1.8, "crit_chance": 0.4},
    },

    # Броня
    "bone_armor": {
        "name": "🦴 Костяная броня", "slot": "armor",
        "desc": "Сделана из останков поверженных врагов. Пугает противников.",
        "req_level": 2, "price": 0, "craft_only": True,
        "stats": {"def": 8, "hp": 30, "counter": 3},
        "scale_per_level": {"def": 1.0, "hp": 5, "counter": 0.2},
    },
    "scout_vest": {
        "name": "🧥 Жилет разведчика", "slot": "armor",
        "desc": "Лёгкий и незаметный. Идеал для быстрых атак.",
        "req_level": 6, "price": 0, "craft_only": True,
        "stats": {"def": 10, "dodge": 8, "hp": 35, "accuracy": 3},
        "scale_per_level": {"def": 1.0, "dodge": 0.4, "hp": 5},
    },

    # Шлем
    "iron_crown": {
        "name": "👑 Железный венец", "slot": "helmet",
        "desc": "Не королевский, но сделан с гордостью.",
        "req_level": 4, "price": 0, "craft_only": True,
        "stats": {"def": 6, "hp": 22, "atk": 4},
        "scale_per_level": {"def": 0.7, "hp": 4, "atk": 0.4},
    },
    "shadow_hood": {
        "name": "🌑 Капюшон тени", "slot": "helmet",
        "desc": "Скрывает лицо. Враги не видят твоих глаз.",
        "req_level": 7, "price": 0, "craft_only": True,
        "stats": {"dodge": 6, "foresight": 5, "hp": 20},
        "scale_per_level": {"dodge": 0.4, "foresight": 0.3, "hp": 4},
    },

    # Сапоги
    "traveler_boots": {
        "name": "👢 Сапоги странника", "slot": "boots",
        "desc": "Тысячи миль пройдено. Не износятся никогда.",
        "req_level": 3, "price": 0, "craft_only": True,
        "stats": {"dodge": 6, "accuracy": 5, "hp": 15},
        "scale_per_level": {"dodge": 0.4, "accuracy": 0.3},
    },
    "swift_sandals": {
        "name": "⚡ Быстрые сандалии", "slot": "boots",
        "desc": "Почти невесомые. Скорость превыше всего.",
        "req_level": 6, "price": 0, "craft_only": True,
        "stats": {"dodge": 10, "accuracy": 7, "crit_chance": 3},
        "scale_per_level": {"dodge": 0.5, "accuracy": 0.4, "crit_chance": 0.2},
    },

    # Кольцо
    "blood_ring": {
        "name": "💢 Кольцо крови", "slot": "ring",
        "desc": "Пропитано кровью врагов. Даёт жажду боя.",
        "req_level": 4, "price": 0, "craft_only": True,
        "stats": {"atk": 7, "crit_chance": 4, "hp": 15},
        "scale_per_level": {"atk": 0.6, "crit_chance": 0.3},
    },
    "bone_ring": {
        "name": "🦴 Костяное кольцо", "slot": "ring",
        "desc": "Из кости дракона-детёныша. Хрупкое но магическое.",
        "req_level": 8, "price": 0, "craft_only": True,
        "stats": {"foresight": 8, "counter": 5, "hp": 20},
        "scale_per_level": {"foresight": 0.5, "counter": 0.3},
    },

    # Амулет
    "warrior_pendant": {
        "name": "⚔️ Кулон воина", "slot": "amulet",
        "desc": "Первый трофей. Символ начала пути.",
        "req_level": 2, "price": 0, "craft_only": True,
        "stats": {"atk": 8, "hp": 25},
        "scale_per_level": {"atk": 0.7, "hp": 5},
    },
    "shard_amulet": {
        "name": "💎 Амулет осколка", "slot": "amulet",
        "desc": "Осколок кристалла маны. Мерцает в темноте.",
        "req_level": 6, "price": 0, "craft_only": True,
        "stats": {"foresight": 6, "crit_power": 15, "hp": 30},
        "scale_per_level": {"foresight": 0.4, "crit_power": 1.0, "hp": 5},
    },

    # ══════════════════════════════════════════════════════════════════════════
    # ТИР 2 — УРОВНИ 11-20 — «Путь воина»
    # ══════════════════════════════════════════════════════════════════════════

    # Оружие
    "cursed_blade": {
        "name": "💀 Проклятый клинок", "slot": "weapon",
        "desc": "Несёт проклятие павших. Режет саму судьбу.",
        "req_level": 11, "price": 0, "craft_only": True,
        "stats": {"atk": 38, "crit_chance": 9, "crit_power": 30, "accuracy": -4},
        "scale_per_level": {"atk": 3.0, "crit_chance": 0.4, "crit_power": 1.5},
    },
    "venom_fang": {
        "name": "🐍 Ядовитый клык", "slot": "weapon",
        "desc": "Каждый удар отравляет противника медленной тоской.",
        "req_level": 13, "price": 0, "craft_only": True,
        "stats": {"atk": 32, "dodge": 6, "counter": 8, "crit_chance": 7},
        "scale_per_level": {"atk": 2.5, "dodge": 0.4, "counter": 0.4},
    },
    "storm_axe": {
        "name": "⛈️ Топор бури", "slot": "weapon",
        "desc": "Свистит как ветер. Удар сотрясает землю.",
        "req_level": 15, "price": 0, "craft_only": True,
        "stats": {"atk": 50, "crit_power": 45, "def": 6, "accuracy": -6},
        "scale_per_level": {"atk": 3.5, "crit_power": 2.0, "def": 0.4},
    },
    "soul_reaper": {
        "name": "☠️ Жнец душ", "slot": "weapon",
        "desc": "Коса смерти в человеческих руках. Наводит ужас.",
        "req_level": 18, "price": 0, "craft_only": True,
        "stats": {"atk": 55, "crit_chance": 13, "crit_power": 35, "foresight": 8},
        "scale_per_level": {"atk": 4.0, "crit_chance": 0.5, "crit_power": 2.0},
    },

    # Броня
    "cursed_armor": {
        "name": "💀 Проклятая броня", "slot": "armor",
        "desc": "Снять невозможно. Носящий становится сильнее с каждым боем.",
        "req_level": 11, "price": 0, "craft_only": True,
        "stats": {"def": 20, "hp": 80, "atk": 8, "dodge": -3},
        "scale_per_level": {"def": 2.0, "hp": 12, "atk": 0.5},
    },
    "storm_mail": {
        "name": "⛈️ Броня бури", "slot": "armor",
        "desc": "Пропитана молниями. Разряжает удары.",
        "req_level": 14, "price": 0, "craft_only": True,
        "stats": {"def": 25, "hp": 95, "counter": 10},
        "scale_per_level": {"def": 2.2, "hp": 13, "counter": 0.5},
    },
    "berserker_hide": {
        "name": "💢 Шкура берсерка", "slot": "armor",
        "desc": "Звериная шкура. Делает носящего диким и непредсказуемым.",
        "req_level": 16, "price": 0, "craft_only": True,
        "stats": {"def": 18, "hp": 90, "atk": 15, "crit_power": 20},
        "scale_per_level": {"def": 1.8, "hp": 12, "atk": 1.0, "crit_power": 1.0},
    },
    "mage_robe": {
        "name": "🔮 Мантия мага", "slot": "armor",
        "desc": "Соткана из заклинаний. Предвидит каждый удар.",
        "req_level": 17, "price": 0, "craft_only": True,
        "stats": {"def": 16, "hp": 85, "foresight": 15, "counter": 12},
        "scale_per_level": {"def": 1.5, "hp": 10, "foresight": 0.7, "counter": 0.5},
    },

    # Шлем
    "cursed_helm": {
        "name": "💀 Проклятый шлем", "slot": "helmet",
        "desc": "Шёпот мёртвых даёт предвидение.",
        "req_level": 12, "price": 0, "craft_only": True,
        "stats": {"def": 14, "hp": 50, "foresight": 8},
        "scale_per_level": {"def": 1.2, "hp": 7, "foresight": 0.4},
    },
    "berserker_skull": {
        "name": "💢 Череп берсерка", "slot": "helmet",
        "desc": "Надевая его — забываешь страх и боль.",
        "req_level": 16, "price": 0, "craft_only": True,
        "stats": {"def": 12, "hp": 45, "atk": 12, "crit_power": 18},
        "scale_per_level": {"def": 1.0, "hp": 6, "atk": 0.8, "crit_power": 1.0},
    },

    # Сапоги
    "storm_boots": {
        "name": "⛈️ Сапоги бури", "slot": "boots",
        "desc": "Оставляют след молний. Не знают усталости.",
        "req_level": 13, "price": 0, "craft_only": True,
        "stats": {"dodge": 14, "accuracy": 10, "def": 5},
        "scale_per_level": {"dodge": 0.6, "accuracy": 0.5, "def": 0.4},
    },
    "shadow_dancer": {
        "name": "🌑 Танцор теней", "slot": "boots",
        "desc": "Движения неуловимы как тень в ночи.",
        "req_level": 17, "price": 0, "craft_only": True,
        "stats": {"dodge": 20, "crit_chance": 7, "counter": 5},
        "scale_per_level": {"dodge": 0.7, "crit_chance": 0.4, "counter": 0.3},
    },

    # Кольцо
    "cursed_ring": {
        "name": "💀 Проклятое кольцо", "slot": "ring",
        "desc": "Снять невозможно. Но носящий сильнее.",
        "req_level": 12, "price": 0, "craft_only": True,
        "stats": {"atk": 12, "crit_chance": 8, "crit_power": 20},
        "scale_per_level": {"atk": 0.8, "crit_chance": 0.4, "crit_power": 1.0},
    },
    "storm_ring": {
        "name": "⛈️ Кольцо бури", "slot": "ring",
        "desc": "Гром в кулаке. Удары звенят как гром.",
        "req_level": 16, "price": 0, "craft_only": True,
        "stats": {"atk": 15, "crit_power": 30, "accuracy": 6},
        "scale_per_level": {"atk": 1.0, "crit_power": 1.5, "accuracy": 0.3},
    },

    # Амулет
    "soul_stone": {
        "name": "☠️ Камень душ", "slot": "amulet",
        "desc": "Хранит души всех кого ты победил.",
        "req_level": 14, "price": 0, "craft_only": True,
        "stats": {"hp": 100, "atk": 10, "foresight": 8},
        "scale_per_level": {"hp": 12, "atk": 0.8, "foresight": 0.4},
    },
    "storm_heart": {
        "name": "⛈️ Сердце бури", "slot": "amulet",
        "desc": "Бьётся как гром. Заряжает тело энергией.",
        "req_level": 18, "price": 0, "craft_only": True,
        "stats": {"hp": 120, "atk": 14, "crit_chance": 6, "counter": 8},
        "scale_per_level": {"hp": 14, "atk": 1.0, "crit_chance": 0.3, "counter": 0.4},
    },

    # ══════════════════════════════════════════════════════════════════════════
    # ТИР 3 — УРОВНИ 21-30 — «Мастер арены»
    # ══════════════════════════════════════════════════════════════════════════

    # Оружие
    "void_reaper": {
        "name": "🌀 Жнец пустоты", "slot": "weapon",
        "desc": "Рассекает само пространство. Удар из ниоткуда.",
        "req_level": 21, "price": 0, "craft_only": True,
        "stats": {"atk": 70, "crit_chance": 15, "crit_power": 45, "dodge": 5},
        "scale_per_level": {"atk": 5.0, "crit_chance": 0.5, "crit_power": 2.5},
    },
    "titan_blade": {
        "name": "⚙️ Клинок титана", "slot": "weapon",
        "desc": "Тяжёлый как гора. Один удар решает всё.",
        "req_level": 23, "price": 0, "craft_only": True,
        "stats": {"atk": 85, "crit_power": 60, "def": 12, "accuracy": -5},
        "scale_per_level": {"atk": 5.5, "crit_power": 3.0, "def": 0.8},
    },
    "eclipse_sword": {
        "name": "🌑 Меч затмения", "slot": "weapon",
        "desc": "Поглощает свет вокруг. Удар — как сама тьма.",
        "req_level": 25, "price": 0, "craft_only": True,
        "stats": {"atk": 75, "crit_chance": 18, "dodge": 8, "foresight": 10},
        "scale_per_level": {"atk": 5.0, "crit_chance": 0.6, "dodge": 0.5},
    },
    "inferno_axe": {
        "name": "🔥 Топор инферно", "slot": "weapon",
        "desc": "Горит даже в воде. Не гаснет никогда.",
        "req_level": 27, "price": 0, "craft_only": True,
        "stats": {"atk": 90, "crit_power": 55, "crit_chance": 10, "accuracy": -8},
        "scale_per_level": {"atk": 6.0, "crit_power": 3.5, "crit_chance": 0.4},
    },

    # Броня
    "void_armor": {
        "name": "🌀 Доспех пустоты", "slot": "armor",
        "desc": "Создан из материи самой пустоты. Поглощает урон.",
        "req_level": 21, "price": 0, "craft_only": True,
        "stats": {"def": 65, "hp": 260, "foresight": 14, "dodge": 6},
        "scale_per_level": {"def": 4.0, "hp": 22, "foresight": 0.6},
    },
    "titan_fortress": {
        "name": "⚙️ Крепость титана", "slot": "armor",
        "desc": "Не броня — крепость. Никто не пробьёт.",
        "req_level": 24, "price": 0, "craft_only": True,
        "stats": {"def": 80, "hp": 300, "counter": 12, "dodge": -5},
        "scale_per_level": {"def": 5.0, "hp": 25, "counter": 0.6},
    },
    "eclipse_cloak": {
        "name": "🌑 Плащ затмения", "slot": "armor",
        "desc": "Ты исчезаешь в тени. Только удар выдаёт тебя.",
        "req_level": 26, "price": 0, "craft_only": True,
        "stats": {"def": 45, "hp": 220, "dodge": 20, "crit_chance": 8},
        "scale_per_level": {"def": 3.0, "hp": 18, "dodge": 0.8, "crit_chance": 0.3},
    },
    "inferno_plate": {
        "name": "🔥 Латы инферно", "slot": "armor",
        "desc": "Раскалены изнутри. Враги обжигаются при ударе.",
        "req_level": 28, "price": 0, "craft_only": True,
        "stats": {"def": 70, "hp": 280, "counter": 15, "atk": 12},
        "scale_per_level": {"def": 4.5, "hp": 22, "counter": 0.7, "atk": 0.6},
    },

    # Шлем
    "void_crown": {
        "name": "🌀 Корона пустоты", "slot": "helmet",
        "desc": "Даёт предвидение и власть над пространством.",
        "req_level": 22, "price": 0, "craft_only": True,
        "stats": {"def": 22, "hp": 85, "foresight": 18, "counter": 10},
        "scale_per_level": {"def": 1.8, "hp": 10, "foresight": 0.8, "counter": 0.5},
    },
    "inferno_helm": {
        "name": "🔥 Шлем инферно", "slot": "helmet",
        "desc": "Пылает как солнце. Защищает разум от страха.",
        "req_level": 26, "price": 0, "craft_only": True,
        "stats": {"def": 28, "hp": 100, "atk": 16, "crit_power": 22},
        "scale_per_level": {"def": 2.2, "hp": 12, "atk": 1.0, "crit_power": 1.2},
    },

    # Сапоги
    "void_walker": {
        "name": "🌀 Ходок пустоты", "slot": "boots",
        "desc": "Шагает сквозь пространство. Уворот почти абсолютный.",
        "req_level": 22, "price": 0, "craft_only": True,
        "stats": {"dodge": 28, "accuracy": 12, "crit_chance": 6},
        "scale_per_level": {"dodge": 0.9, "accuracy": 0.5, "crit_chance": 0.3},
    },
    "titan_stompers": {
        "name": "⚙️ Поступь титана", "slot": "boots",
        "desc": "Земля трясётся под каждым шагом.",
        "req_level": 27, "price": 0, "craft_only": True,
        "stats": {"def": 16, "hp": 70, "counter": 10, "accuracy": 8},
        "scale_per_level": {"def": 1.2, "hp": 8, "counter": 0.5, "accuracy": 0.4},
    },

    # Кольцо
    "void_sigil": {
        "name": "🌀 Перстень пустоты", "slot": "ring",
        "desc": "Печать самой пустоты. Притягивает силу.",
        "req_level": 23, "price": 0, "craft_only": True,
        "stats": {"atk": 18, "crit_chance": 12, "foresight": 10},
        "scale_per_level": {"atk": 1.2, "crit_chance": 0.5, "foresight": 0.5},
    },
    "inferno_seal": {
        "name": "🔥 Печать инферно", "slot": "ring",
        "desc": "Обжигает при рукопожатии. Мощь огня в кольце.",
        "req_level": 28, "price": 0, "craft_only": True,
        "stats": {"atk": 22, "crit_power": 40, "crit_chance": 10},
        "scale_per_level": {"atk": 1.5, "crit_power": 2.0, "crit_chance": 0.4},
    },

    # Амулет
    "void_eye": {
        "name": "🌀 Глаз пустоты", "slot": "amulet",
        "desc": "Видит врагов насквозь. Предвидит каждый удар.",
        "req_level": 24, "price": 0, "craft_only": True,
        "stats": {"foresight": 22, "counter": 15, "hp": 140},
        "scale_per_level": {"foresight": 0.9, "counter": 0.6, "hp": 14},
    },
    "inferno_core": {
        "name": "🔥 Ядро инферно", "slot": "amulet",
        "desc": "Горит внутри тела. Придаёт нечеловеческую силу.",
        "req_level": 28, "price": 0, "craft_only": True,
        "stats": {"hp": 160, "atk": 20, "crit_power": 35, "def": 12},
        "scale_per_level": {"hp": 16, "atk": 1.5, "crit_power": 2.0, "def": 0.8},
    },

    # ══════════════════════════════════════════════════════════════════════════
    # ТИР 4 — УРОВНИ 31-40 — «Легендарный путь»
    # ══════════════════════════════════════════════════════════════════════════

    # Оружие
    "celestial_blade": {
        "name": "✨ Небесный клинок", "slot": "weapon",
        "desc": "Упал с небес. Несёт в себе звёздный свет.",
        "req_level": 31, "price": 0, "craft_only": True,
        "stats": {"atk": 100, "crit_chance": 20, "crit_power": 60, "accuracy": 8},
        "scale_per_level": {"atk": 6.0, "crit_chance": 0.6, "crit_power": 3.0},
    },
    "abyssal_scythe": {
        "name": "🌊 Коса бездны", "slot": "weapon",
        "desc": "Из глубин океана. Тянет врагов в пучину.",
        "req_level": 34, "price": 0, "craft_only": True,
        "stats": {"atk": 110, "crit_power": 70, "dodge": 10, "foresight": 12},
        "scale_per_level": {"atk": 6.5, "crit_power": 3.5, "dodge": 0.5},
    },
    "chaos_sword": {
        "name": "🌪️ Меч хаоса", "slot": "weapon",
        "desc": "Непредсказуемый. Каждый удар другой силы.",
        "req_level": 36, "price": 0, "craft_only": True,
        "stats": {"atk": 95, "crit_chance": 22, "crit_power": 65, "counter": 12},
        "scale_per_level": {"atk": 6.0, "crit_chance": 0.7, "crit_power": 3.5},
    },
    "god_slayer": {
        "name": "⚡ Убийца богов", "slot": "weapon",
        "desc": "Создан чтобы убивать бессмертных. Никто не устоит.",
        "req_level": 39, "price": 0, "craft_only": True,
        "stats": {"atk": 125, "crit_chance": 18, "crit_power": 75, "accuracy": 10},
        "scale_per_level": {"atk": 7.0, "crit_chance": 0.6, "crit_power": 4.0},
    },

    # Броня
    "celestial_plate": {
        "name": "✨ Небесные латы", "slot": "armor",
        "desc": "Сотканы из звёздного металла. Почти невесомые.",
        "req_level": 31, "price": 0, "craft_only": True,
        "stats": {"def": 90, "hp": 350, "dodge": 8, "foresight": 15},
        "scale_per_level": {"def": 5.5, "hp": 28, "foresight": 0.7},
    },
    "abyssal_shell": {
        "name": "🌊 Панцирь бездны", "slot": "armor",
        "desc": "Давление глубин сделало его нерушимым.",
        "req_level": 34, "price": 0, "craft_only": True,
        "stats": {"def": 100, "hp": 380, "counter": 18},
        "scale_per_level": {"def": 6.0, "hp": 30, "counter": 0.8},
    },
    "chaos_hide": {
        "name": "🌪️ Шкура хаоса", "slot": "armor",
        "desc": "Сделана из существа хаоса. Непредсказуемая защита.",
        "req_level": 37, "price": 0, "craft_only": True,
        "stats": {"def": 80, "hp": 340, "dodge": 15, "counter": 15, "atk": 15},
        "scale_per_level": {"def": 5.0, "hp": 26, "dodge": 0.6, "counter": 0.6},
    },

    # Шлем
    "celestial_crown": {
        "name": "✨ Небесная корона", "slot": "helmet",
        "desc": "Корона звёзд. Даёт мудрость богов.",
        "req_level": 32, "price": 0, "craft_only": True,
        "stats": {"def": 35, "hp": 130, "foresight": 22, "atk": 18},
        "scale_per_level": {"def": 2.5, "hp": 14, "foresight": 1.0, "atk": 1.0},
    },
    "chaos_mask": {
        "name": "🌪️ Маска хаоса", "slot": "helmet",
        "desc": "Носящий её сам становится воплощением хаоса.",
        "req_level": 37, "price": 0, "craft_only": True,
        "stats": {"def": 30, "hp": 120, "crit_chance": 14, "crit_power": 28},
        "scale_per_level": {"def": 2.2, "hp": 12, "crit_chance": 0.6, "crit_power": 1.5},
    },

    # Сапоги
    "celestial_steps": {
        "name": "✨ Небесная поступь", "slot": "boots",
        "desc": "Ходит по воздуху. Уворот на грани магии.",
        "req_level": 33, "price": 0, "craft_only": True,
        "stats": {"dodge": 32, "accuracy": 14, "hp": 60},
        "scale_per_level": {"dodge": 1.0, "accuracy": 0.6, "hp": 7},
    },
    "abyssal_treads": {
        "name": "🌊 Ступни бездны", "slot": "boots",
        "desc": "Тянут врагов вниз контрударом после каждого шага.",
        "req_level": 37, "price": 0, "craft_only": True,
        "stats": {"def": 18, "hp": 80, "counter": 14, "dodge": 10},
        "scale_per_level": {"def": 1.5, "hp": 9, "counter": 0.7, "dodge": 0.5},
    },

    # Кольцо
    "celestial_band": {
        "name": "✨ Небесный обруч", "slot": "ring",
        "desc": "Кольцо из застывшего звёздного света.",
        "req_level": 33, "price": 0, "craft_only": True,
        "stats": {"atk": 25, "crit_chance": 14, "crit_power": 35, "hp": 40},
        "scale_per_level": {"atk": 1.8, "crit_chance": 0.6, "crit_power": 2.0},
    },
    "chaos_signet": {
        "name": "🌪️ Перстень хаоса", "slot": "ring",
        "desc": "Пульсирует энергией хаоса. Непредсказуемая мощь.",
        "req_level": 38, "price": 0, "craft_only": True,
        "stats": {"atk": 28, "crit_power": 50, "counter": 12, "foresight": 10},
        "scale_per_level": {"atk": 2.0, "crit_power": 2.5, "counter": 0.6},
    },

    # Амулет
    "star_fragment": {
        "name": "✨ Осколок звезды", "slot": "amulet",
        "desc": "Упал с небес тысячу лет назад. Хранит силу звезды.",
        "req_level": 32, "price": 0, "craft_only": True,
        "stats": {"hp": 200, "atk": 22, "foresight": 18, "crit_power": 28},
        "scale_per_level": {"hp": 20, "atk": 1.8, "foresight": 0.8, "crit_power": 1.5},
    },
    "abyss_heart": {
        "name": "🌊 Сердце бездны", "slot": "amulet",
        "desc": "Пульсирует из глубин. Даёт силу океана.",
        "req_level": 38, "price": 0, "craft_only": True,
        "stats": {"hp": 240, "def": 22, "counter": 18, "atk": 18},
        "scale_per_level": {"hp": 22, "def": 1.5, "counter": 0.8, "atk": 1.2},
    },

    # ══════════════════════════════════════════════════════════════════════════
    # ТИР 5 — УРОВНИ 41-50 — «Абсолютная сила»
    # ══════════════════════════════════════════════════════════════════════════

    # Оружие
    "eternity_blade": {
        "name": "♾️ Клинок вечности", "slot": "weapon",
        "desc": "Существует вне времени. Убивает прошлое и будущее.",
        "req_level": 41, "price": 0, "craft_only": True,
        "stats": {"atk": 145, "crit_chance": 25, "crit_power": 80, "accuracy": 12},
        "scale_per_level": {"atk": 8.0, "crit_chance": 0.8, "crit_power": 4.0},
    },
    "world_ender": {
        "name": "💥 Конец света", "slot": "weapon",
        "desc": "Последнее оружие. Тот кто держит его — решает судьбы.",
        "req_level": 44, "price": 0, "craft_only": True,
        "stats": {"atk": 160, "crit_power": 90, "crit_chance": 20, "accuracy": -10},
        "scale_per_level": {"atk": 9.0, "crit_power": 5.0, "crit_chance": 0.5},
    },
    "genesis_spear": {
        "name": "🌟 Копьё Генезиса", "slot": "weapon",
        "desc": "Первое оружие созданное в начале времён.",
        "req_level": 46, "price": 0, "craft_only": True,
        "stats": {"atk": 150, "crit_chance": 28, "dodge": 12, "foresight": 15},
        "scale_per_level": {"atk": 8.5, "crit_chance": 0.9, "dodge": 0.6},
    },
    "omega_scythe": {
        "name": "Ω Коса Омега", "slot": "weapon",
        "desc": "Альфа и омега. Начало и конец всего. Абсолютная сила.",
        "req_level": 49, "price": 0, "craft_only": True,
        "stats": {"atk": 180, "crit_chance": 30, "crit_power": 100, "accuracy": 5, "dodge": 10},
        "scale_per_level": {"atk": 10.0, "crit_chance": 1.0, "crit_power": 5.0},
    },

    # Броня
    "eternity_armor": {
        "name": "♾️ Доспех вечности", "slot": "armor",
        "desc": "Нерушимый. Существует пока существует носящий.",
        "req_level": 41, "price": 0, "craft_only": True,
        "stats": {"def": 120, "hp": 450, "foresight": 20, "counter": 20},
        "scale_per_level": {"def": 7.0, "hp": 35, "foresight": 0.8, "counter": 0.8},
    },
    "world_shell": {
        "name": "💥 Панцирь мира", "slot": "armor",
        "desc": "Выкован из останков мира. Поглощает любой урон.",
        "req_level": 45, "price": 0, "craft_only": True,
        "stats": {"def": 140, "hp": 500, "counter": 25, "dodge": -8},
        "scale_per_level": {"def": 8.0, "hp": 40, "counter": 1.0},
    },
    "genesis_robe": {
        "name": "🌟 Мантия Генезиса", "slot": "armor",
        "desc": "Сотканна из первозданного света. Идеальная защита.",
        "req_level": 47, "price": 0, "craft_only": True,
        "stats": {"def": 110, "hp": 480, "dodge": 22, "foresight": 25},
        "scale_per_level": {"def": 7.0, "hp": 38, "dodge": 0.8, "foresight": 1.0},
    },
    "omega_fortress": {
        "name": "Ω Крепость Омега", "slot": "armor",
        "desc": "Финальная броня. Тот кто носит её — непобедим.",
        "req_level": 50, "price": 0, "craft_only": True,
        "stats": {"def": 160, "hp": 600, "counter": 30, "foresight": 22, "atk": 25},
        "scale_per_level": {"def": 0, "hp": 0},  # Макс уровень
    },

    # Шлем
    "eternity_crown": {
        "name": "♾️ Корона вечности", "slot": "helmet",
        "desc": "Правит не народами — самой вечностью.",
        "req_level": 42, "price": 0, "craft_only": True,
        "stats": {"def": 45, "hp": 180, "foresight": 28, "atk": 22},
        "scale_per_level": {"def": 3.0, "hp": 16, "foresight": 1.2, "atk": 1.2},
    },
    "omega_helm": {
        "name": "Ω Шлем Омега", "slot": "helmet",
        "desc": "Финальный шлем. Разум острее лезвия.",
        "req_level": 48, "price": 0, "craft_only": True,
        "stats": {"def": 50, "hp": 200, "crit_chance": 18, "crit_power": 40, "foresight": 20},
        "scale_per_level": {"def": 3.5, "hp": 18, "crit_chance": 0.8, "crit_power": 2.0},
    },

    # Сапоги
    "eternity_steps": {
        "name": "♾️ Шаги вечности", "slot": "boots",
        "desc": "Ходит по времени. Уворот вне физики.",
        "req_level": 42, "price": 0, "craft_only": True,
        "stats": {"dodge": 40, "accuracy": 18, "crit_chance": 10},
        "scale_per_level": {"dodge": 1.2, "accuracy": 0.7, "crit_chance": 0.4},
    },
    "omega_treads": {
        "name": "Ω Поступь Омега", "slot": "boots",
        "desc": "Финальные сапоги. Каждый шаг — как гром богов.",
        "req_level": 48, "price": 0, "craft_only": True,
        "stats": {"dodge": 45, "counter": 20, "def": 22, "accuracy": 15},
        "scale_per_level": {"dodge": 1.5, "counter": 1.0, "def": 1.5},
    },

    # Кольцо
    "eternity_ring": {
        "name": "♾️ Кольцо вечности", "slot": "ring",
        "desc": "Не имеет начала и конца. Как сама сила.",
        "req_level": 43, "price": 0, "craft_only": True,
        "stats": {"atk": 35, "crit_chance": 18, "crit_power": 50, "hp": 60},
        "scale_per_level": {"atk": 2.5, "crit_chance": 0.8, "crit_power": 3.0},
    },
    "omega_signet": {
        "name": "Ω Перстень Омега", "slot": "ring",
        "desc": "Финальная печать. Всё заканчивается здесь.",
        "req_level": 49, "price": 0, "craft_only": True,
        "stats": {"atk": 40, "crit_power": 70, "counter": 18, "crit_chance": 20},
        "scale_per_level": {"atk": 3.0, "crit_power": 4.0, "counter": 1.0},
    },

    # Амулет
    "eternity_core": {
        "name": "♾️ Ядро вечности", "slot": "amulet",
        "desc": "Пульсирует вечностью. Нет ничего сильнее.",
        "req_level": 43, "price": 0, "craft_only": True,
        "stats": {"hp": 300, "atk": 28, "def": 25, "foresight": 22},
        "scale_per_level": {"hp": 25, "atk": 2.0, "def": 1.5, "foresight": 1.0},
    },
    "omega_heart": {
        "name": "Ω Сердце Омега", "slot": "amulet",
        "desc": "Финальный артефакт. Носящий его — абсолютный чемпион Арены.",
        "req_level": 50, "price": 0, "craft_only": True,
        "stats": {"hp": 400, "atk": 35, "def": 30, "crit_power": 60, "counter": 25, "foresight": 25},
        "scale_per_level": {"hp": 0, "atk": 0},  # Макс уровень
    },
}

# Добавляем крафтовые предметы в общий словарь ITEMS
ITEMS.update(CRAFT_ONLY_ITEMS)


# ═══════════════════════════════════════════════════════════════════════════
# ЭКСКЛЮЗИВНЫЕ КРАФТОВЫЕ ПРЕДМЕТЫ
# Недоступны в магазине — только через /craft
# По одному уникальному предмету на каждый диапазон уровней
# ═══════════════════════════════════════════════════════════════════════════

CRAFT_ONLY_ITEMS = {
    # ── Ур.1-5 — Клык новичка ────────────────────────────────────────────────
    "novice_fang": {
        "name": "🦷 Клык новичка", "slot": "weapon",
        "desc": "Зачарованный клык первого поверженного зверя. Только для крафта.",
        "req_level": 1, "price": 0, "craft_only": True,
        "stats": {"atk": 14, "crit_chance": 5, "accuracy": 4},
        "scale_per_level": {"atk": 1.5, "crit_chance": 0.3},
    },

    # ── Ур.5-10 — Перчатка первого боя ───────────────────────────────────────
    "first_blood_gauntlet": {
        "name": "🥊 Перчатка Первой крови", "slot": "ring",
        "desc": "Хранит память о первой победе на арене.",
        "req_level": 5, "price": 0, "craft_only": True,
        "stats": {"atk": 10, "crit_power": 22, "counter": 4},
        "scale_per_level": {"atk": 0.8, "crit_power": 1.0},
    },

    # ── Ур.10-15 — Сердце волка ──────────────────────────────────────────────
    "wolf_heart": {
        "name": "🐺 Сердце волка", "slot": "amulet",
        "desc": "Бьётся в груди — даёт нюх на слабости врага.",
        "req_level": 10, "price": 0, "craft_only": True,
        "stats": {"hp": 90, "dodge": 8, "foresight": 6},
        "scale_per_level": {"hp": 8, "dodge": 0.4},
    },

    # ── Ур.15-20 — Маска палача ──────────────────────────────────────────────
    "executioner_mask": {
        "name": "💀 Маска палача", "slot": "helmet",
        "desc": "Видевшая сотни казней. Внушает страх.",
        "req_level": 15, "price": 0, "craft_only": True,
        "stats": {"def": 20, "hp": 80, "crit_power": 25, "counter": 5},
        "scale_per_level": {"def": 1.8, "hp": 10, "crit_power": 1.2},
    },

    # ── Ур.20-25 — Кираса бури ───────────────────────────────────────────────
    "storm_cuirass": {
        "name": "⛈️ Кираса бури", "slot": "armor",
        "desc": "Притягивает молнии, отталкивает удары.",
        "req_level": 20, "price": 0, "craft_only": True,
        "stats": {"def": 35, "hp": 150, "dodge": 8, "counter": 6},
        "scale_per_level": {"def": 2.2, "hp": 14, "dodge": 0.3},
    },

    # ── Ур.25-30 — Сапоги пожирателя пути ────────────────────────────────────
    "pathdevourer_boots": {
        "name": "🌪️ Сапоги Пожирателя Пути", "slot": "boots",
        "desc": "Каждый шаг стирает границу между атакой и защитой.",
        "req_level": 25, "price": 0, "craft_only": True,
        "stats": {"dodge": 25, "accuracy": 14, "def": 10, "hp": 50},
        "scale_per_level": {"dodge": 0.7, "accuracy": 0.5, "def": 0.6},
    },

    # ── Ур.30-35 — Клинок Бездны ─────────────────────────────────────────────
    "abyss_blade": {
        "name": "🌌 Клинок Бездны", "slot": "weapon",
        "desc": "Выкован из обломков уничтоженного мира.",
        "req_level": 30, "price": 0, "craft_only": True,
        "stats": {"atk": 70, "crit_chance": 16, "crit_power": 50, "accuracy": 6},
        "scale_per_level": {"atk": 4.5, "crit_chance": 0.4, "crit_power": 2.2},
    },

    # ── Ур.35-40 — Кольцо Вечного Пламени ────────────────────────────────────
    "eternal_flame_ring": {
        "name": "🔥 Кольцо Вечного Пламени", "slot": "ring",
        "desc": "Никогда не гаснет. Питает носителя силой.",
        "req_level": 35, "price": 0, "craft_only": True,
        "stats": {"atk": 25, "crit_power": 35, "hp": 100, "def": 15},
        "scale_per_level": {"atk": 1.8, "crit_power": 1.5, "hp": 8},
    },

    # ── Ур.40-45 — Корона Падшего Короля ─────────────────────────────────────
    "fallen_king_crown": {
        "name": "👑 Корона Падшего Короля", "slot": "helmet",
        "desc": "Венчала голову того, кто правил до Катастрофы.",
        "req_level": 40, "price": 0, "craft_only": True,
        "stats": {"def": 40, "hp": 180, "atk": 30, "foresight": 12, "counter": 8},
        "scale_per_level": {"def": 2.5, "hp": 16, "atk": 1.8},
    },

    # ── Ур.45-50 — Амулет Творца Миров ───────────────────────────────────────
    "worldmaker_amulet": {
        "name": "🌍 Амулет Творца Миров", "slot": "amulet",
        "desc": "Легендарный артефакт. Говорят, он способен переписывать судьбу.",
        "req_level": 45, "price": 0, "craft_only": True,
        "stats": {
            "hp": 280, "atk": 35, "def": 30,
            "crit_chance": 10, "crit_power": 40,
            "dodge": 10, "foresight": 15, "counter": 12,
        },
        "scale_per_level": {"hp": 20, "atk": 2.5, "def": 1.8, "crit_power": 2.0},
    },
}

# Объединяем с обычными ITEMS чтобы calc_stats видел все предметы
ITEMS.update(CRAFT_ONLY_ITEMS)
