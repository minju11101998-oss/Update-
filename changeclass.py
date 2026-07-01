"""Смена класса — /changeclass"""

import time
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database import Database
from gamedata import CLASSES, calc_stats, stats_text, def_reduction
from config import CLASS_CHANGE_COOLDOWN, CLASS_CHANGE_COST
from safety import guard_handler


def _cd_left(ts: int) -> int:
    return max(0, CLASS_CHANGE_COOLDOWN - (int(time.time()) - int(ts)))


def _fmt_time(sec: int) -> str:
    if sec <= 0:
        return "0с"
    if sec >= 86400:
        return f"{sec // 86400}д {(sec % 86400) // 3600}ч"
    if sec >= 3600:
        return f"{sec // 3600}ч {(sec % 3600) // 60}мин"
    return f"{sec // 60}мин {sec % 60}с"


def _class_buttons(current_class: str) -> list:
    buttons = []
    for cid, cls in CLASSES.items():
        if cid == current_class:
            label = f"✅ {cls['name']} (текущий)"
        else:
            label = f"{cls['emoji']} {cls['name']}"
        buttons.append([InlineKeyboardButton(label, callback_data=f"cc_view:{cid}")])
    buttons.append([InlineKeyboardButton("◀️ Профиль", callback_data="profile")])
    return buttons


