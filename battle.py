"""
Боевая система Арены
- def реально снижает урон через формулу def/(def+50)
- Каждый класс имеет уникальное рабочее умение
- Контрудар — шанс ответного урона при defend/attack
- Предвидение — снижает входящий урон (% от foresight)
- Уворот работает всегда, с поправкой на defend
- Берсерк теряет защиту в ярости (реально применяется)
- Маг в умении удваивает предвидение и контрудар на раунд
- БОТЫ: 4 уровня сложности с тактическим ИИ
"""

import asyncio
import random
import copy
import time
import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes
from database import Database
from gamedata import CLASSES, ITEMS, calc_stats, def_reduction
from config import (
    ARENA_WIN_GOLD, ARENA_LOSS_GOLD,
    ARENA_WIN_EXP, ARENA_LOSS_EXP,
    EXP_BASE, EXP_SCALE, MAX_LEVEL, TURN_TIMEOUT,
    MMR_WIN, MMR_LOSS,
)

logger = logging.getLogger(__name__)
active_battles: dict[str, "BattleState"] = {}


def exp_for_level(lvl: int) -> int:
    return int(EXP_BASE * (lvl ** EXP_SCALE))


def _add_exp(player: dict, gain: int) -> tuple[int, bool]:
    if player["level"] >= MAX_LEVEL:
        return player["exp"], False
    new_exp = player["exp"] + gain
    needed  = exp_for_level(player["level"])
    if new_exp >= needed:
        return new_exp - needed, True
    return new_exp, False


# ═══════════════════════════════════════════════════════════════════════════
# СИСТЕМА БОТОВ — 4 уровня сложности
# ═══════════════════════════════════════════════════════════════════════════

BOT_NAMES = {
    "rookie": [
        "Слабый страж", "Деревенский забияка", "Юный рекрут",
        "Ученик арены", "Зелёный боец",
    ],
    "veteran": [
        "Закалённый воин", "Арена-Голем", "Красный клинок",
        "Опытный страж", "Боец гильдии",
    ],
    "elite": [
        "Хаос-Берсерк", "Призрак войны", "Стальной мститель",
        "Кровавый страж", "Чемпион арены",
    ],
    "nightmare": [
        "Пепельный король", "Владыка теней", "Разрушитель миров",
        "Древний страж", "Аватар Катастрофы",
    ],
}

# Множители силы бота относительно игрока
BOT_DIFFICULTY = {
    "rookie":    {"stat_mult": 0.85, "ai_skill": 0.3, "label": "🟢 Новичок"},
    "veteran":   {"stat_mult": 1.00, "ai_skill": 0.6, "label": "🟡 Ветеран"},
    "elite":     {"stat_mult": 1.15, "ai_skill": 0.85,"label": "🟠 Элита"},
    "nightmare": {"stat_mult": 1.30, "ai_skill": 1.0, "label": "🔴 Кошмар"},
}


def pick_bot_difficulty(player_level: int, player_streak: int = 0) -> str:
    """
    Выбрать сложность бота.
    На низких уровнях — легче, на высоких — сложнее.
    Винстрик игрока повышает шанс сложного бота (challenge scaling).
    """
    if player_level <= 5:
        weights = {"rookie": 70, "veteran": 30, "elite": 0, "nightmare": 0}
    elif player_level <= 15:
        weights = {"rookie": 30, "veteran": 50, "elite": 20, "nightmare": 0}
    elif player_level <= 30:
        weights = {"rookie": 10, "veteran": 35, "elite": 45, "nightmare": 10}
    else:
        weights = {"rookie": 5, "veteran": 20, "elite": 45, "nightmare": 30}

    # Длинный винстрик — повышаем шанс кошмарного бота
    if player_streak >= 5:
        weights["nightmare"] = weights.get("nightmare", 0) + 20
        weights["elite"]     = weights.get("elite", 0) + 10

    diffs = list(weights.keys())
    probs = [max(0, weights[d]) for d in diffs]
    total = sum(probs)
    if total == 0:
        return "veteran"
    probs = [p / total for p in probs]
    return random.choices(diffs, weights=probs, k=1)[0]


