"""Система дуэлей — /duel @username"""

import time
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database import Database
from handlers.battle import BattleHandler
from safety import guard_handler

DUEL_EXPIRE = 60  # секунд на принятие


class DuelHandler:

    @staticmethod
    @guard_handler()
    async def send(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        db: Database = ctx.bot_data["db"]
        uid  = update.effective_user.id
        p    = await db.get_player(uid)
        if not p:
            await update.message.reply_text("Сначала /start"); return

        # /duel @username
        if not update.message.entities:
            await update.message.reply_text(
                "Использование: /duel @username\nПример: /duel @battleking"); return

        target_username = None
        for ent in update.message.entities:
            if ent.type == "mention":
                target_username = update.message.text[
                    ent.offset+1 : ent.offset+ent.length].lower()
                break

        if not target_username:
            await update.message.reply_text("Укажи @username противника"); return

        # Найти игрока по username
        all_players = await db.get_all_players()
        target = next(
            (pl for pl in all_players
             if pl.get("username", "").lower() == target_username),
            None
        )
        if not target:
            await update.message.reply_text(
                f"❌ Игрок @{target_username} не найден в Арене."); return

        to_id = target["user_id"]
        if to_id == uid:
            await update.message.reply_text("Нельзя вызвать самого себя!"); return

        # Сохранить вызов
        await db.create_duel(uid, to_id)

        kb = InlineKeyboardMarkup([[
            InlineKeyboardButton("✅ Принять дуэль",  callback_data=f"duel_accept:{uid}"),
            InlineKeyboardButton("❌ Отклонить",      callback_data=f"duel_decline:{uid}"),
        ]])

        await update.message.reply_text(
            f"⚔️ Вызов отправлен *{target['first_name']}*!\n"
            f"У него {DUEL_EXPIRE} секунд на ответ.",
            parse_mode="Markdown"
        )

        try:
            await ctx.bot.send_message(
                to_id,
                f"⚔️ *{p['first_name']}* вызывает тебя на дуэль!\n"
                f"Уровень {p['level']} | {p['wins']}W\n\n"
                f"У тебя {DUEL_EXPIRE} секунд.",
                parse_mode="Markdown",
                reply_markup=kb
            )
        except Exception:
            await update.message.reply_text(
                "❌ Не удалось отправить уведомление. Возможно, игрок не запускал бота.")

    @staticmethod
    @guard_handler()
    async def accept(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        q      = update.callback_query; await q.answer()
        db: Database = ctx.bot_data["db"]
        to_id  = q.from_user.id
        from_id = int(q.data.split(":")[1])

        duel = await db.get_duel(from_id, to_id)
        if not duel:
            await q.edit_message_text("❌ Вызов истёк или отменён."); return

        if int(time.time()) - duel["created_at"] > DUEL_EXPIRE:
            await db.delete_duel(from_id, to_id)
            await q.edit_message_text("⏳ Время вышло."); return

        await db.delete_duel(from_id, to_id)
        await q.edit_message_text("⚔️ Дуэль принята! Бой начинается...")

        await BattleHandler.start_pvp(
            ctx.application,
            from_id, to_id,
            from_id, to_id  # chat_id = user_id для личных сообщений
        )

    @staticmethod
    @guard_handler()
    async def decline(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        q      = update.callback_query; await q.answer()
        db: Database = ctx.bot_data["db"]
        to_id   = q.from_user.id
        from_id = int(q.data.split(":")[1])

        await db.delete_duel(from_id, to_id)
        p = await db.get_player(to_id)
        name = p["first_name"] if p else "Игрок"

        await q.edit_message_text(f"❌ Ты отклонил вызов.")
        try:
            await ctx.bot.send_message(from_id, f"❌ *{name}* отклонил твой вызов.",
                                       parse_mode="Markdown")
        except Exception:
            pass