class ClassChangeHandler:

    # ── /changeclass — главное меню ──────────────────────────────────────────

    @staticmethod
    @guard_handler()
    async def show(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        db: Database = ctx.bot_data["db"]
        p = await db.get_player(update.effective_user.id)
        if not p:
            await update.message.reply_text("Сначала /start")
            return
        txt, kb = _build_menu(p)
        await update.message.reply_text(txt, parse_mode="Markdown", reply_markup=kb)

    @staticmethod
    @guard_handler()
    async def show_cb(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        q = update.callback_query
        await q.answer()
        db: Database = ctx.bot_data["db"]
        p = await db.get_player(q.from_user.id)
        if not p:
            await q.edit_message_text("Сначала /start")
            return
        txt, kb = _build_menu(p)
        await q.edit_message_text(txt, parse_mode="Markdown", reply_markup=kb)

    # ── Просмотр класса перед сменой ────────────────────────────────────────

    @staticmethod
    @guard_handler()
    async def preview(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        q = update.callback_query
        await q.answer()
        db: Database = ctx.bot_data["db"]
        uid = q.from_user.id

        # Получаем выбранный класс из callback_data
        # Формат: cc_view:warrior  или  class_preview:warrior
        raw = q.data  # например "cc_view:assassin"
        new_cls = raw.split(":", 1)[1]

        if new_cls not in CLASSES:
            await q.answer("Неверный класс!", show_alert=True)
            return

        p = await db.get_player(uid)
        if not p:
            await q.edit_message_text("Сначала /start")
            return

        # Если это текущий класс — просто показать инфо
        if p["class_id"] == new_cls:
            cls = CLASSES[new_cls]
            fake = {"level": p["level"], "class_id": new_cls}
            st, sk = calc_stats(fake, {})
            await q.edit_message_text(
                f"✅ *{cls['name']}* — это твой текущий класс\n\n"
                f"_{cls['desc']}_\n\n"
                f"🔑 *{cls['skill']}*\n_{cls['skill_desc']}_\n\n"
                f"❤️ {st['hp']}  🗡 {st['atk']}  🔰 {st['def']}\n"
                f"🥊 {st['crit_chance']}%  💥 {st['crit_power']}%  ⚡️ {st['dodge']}%",
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("◀️ Назад", callback_data="changeclass")]
                ])
            )
            return

        # Проверки доступности
        cd = _cd_left(p.get("last_class_change") or 0)
        can_change = cd == 0 and p["gold"] >= CLASS_CHANGE_COST

        cls     = CLASSES[new_cls]
        old_cls = CLASSES[p["class_id"]]
        fake    = {"level": p["level"], "class_id": new_cls}
        st, sk  = calc_stats(fake, {})
        dr      = round(def_reduction(st["def"]) * 100, 1)

        # Статус
        if cd > 0:
            status = f"⏳ Кулдаун: *{_fmt_time(cd)}*"
        elif p["gold"] < CLASS_CHANGE_COST:
            status = f"❌ Недостаточно золота (нужно {CLASS_CHANGE_COST}💰)"
        else:
            status = f"✅ Смена доступна"

        txt = (
            f"🔄 *Смена класса*\n\n"
            f"{old_cls['emoji']} {old_cls['name']} → "
            f"{cls['emoji']} *{cls['name']}*\n"
            f"_{cls['desc']}_\n\n"
            f"*Навыки на Ур.{p['level']}:*\n"
            f"✊ Сила: {sk['strength']}   ♥️ Выносливость: {sk['endurance']}\n"
            f"💫 Ловкость: {sk['agility']}   🧿 Интуиция: {sk['intuition']}\n\n"
            f"*Боевые статы:*\n"
            f"❤️ {st['hp']}  🗡 {st['atk']}  🔰 {st['def']} (-{dr}%)\n"
            f"🥊 {st['crit_chance']}%  💥 {st['crit_power']}%  ⚡️ {st['dodge']}%\n"
            f"👁 {st['foresight']}%  🤺 {st['counter']}%\n\n"
            f"🔑 *{cls['skill']}*\n_{cls['skill_desc']}_\n\n"
            f"💰 Стоимость: *{CLASS_CHANGE_COST}* золота\n"
            f"👛 У тебя: *{p['gold']}* золота\n"
            f"{status}"
        )

        buttons = []
        if can_change:
            buttons.append([InlineKeyboardButton(
                f"✅ Сменить на {cls['name']} ({CLASS_CHANGE_COST}💰)",
                callback_data=f"cc_confirm:{new_cls}"
            )])
        buttons.append([InlineKeyboardButton("◀️ Назад", callback_data="changeclass")])

        await q.edit_message_text(
            txt, parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(buttons)
        )

    # ── Подтверждение смены ──────────────────────────────────────────────────

    @staticmethod
    @guard_handler()
    async def confirm(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        q = update.callback_query
        await q.answer()
        db: Database = ctx.bot_data["db"]
        uid = q.from_user.id

        new_cls = q.data.split(":", 1)[1]

        if new_cls not in CLASSES:
            await q.answer("Неверный класс!", show_alert=True)
            return

        p = await db.get_player(uid)
        if not p:
            await q.edit_message_text("Сначала /start")
            return

        # Финальные проверки
        cd = _cd_left(p.get("last_class_change") or 0)
        if cd > 0:
            await q.edit_message_text(
                f"⏳ Кулдаун ещё не истёк: *{_fmt_time(cd)}*",
                parse_mode="Markdown"
            )
            return

        if p["class_id"] == new_cls:
            await q.edit_message_text("Это уже твой класс.")
            return

        if p["gold"] < CLASS_CHANGE_COST:
            await q.edit_message_text(
                f"❌ Недостаточно золота!\n"
                f"Нужно: *{CLASS_CHANGE_COST}*💰\n"
                f"У тебя: *{p['gold']}*💰",
                parse_mode="Markdown"
            )
            return

        # Применяем смену
        old_cls = CLASSES[p["class_id"]]
        new_cls_data = CLASSES[new_cls]

        await db.update_player(
            uid,
            class_id=new_cls,
            gold=p["gold"] - CLASS_CHANGE_COST,
            last_class_change=int(time.time()),
        )

        # Показываем новые статы
        fake = {"level": p["level"], "class_id": new_cls}
        st, sk = calc_stats(fake, {})

        await q.edit_message_text(
            f"✅ *Класс успешно изменён!*\n\n"
            f"{old_cls['emoji']} {old_cls['name']} → "
            f"{new_cls_data['emoji']} *{new_cls_data['name']}*\n\n"
            f"{stats_text(st, sk)}\n\n"
            f"💰 Списано: *{CLASS_CHANGE_COST}* золота\n"
            f"⏳ Следующая смена через: *{_fmt_time(CLASS_CHANGE_COOLDOWN)}*",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("👤 Профиль", callback_data="profile"),
                 InlineKeyboardButton("⚔️ Арена",   callback_data="arena")],
            ])
        )


def _build_menu(p: dict) -> tuple[str, InlineKeyboardMarkup]:
    cur    = CLASSES[p["class_id"]]
    cd     = _cd_left(p.get("last_class_change") or 0)
    cd_txt = f"⏳ Кулдаун: *{_fmt_time(cd)}*" if cd > 0 else "✅ Смена доступна"

    txt = (
        f"🔄 *СМЕНА КЛАССА*\n\n"
        f"Текущий класс: {cur['emoji']} *{cur['name']}*\n"
        f"💰 Стоимость: *{CLASS_CHANGE_COST}* | У тебя: *{p['gold']}*\n"
        f"{cd_txt}\n\n"
        f"Выбери класс чтобы посмотреть статы:"
    )
    kb = InlineKeyboardMarkup(_class_buttons(p["class_id"]))
    return txt, kb