def make_bot_opponent(level: int, streak: int = 0) -> dict:
    difficulty = pick_bot_difficulty(level, streak)
    diff_data  = BOT_DIFFICULTY[difficulty]

    cls_id = random.choice(list(CLASSES.keys()))
    lvl    = max(1, level + random.randint(-1, 2))  # боты чуть выше уровнем
    stats, skills = calc_stats({"level": lvl, "class_id": cls_id}, {})

    mult = diff_data["stat_mult"]
    stats["hp"]          = int(stats["hp"] * mult)
    stats["atk"]         = int(stats["atk"] * mult)
    stats["def"]         = int(stats["def"] * mult)
    stats["crit_chance"] = min(70, stats["crit_chance"] * mult)
    stats["dodge"]       = min(55, stats["dodge"] * mult)

    name = random.choice(BOT_NAMES[difficulty])
    label = diff_data["label"]

    return {
        "first_name": f"🤖 {label} {name}",
        "class_id":   cls_id,
        "level":      lvl,
        "stats":      stats,
        "difficulty": difficulty,
        "ai_skill":   diff_data["ai_skill"],
    }


def bot_decide_action(bot_fighter: dict, opponent: dict) -> str:
    """
    Тактический ИИ бота.
    ai_skill (0.0-1.0) определяет насколько умно бот принимает решения:
    - Низкий skill: случайные действия
    - Высокий skill: реагирует на HP, использует контр-тактику
    """
    ai_skill = bot_fighter.get("ai_skill", 0.5)
    my_hp_pct  = bot_fighter["hp"] / bot_fighter["max_hp"]
    opp_hp_pct = opponent["hp"] / opponent["max_hp"]
    potions    = bot_fighter.get("potions", 0)

    # ── Случайный шум (чем ниже skill — тем больше рандома) ──────────────────
    if random.random() > ai_skill:
        return random.choices(
            ["attack", "skill", "defend"],
            weights=[50, 30, 20])[0]

    # ── Тактика умного бота ────────────────────────────────────────────────

    # 1. Критическое здоровье — лечимся
    if my_hp_pct < 0.30 and potions > 0:
        return "heal"

    # 2. Низкое здоровье но нет зелий — защищаемся
    if my_hp_pct < 0.25 and potions == 0:
        return "defend" if random.random() < 0.6 else "attack"

    # 3. Противник почти мёртв — добиваем умением (повышенный урон)
    if opp_hp_pct < 0.25:
        return "skill"

    # 4. Мы здоровее противника — давим атакой/умением
    if my_hp_pct > opp_hp_pct + 0.2:
        return random.choices(["skill", "attack"], weights=[60, 40])[0]

    # 5. Здоровье примерно равное — смешанная тактика
    if abs(my_hp_pct - opp_hp_pct) < 0.15:
        return random.choices(
            ["attack", "skill", "defend"],
            weights=[40, 35, 25])[0]

    # 6. Мы слабее — играем осторожно
    return random.choices(
        ["defend", "attack", "skill"],
        weights=[40, 35, 25])[0]


# ─── BATTLE STATE ──────────────────────────────────────────────────────────────

def _make_fighter(uid: int, chat_id, data: dict) -> dict:
    """Создать объект бойца из данных игрока"""
    s = data["stats"]
    return {
        "id":           uid,
        "chat":         chat_id,
        "name":         data["first_name"],
        "class_id":     data["class_id"],
        "hp":           s["hp"],
        "max_hp":       s["hp"],
        "stats":        copy.copy(s),
        "base_stats":   copy.copy(s),
        "action":       None,
        "potions":      2,
        "pending_heal": 0,
        "ai_skill":     data.get("ai_skill", 0),
        "difficulty":   data.get("difficulty", ""),
    }
