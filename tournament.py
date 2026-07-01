"""
Турнир — /tournament
Регистрация → 8 игроков → автоматические бои → финал
"""

import asyncio
import random
import time
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database import Database
from gamedata import calc_stats, CLASSES
from safety import guard_handler

TOURNAMENT_SIZE = 8
TOURNAMENT_REG_TIME = 300   # 5 минут на регистрацию
TOURNAMENT_REWARDS = {
    1: {"gold": 1000, "title": "🏆 Чемпион"},
    2: {"gold": 500,  "title": "🥈 Финалист"},
    3: {"gold": 250,  "title": "🥉 Полуфиналист"},
}

# Глобальное состояние турнира
tournament_state = {
    "active":       False,
    "registering":  False,
    "participants": [],   # list of user_id
    "bracket":      [],   # список пар
    "round":        0,
    "winners":      [],
}


class TournamentHandler:

    @staticmethod
    @guard_handler()
    async def show(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        db: Database = ctx.bot_data["db"]
        uid = update.effective_user.id
        p = await db.get_player(uid)
        if not p:
            await update.message.reply_text("Сначала /start")
            return
        text, kb = _build_menu(uid)
        await update.message.reply_text(text, parse_mode="Markdown", reply_markup=kb)

    @staticmethod
    @guard_handler()
    async def register(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        q = update.callback_query
        await q.answer()
        db: Database = ctx.bot_data["db"]
        uid = q.from_user.id
        p = await db.get_player(uid)
        if not p:
            await q.edit_message_text("Сначала /start")
            return

        t = tournament_state
        if not t["registering"]:
            await q.answer("Регистрация закрыта.", show_alert=True)
            return
        if uid in t["participants"]:
            await q.answer("Ты уже зарегистрирован!", show_alert=True)
            return
        if len(t["participants"]) >= TOURNAMENT_SIZE:
            await q.answer("Турнир заполнен!", show_alert=True)
            return

        t["participants"].append(uid)
        count = len(t["participants"])
        await q.edit_message_text(
            f"✅ *Ты зарегистрирован на турнир!*\n\n"
            f"Участников: *{count}/{TOURNAMENT_SIZE}*\n"
            f"Ожидай начала...",
            parse_mode="Markdown"
        )

        if count >= TOURNAMENT_SIZE:
            asyncio.create_task(_start_tournament(ctx.application))

    @staticmethod
    @guard_handler()
    async def start_registration(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        """Только для админов"""
        from config import ADMIN_IDS
        if update.effective_user.id not in ADMIN_IDS:
            await update.message.reply_text("🚫 Нет доступа.")
            return

        t = tournament_state
        if t["active"] or t["registering"]:
            await update.message.reply_text("Турнир уже идёт!")
            return

        t["registering"] = True
        t["participants"] = []
        t["bracket"] = []
        t["round"] = 0
        t["winners"] = []

        # Оповестить всех
        db: Database = ctx.bot_data["db"]
        players = await db.get_all_players()
        kb = InlineKeyboardMarkup([[
            InlineKeyboardButton("⚔️ Зарегистрироваться", callback_data="tournament_reg")
        ]])
        for pl in players:
            try:
                await ctx.bot.send_message(
                    pl["user_id"],
                    f"🏆 *НАЧИНАЕТСЯ ТУРНИР АРЕНЫ!*\n\n"
                    f"Нужно {TOURNAMENT_SIZE} участников\n"
                    f"Регистрация открыта {TOURNAMENT_REG_TIME//60} минут!\n\n"
                    f"Победитель получит *1000💰* и титул *Чемпион*!",
                    parse_mode="Markdown",
                    reply_markup=kb
                )
                await asyncio.sleep(0.05)
            except Exception:
                pass

        await update.message.reply_text(
            f"✅ Регистрация открыта! Ждём {TOURNAMENT_SIZE} участников.")

        # Авто-старт через 5 минут с ботами если не хватает
        asyncio.create_task(_auto_start(ctx.application, TOURNAMENT_REG_TIME))


async def _auto_start(app, delay: int):
    await asyncio.sleep(delay)
    t = tournament_state
    if not t["registering"]:
        return
    # Добрать ботами до TOURNAMENT_SIZE
    while len(t["participants"]) < TOURNAMENT_SIZE:
        t["participants"].append(-(len(t["participants"]) + 1))  # отрицательный ID = бот
    await _start_tournament(app)


async def _start_tournament(app):
    t = tournament_state
    t["registering"] = False
    t["active"] = True
    t["round"] = 1

    participants = list(t["participants"])
    random.shuffle(participants)
    t["bracket"] = list(zip(participants[::2], participants[1::2]))

    db: Database = app.bot_data["db"]

    # Уведомить участников
    for uid in participants:
        if uid > 0:
            try:
                await app.bot.send_message(
                    uid,
                    f"🏆 *Турнир начался!*\nРаунд {t['round']}/{_rounds(TOURNAMENT_SIZE)}\n\nСкоро будет объявлен твой противник...",
                    parse_mode="Markdown"
                )
            except Exception:
                pass

    await asyncio.sleep(3)
    await _run_round(app)


async def _run_round(app):
    t = tournament_state
    db: Database = app.bot_data["db"]
    winners = []

    for p1_id, p2_id in t["bracket"]:
        winner = await _simulate_fight(app, db, p1_id, p2_id)
        winners.append(winner)

    t["winners"] = winners
    t["round"] += 1

    if len(winners) == 1:
        await _end_tournament(app, winners[0])
        return

    if len(winners) % 2 != 0:
        # Пропуск при нечётном количестве
        winners.append(winners[-1])

    t["bracket"] = list(zip(winners[::2], winners[1::2]))
    await asyncio.sleep(5)
    await _run_round(app)


async def _simulate_fight(app, db: Database, p1_id: int, p2_id: int) -> int:
    """Быстрый симулированный бой для турнира"""
    p1_is_bot = p1_id < 0
    p2_is_bot = p2_id < 0

    p1_power = await _get_power(db, p1_id) if not p1_is_bot else random.randint(100, 300)
    p2_power = await _get_power(db, p2_id) if not p2_is_bot else random.randint(100, 300)

    # Победитель определяется по силе + рандом ±20%
    p1_roll = p1_power * random.uniform(0.8, 1.2)
    p2_roll = p2_power * random.uniform(0.8, 1.2)
    winner_id = p1_id if p1_roll >= p2_roll else p2_id
    loser_id  = p2_id if winner_id == p1_id else p1_id

    # Уведомить
    for uid, result in [(p1_id, winner_id == p1_id), (p2_id, winner_id == p2_id)]:
        if uid > 0:
            opp_id = p2_id if uid == p1_id else p1_id
            opp_name = (await db.get_player(opp_id))["first_name"] if opp_id > 0 else "🤖 Бот"
            try:
                await app.bot.send_message(
                    uid,
                    f"🏆 *Раунд {tournament_state['round']} турнира*\n\n"
                    f"Vs *{opp_name}*\n\n"
                    f"{'✅ Ты победил!' if result else '❌ Ты выбыл из турнира.'}",
                    parse_mode="Markdown"
                )
            except Exception:
                pass

    return winner_id


async def _get_power(db: Database, uid: int) -> int:
    p = await db.get_player(uid)
    if not p:
        return 100
    eq = await db.get_equipped(uid)
    stats, _ = calc_stats(p, eq)
    return stats["hp"] + stats["atk"] * 5 + stats["def"] * 3


async def _end_tournament(app, winner_id: int):
    t = tournament_state
    t["active"] = False
    db: Database = app.bot_data["db"]

    if winner_id > 0:
        p = await db.get_player(winner_id)
        reward = TOURNAMENT_REWARDS[1]
        await db.update_player(winner_id,
            gold=p["gold"] + reward["gold"],
            title_id="champion"
        )
        try:
            await app.bot.send_message(
                winner_id,
                f"🏆 *ТЫ ПОБЕДИЛ В ТУРНИРЕ!*\n\n"
                f"💰 +{reward['gold']} золота\n"
                f"👑 Титул: {reward['title']}",
                parse_mode="Markdown"
            )
        except Exception:
            pass


def _rounds(n: int) -> int:
    import math
    return math.ceil(math.log2(n))


def _build_menu(uid: int) -> tuple[str, InlineKeyboardMarkup]:
    t = tournament_state
    if t["registering"]:
        registered = uid in t["participants"]
        txt = (
            f"🏆 *ТУРНИР АРЕНЫ*\n\n"
            f"📋 Участников: *{len(t['participants'])}/{TOURNAMENT_SIZE}*\n"
            f"Статус: 🟢 Регистрация открыта\n\n"
            f"Победитель получит *1000💰* и титул *Чемпион*!"
        )
        if registered:
            kb = InlineKeyboardMarkup([[
                InlineKeyboardButton("✅ Ты зарегистрирован", callback_data="tournament_menu")
            ]])
        else:
            kb = InlineKeyboardMarkup([[
                InlineKeyboardButton("⚔️ Зарегистрироваться", callback_data="tournament_reg")
            ]])
    elif t["active"]:
        txt = (
            f"🏆 *ТУРНИР ИДЁТ*\n\n"
            f"⚔️ Раунд: *{t['round']}*\n"
            f"Участников осталось: *{len(t['bracket']) * 2}*"
        )
        kb = InlineKeyboardMarkup([[
            InlineKeyboardButton("◀️ Профиль", callback_data="profile")
        ]])
    else:
        txt = (
            f"🏆 *ТУРНИР АРЕНЫ*\n\n"
            f"Сейчас турнира нет.\n"
            f"Ожидай объявления от администратора!\n\n"
            f"_Команда для старта: /tournament_start (только для админа)_"
        )
        kb = InlineKeyboardMarkup([[
            InlineKeyboardButton("◀️ Профиль", callback_data="profile")
        ]])
    return txt, kb