class BattleState:
    def __init__(self, bid, p1, p2, is_bot=False):
        self.battle_id = bid
        self.is_bot    = is_bot
        self.round     = 1
        self.p1        = p1
        self.p2        = p2
        self._turn_task: asyncio.Task | None = None

    def get_fighter(self, uid: int) -> dict | None:
        if self.p1["id"] == uid: return self.p1
        if self.p2["id"] == uid: return self.p2
        return None

    def both_acted(self) -> bool:
        return (
            self.p1["action"] is not None and
            (self.is_bot or self.p2["action"] is not None)
        )


# ─── UI ────────────────────────────────────────────────────────────────────────

def battle_keyboard(bid: str, potions: int = 2) -> InlineKeyboardMarkup:
    pot_label = f"💊 Зелье ({potions})" if potions > 0 else "💊 Нет зелий"
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("⚔️ Атака",   callback_data=f"battle:attack:{bid}"),
         InlineKeyboardButton("✨ Умение",   callback_data=f"battle:skill:{bid}")],
        [InlineKeyboardButton("🛡️ Защита",  callback_data=f"battle:defend:{bid}"),
         InlineKeyboardButton(pot_label,     callback_data=f"battle:heal:{bid}")],
    ])


def hp_bar(hp: int, max_hp: int, n: int = 8) -> str:
    f = round(max(hp, 0) / max(max_hp, 1) * n)
    return "█" * f + "░" * (n - f)


def round_header(state: "BattleState") -> str:
    p1, p2 = state.p1, state.p2
    return (
        f"⚔️ *Раунд {state.round}*\n\n"
        f"*{p1['name']}*\n"
        f"❤️ `{hp_bar(p1['hp'], p1['max_hp'])}` {max(0,p1['hp'])}/{p1['max_hp']}\n\n"
        f"*{p2['name']}*\n"
        f"❤️ `{hp_bar(p2['hp'], p2['max_hp'])}` {max(0,p2['hp'])}/{p2['max_hp']}\n\n"
    )


# ─── COMBAT ENGINE ─────────────────────────────────────────────────────────────

def resolve_attack(attacker: dict, defender: dict,
                   act_a: str, act_d: str) -> tuple[str, int, int]:
    """
    Рассчитать один удар: attacker → defender.
    Возвращает (лог, урон_defender, контрудар_attacker).
    """
    sa  = attacker["stats"]
    sd  = defender["stats"]
    log = []
    cls_id = attacker["class_id"]

    # Зелье — не атакует
    if act_a == "heal":
        return "", 0, 0

    # ── Промах ──────────────────────────────────────────────────────────────
    if random.uniform(0, 100) > sa["accuracy"]:
        log.append(f"💨 *{attacker['name']}* промахнулся!")
        return "\n".join(log), 0, 0

    # ── Уворот ──────────────────────────────────────────────────────────────
    eff_dodge = sd["dodge"] * (0.65 if act_d == "defend" else 1.0)
    if random.uniform(0, 100) < eff_dodge:
        log.append(f"⚡️ *{defender['name']}* уклонился!")
        return "\n".join(log), 0, 0

    # ── Базовый урон ────────────────────────────────────────────────────────
    base = sa["atk"]
    class_mult = 1.0
    ignore_def_pct = 0.0    # сколько % защиты игнорирует
    guaranteed_crit = False

    # ── Умения классов ──────────────────────────────────────────────────────
    if act_a == "skill":
        if cls_id == "warrior":
            # Воин умение — это защита, не атака; здесь не применяется
            pass
        elif cls_id == "assassin":
            # Смертельный удар: гарантированный крит ×1.6, игнорирует 30% def
            guaranteed_crit = True
            class_mult      = 1.6
            ignore_def_pct  = 0.30
            log.append("🗡️ *Смертельный удар!*")
        elif cls_id == "berserker":
            # Ярость: гарантированный крит ×1.3, class_mult уже учитывает crit
            guaranteed_crit = True
            class_mult      = 1.3
            log.append("💢 *Ярость!*")
        elif cls_id == "mage":
            # Маг умение применяется в _resolve_round (меняет stats на раунд)
            pass

    # ── Крит ────────────────────────────────────────────────────────────────
    is_crit = guaranteed_crit or (random.uniform(0, 100) < sa["crit_chance"])
    crit_mult = (sa["crit_power"] / 100) if is_crit else 1.0

    if is_crit and not guaranteed_crit:
        log.append("💥 *Критический удар!*")

    # ── Блок (действие defend) ──────────────────────────────────────────────
    block = 0.0
    if act_d == "defend":
        if defender["class_id"] == "warrior" and act_d == "defend":
            # Железный блок: гарантированные 50% + 20% шанс полного отражения
            if random.uniform(0, 100) < 20:
                log.append(f"🛡️ *{defender['name']}* полностью отразил удар!")
                return "\n".join(log), 0, 0
            block = 0.50
            log.append(f"🛡️ *{defender['name']}* блокирует 50% урона.")
        else:
            block = 0.35
            log.append(f"🛡️ *{defender['name']}* уходит в защиту (-35%).")

    # ── Защита (def) снижает урон по формуле ────────────────────────────────
    effective_def = sd["def"] * (1.0 - ignore_def_pct)
    def_red = def_reduction(int(effective_def))

    # ── Предвидение снижает урон ─────────────────────────────────────────────
    foresight_red = min(0.30, sd["foresight"] / 100 * 0.5)

    # ── Итоговый урон ───────────────────────────────────────────────────────
    dmg = base * class_mult * crit_mult
    dmg = dmg * (1 - block)
    dmg = dmg * (1 - def_red)
    dmg = dmg * (1 - foresight_red)
    dmg = max(1, int(dmg))

    if is_crit:
        log.append(f"💥 *×{crit_mult:.1f}* крит-множитель")

    log.append(f"🗡️ *{attacker['name']}* наносит *{dmg}* урона.")

    # ── Контрудар ────────────────────────────────────────────────────────────
    cnt_dmg = 0
    counter_chance = sd["counter"]
    # Воин получает +15% к шансу контрудара когда его бьют критом — наказывает
    # агрессивные крит-классы (Берсерк/Ассасин) за атаку на защищающегося танка
    if defender["class_id"] == "warrior" and is_crit:
        counter_chance += 15

    if act_d in ("defend", "attack") and random.uniform(0, 100) < counter_chance:
        cnt_dmg = max(1, int(sd["atk"] * 0.25))
        log.append(f"🤺 *{defender['name']}* наносит контрудар: *{cnt_dmg}* урона!")

    return "\n".join(log), dmg, cnt_dmg


# ─── BATTLE HANDLER ────────────────────────────────────────────────────────────

class BattleHandler:

    @staticmethod
    async def start_pvp(app, p1_id, p2_id, p1_chat, p2_chat):
        db: Database = app.bot_data["db"]
        p1_raw = await db.get_player(p1_id)
        p2_raw = await db.get_player(p2_id)
        p1_eq  = await db.get_equipped(p1_id)
        p2_eq  = await db.get_equipped(p2_id)

        p1_stats, _ = calc_stats(p1_raw, p1_eq)
        p2_stats, _ = calc_stats(p2_raw, p2_eq)

        p1f = _make_fighter(p1_id, p1_chat,  {**p1_raw, "stats": p1_stats})
        p2f = _make_fighter(p2_id, p2_chat,  {**p2_raw, "stats": p2_stats})

        bid   = f"{p1_id}_{p2_id}"
        state = BattleState(bid, p1f, p2f, is_bot=False)
        active_battles[bid] = state

        cls1 = CLASSES[p1_raw["class_id"]]
        cls2 = CLASSES[p2_raw["class_id"]]
        intro = (
            f"⚔️ *АРЕНА — БОЙ НАЧИНАЕТСЯ!*\n\n"
            f"*{p1f['name']}* {cls1['name']}\n"
            f"❤️{p1_stats['hp']} 🗡{p1_stats['atk']} 🔰{p1_stats['def']}\n\n"
            f"VS\n\n"
            f"*{p2f['name']}* {cls2['name']}\n"
            f"❤️{p2_stats['hp']} 🗡{p2_stats['atk']} 🔰{p2_stats['def']}\n\n"
            f"Выбери действие:"
        )
        try:
            await app.bot.send_message(p1_chat, intro, parse_mode="Markdown",
                                       reply_markup=battle_keyboard(bid, 2))
            await app.bot.send_message(p2_chat, intro, parse_mode="Markdown",
                                       reply_markup=battle_keyboard(bid, 2))
        except Exception as e:
            logger.error(f"PvP start error: {e}")

        state._turn_task = asyncio.create_task(
            BattleHandler._turn_timeout(app, bid))

    @staticmethod
    async def start_vs_bot(app, p1_id: int, p1_chat: int):
        db: Database = app.bot_data["db"]
        p1_raw = await db.get_player(p1_id)
        if not p1_raw:
            return
        p1_eq     = await db.get_equipped(p1_id)
        p1_stats, _ = calc_stats(p1_raw, p1_eq)
        p1f = _make_fighter(p1_id, p1_chat, {**p1_raw, "stats": p1_stats})

        streak  = p1_raw.get("streak", 0)
        bot_raw = make_bot_opponent(p1_raw["level"], streak)
        p2f     = _make_fighter(0, None, bot_raw)

        bid   = f"{p1_id}_bot"
        state = BattleState(bid, p1f, p2f, is_bot=True)
        active_battles[bid] = state

        diff_label = BOT_DIFFICULTY.get(bot_raw.get("difficulty", ""), {}).get("label", "")
        intro = (
            f"⚔️ *БОЙ С БОТОМ* {diff_label}\n_Соперник не найден_\n\n"
            f"*{p1f['name']}* {CLASSES[p1_raw['class_id']]['name']}\n"
            f"❤️{p1_stats['hp']} 🗡{p1_stats['atk']} 🔰{p1_stats['def']}\n\n"
            f"VS\n\n"
            f"*{p2f['name']}* {CLASSES[bot_raw['class_id']]['name']}\n"
            f"❤️{p2f['hp']} 🗡{p2f['stats']['atk']} 🔰{p2f['stats']['def']}\n\n"
            f"Выбери действие:"
        )
        try:
            await app.bot.send_message(p1_chat, intro, parse_mode="Markdown",
                                       reply_markup=battle_keyboard(bid, 2))
        except Exception as e:
            logger.error(f"vs_bot start error: {e}")

        state._turn_task = asyncio.create_task(
            BattleHandler._turn_timeout(app, bid))

    @staticmethod
    async def action(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        query  = update.callback_query
        await query.answer()
        uid    = query.from_user.id
        parts  = query.data.split(":")
        action = parts[1]
        bid    = parts[2]

        state = active_battles.get(bid)
        if not state:
            await query.edit_message_text("⚠️ Бой завершён.")
            return

        fighter = state.get_fighter(uid)
        if not fighter:
            await query.answer("Ты не в этом бою!", show_alert=True)
            return
        if fighter["action"] is not None:
            await query.answer("Ты уже выбрал действие.", show_alert=True)
            return

        names = {"attack": "⚔️ Атака", "skill": "✨ Умение",
                 "defend": "🛡️ Защита", "heal": "💊 Зелье"}

        if action == "heal":
            if fighter["potions"] <= 0:
                await query.answer("💊 Зелья закончились!", show_alert=True)
                return
            fighter["potions"] -= 1
            heal = int(fighter["max_hp"] * 0.25)
            fighter["pending_heal"] = heal
            fighter["action"] = "heal"
            await query.edit_message_text(
                f"💊 *Зелье выбрано* (осталось: {fighter['potions']})\n"
                f"+{heal} ОЗ применятся в начале раунда.\n\n"
                f"⏳ Ждём противника...", parse_mode="Markdown")
        else:
            fighter["action"] = action
            await query.edit_message_text(
                f"✅ *{names.get(action, action)}* выбрана.\n\n"
                f"⏳ Ждём противника...", parse_mode="Markdown")

        # Бот ходит немедленно — тактический ИИ
        if state.is_bot and state.p2["action"] is None:
            decision = bot_decide_action(state.p2, state.p1)
            if decision == "heal" and state.p2["potions"] > 0:
                state.p2["potions"] -= 1
                state.p2["pending_heal"] = int(state.p2["max_hp"] * 0.25)
                state.p2["action"] = "heal"
            elif decision == "heal":
                # Нет зелий — атакуем вместо лечения
                state.p2["action"] = "attack"
            else:
                state.p2["action"] = decision

        if state.both_acted():
            if state._turn_task:
                state._turn_task.cancel()
            await BattleHandler._resolve_round(ctx.application, bid)

    @staticmethod
    async def _turn_timeout(app, bid: str):
        await asyncio.sleep(TURN_TIMEOUT)
        state = active_battles.get(bid)
        if not state:
            return
        if state.p1["action"] is None:
            state.p1["action"] = "attack"
        if not state.is_bot and state.p2["action"] is None:
            state.p2["action"] = "attack"
        if state.is_bot and state.p2["action"] is None:
            state.p2["action"] = "attack"
        await BattleHandler._resolve_round(app, bid)

    @staticmethod
    async def _resolve_round(app, bid: str):
        state = active_battles.get(bid)
        if not state:
            return

        p1, p2 = state.p1, state.p2
        log = [f"*── Раунд {state.round} ──*\n"]

        # ── 1. Зелья ────────────────────────────────────────────────────────
        for f in (p1, p2):
            if f.get("pending_heal", 0) > 0:
                f["hp"] = min(f["max_hp"], f["hp"] + f["pending_heal"])
                log.append(f"💊 *{f['name']}* восстанавливает {f['pending_heal']} ОЗ!")
                f["pending_heal"] = 0

        # ── 2. Умение мага — удвоить предвидение и контрудар на этот раунд ─
        for f in (p1, p2):
            if f["action"] == "skill" and f["class_id"] == "mage":
                f["stats"] = copy.copy(f["base_stats"])
                f["stats"]["foresight"] = min(40, f["stats"]["foresight"] * 2)
                f["stats"]["counter"]   = min(35, f["stats"]["counter"] * 2)
                log.append(f"🧿 *{f['name']}* активирует Предчувствие! "
                           f"(предвидение ×2, контрудар ×2)")

        # ── 3. Берсерк в ярости — def -30% ──────────────────────────────────
        p1_rage = p1["action"] == "skill" and p1["class_id"] == "berserker"
        p2_rage = p2["action"] == "skill" and p2["class_id"] == "berserker"
        if p1_rage:
            p1["stats"] = copy.copy(p1["base_stats"])
            p1["stats"]["def"] = max(0, int(p1["stats"]["def"] * 0.70))
        if p2_rage:
            p2["stats"] = copy.copy(p2["base_stats"])
            p2["stats"]["def"] = max(0, int(p2["stats"]["def"] * 0.70))

        # ── 4. Удары ─────────────────────────────────────────────────────────
        txt1, dmg1, cnt1 = resolve_attack(p1, p2, p1["action"], p2["action"])
        if txt1: log.append(txt1)
        p2["hp"] -= dmg1
        p1["hp"] -= cnt1

        if p2["hp"] > 0:
            txt2, dmg2, cnt2 = resolve_attack(p2, p1, p2["action"], p1["action"])
            if txt2: log.append("\n" + txt2)
            p1["hp"] -= dmg2
            p2["hp"] -= cnt2

        # ── 5. Восстановить stats после раунда ───────────────────────────────
        for f in (p1, p2):
            f["stats"] = copy.copy(f["base_stats"])

        # ── 6. Сброс действий ────────────────────────────────────────────────
        p1["action"] = None
        p2["action"] = None
        state.round += 1

        # ── 7. Проверка победителя ───────────────────────────────────────────
        winner_id = None
        if p1["hp"] <= 0 and p2["hp"] <= 0:
            winner_id = -1
        elif p1["hp"] <= 0:
            winner_id = p2["id"]
        elif p2["hp"] <= 0:
            winner_id = p1["id"]

        # ── 8. Итог раунда ───────────────────────────────────────────────────
        status = (
            f"\n\n❤️ *{p1['name']}*: {max(0,p1['hp'])}/{p1['max_hp']}\n"
            f"❤️ *{p2['name']}*: {max(0,p2['hp'])}/{p2['max_hp']}"
        )
        summary = "\n".join(log) + status

        if winner_id is not None:
            await BattleHandler._end_battle(app, bid, winner_id, summary)
        else:
            next_txt = summary + "\n\n*Выбери действие:*"
            try:
                await app.bot.send_message(
                    p1["chat"], next_txt, parse_mode="Markdown",
                    reply_markup=battle_keyboard(bid, p1["potions"]))
                if not state.is_bot and p2["chat"]:
                    await app.bot.send_message(
                        p2["chat"], next_txt, parse_mode="Markdown",
                        reply_markup=battle_keyboard(bid, p2["potions"]))
            except Exception as e:
                logger.error(f"round msg error: {e}")

            state._turn_task = asyncio.create_task(
                BattleHandler._turn_timeout(app, bid))

    @staticmethod
    async def _end_battle(app, bid: str, winner_id: int, last_log: str):
        state = active_battles.pop(bid, None)
        if not state:
            return

        db: Database = app.bot_data["db"]
        p1, p2 = state.p1, state.p2
        is_draw = winner_id == -1

        result_p1 = "🤝 *Ничья!*" if is_draw else (
            "🏆 *Ты победил!*" if winner_id == p1["id"] else "💀 *Ты проиграл...*")
        result_p2 = "🤝 *Ничья!*" if is_draw else (
            "🏆 *Ты победил!*" if winner_id == p2["id"] else "💀 *Ты проиграл...*")

        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("⚔️ Снова в бой", callback_data="arena")],
            [InlineKeyboardButton("👤 Профиль",     callback_data="profile")],
        ])

        async def _update_and_msg(fighter, result_txt, is_winner, opponent=None):
            try:
                raw = await db.get_player(fighter["id"])
                if not raw:
                    return
                exp_gain  = ARENA_WIN_EXP  if is_winner else ARENA_LOSS_EXP
                gold_gain = ARENA_WIN_GOLD if is_winner else ARENA_LOSS_GOLD

                # Бонус за победу над сложным ботом
                diff_bonus_txt = ""
                if is_winner and opponent and opponent.get("difficulty"):
                    diff_mult = {
                        "rookie": 1.0, "veteran": 1.15,
                        "elite": 1.4, "nightmare": 1.8,
                    }.get(opponent["difficulty"], 1.0)
                    if diff_mult > 1.0:
                        bonus_gold = int(gold_gain * (diff_mult - 1))
                        bonus_exp  = int(exp_gain * (diff_mult - 1))
                        gold_gain += bonus_gold
                        exp_gain  += bonus_exp
                        diff_label = BOT_DIFFICULTY.get(opponent["difficulty"], {}).get("label", "")
                        diff_bonus_txt = f"\n🎯 Бонус за сложность {diff_label}: +{bonus_gold}💰 +{bonus_exp}✨"

                # MMR
                old_mmr = raw.get("mmr", 1000)
                new_mmr = max(0, old_mmr + (MMR_WIN if is_winner else -MMR_LOSS))

                # Серия побед
                old_streak = raw.get("streak", 0)
                new_streak = (old_streak + 1) if is_winner else 0

                new_exp, leveled = _add_exp(raw, exp_gain)
                new_lvl  = raw["level"] + (1 if leveled else 0)
                new_gold = raw["gold"] + gold_gain

                await db.update_player(
                    fighter["id"],
                    wins=raw["wins"]     + (1 if is_winner else 0),
                    losses=raw["losses"] + (0 if is_winner else 1),
                    exp=new_exp, level=new_lvl, gold=new_gold,
                    mmr=new_mmr, streak=new_streak,
                    last_battle=int(time.time()),
                )

                drop_txt = ""
                ach_txt  = ""

                # Дроп предметов (только победителю) — не критично если упадёт
                try:
                    from handlers.loot import roll_drop, format_drop
                    drop_items = await roll_drop(
                        db, fighter["id"], raw["level"], is_winner, state.is_bot
                    )
                    drop_txt = format_drop(drop_items)
                except Exception as e:
                    logger.error(f"roll_drop error: {e}")

                # Дроп материалов крафта — не критично если упадёт
                try:
                    from handlers.craft import roll_materials, format_materials, MATERIALS
                    mat_list = await roll_materials(db, fighter["id"], raw["level"])
                    if is_winner and not state.is_bot:
                        await db.add_material(fighter["id"], "victory_token", 1)
                        mat_list.append(MATERIALS["victory_token"]["name"])
                    drop_txt += format_materials(mat_list)
                except Exception as e:
                    logger.error(f"roll_materials error: {e}")

                # Достижения — не критично если упадёт
                try:
                    from handlers.achievements import check_achievements
                    p_updated = await db.get_player(fighter["id"])
                    ach_msgs  = await check_achievements(db, fighter["id"], p_updated)
                    ach_txt   = ("\n\n" + "\n".join(ach_msgs)) if ach_msgs else ""
                except Exception as e:
                    logger.error(f"check_achievements error: {e}")

                # Квесты — не критично если упадёт
                try:
                    from handlers.quests import update_battle_quests
                    await update_battle_quests(db, fighter["id"], is_winner)
                except Exception as e:
                    logger.error(f"update_battle_quests error: {e}")

                try:
                    from gamedata import get_rank
                    rank = get_rank(new_mmr)
                except Exception:
                    rank = ""

                msg = (
                    f"{last_log}\n\n{'━'*20}\n"
                    f"{result_txt}\n"
                    f"💰 +{gold_gain} золота  ✨ +{exp_gain} опыта\n"
                    f"📊 MMR: {old_mmr} → *{new_mmr}* {rank}"
                    + (f"\n🔥 Серия: *{new_streak}*" if new_streak >= 2 else "")
                    + ("\n🎉 *Новый уровень!*" if leveled else "")
                    + drop_txt + ach_txt
                )

                await app.bot.send_message(
                    fighter["chat"], msg, parse_mode="Markdown", reply_markup=kb)

            except Exception as e:
                logger.error(f"_update_and_msg CRITICAL error for {fighter.get('id')}: {e}")
                # Аварийное сообщение — хотя бы базовый результат должен дойти
                try:
                    await app.bot.send_message(
                        fighter["chat"],
                        f"{result_txt}\n\n⚠️ Произошла ошибка при начислении награды. "
                        f"Обратись к администратору.",
                        parse_mode="Markdown"
                    )
                except Exception:
                    pass

        if not state.is_bot:
            await _update_and_msg(p1, result_p1, not is_draw and winner_id == p1["id"])
            await _update_and_msg(p2, result_p2, not is_draw and winner_id == p2["id"])
            await db.save_battle(p1["id"], p2["id"],
                                 0 if is_draw else winner_id, state.round - 1, [],
                                 is_bot=False)
        else:
            is_win = winner_id == p1["id"]
            await _update_and_msg(p1, result_p1, is_win, opponent=p2)
            await db.save_battle(p1["id"], 0, p1["id"] if is_win else 0,
                                 state.round - 1, [], is_bot=True)
