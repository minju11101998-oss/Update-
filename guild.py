"""Гильдии — /guild"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database import Database
from safety import guard_handler


class GuildHandler:

    @staticmethod
    @guard_handler()
    async def show(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        db: Database = ctx.bot_data["db"]
        uid = update.effective_user.id
        p   = await db.get_player(uid)
        if not p:
            await update.message.reply_text("Сначала /start"); return
        text, kb = await _build_menu(db, uid)
        await update.message.reply_text(text, parse_mode="Markdown", reply_markup=kb)

    @staticmethod
    @guard_handler()
    async def show_cb(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        q = update.callback_query; await q.answer()
        db: Database = ctx.bot_data["db"]
        text, kb = await _build_menu(db, q.from_user.id)
        await q.edit_message_text(text, parse_mode="Markdown", reply_markup=kb)

    @staticmethod
    @guard_handler()
    async def create(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        db: Database = ctx.bot_data["db"]
        uid  = update.effective_user.id
        args = ctx.args
        if not args:
            await update.message.reply_text(
                "Использование: /guild_create [название]\nПример: /guild_create Стражи")
            return
        name = " ".join(args)[:30]
        p    = await db.get_player(uid)
        if not p:
            await update.message.reply_text("Сначала /start"); return

        existing = await db.get_player_guild(uid)
        if existing:
            await update.message.reply_text(
                f"Ты уже в гильдии *{existing['name']}*. Сначала выйди: /guild_leave",
                parse_mode="Markdown"); return

        if p["gold"] < 500:
            await update.message.reply_text("❌ Создание гильдии стоит 500💰"); return

        ok = await db.create_guild(name, uid)
        if not ok:
            await update.message.reply_text("❌ Название занято!"); return

        await db.update_player(uid, gold=p["gold"] - 500)

        # Достижение
        from handlers.achievements import check_achievements
        p_new = await db.get_player(uid)
        p_new["_guild_created"] = True
        await db.grant_achievement(uid, "guild_founder")

        await update.message.reply_text(
            f"🏰 Гильдия *{name}* создана!\n💰 -500 золота\n\n"
            f"Расскажи друзьям: /guild_join {name}",
            parse_mode="Markdown")

    @staticmethod
    @guard_handler()
    async def join(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        db: Database = ctx.bot_data["db"]
        uid  = update.effective_user.id
        args = ctx.args
        if not args:
            await update.message.reply_text("Использование: /guild_join [название]"); return
        name = " ".join(args)

        existing = await db.get_player_guild(uid)
        if existing:
            await update.message.reply_text(
                f"Ты уже в гильдии *{existing['name']}*. Сначала выйди: /guild_leave",
                parse_mode="Markdown"); return

        guild = await db.get_guild_by_name(name)
        if not guild:
            await update.message.reply_text(f"❌ Гильдия «{name}» не найдена."); return

        members = await db.get_guild_members(guild["id"])
        if len(members) >= 20:
            await update.message.reply_text("❌ Гильдия переполнена (макс. 20)."); return

        await db.join_guild(uid, guild["id"])
        await update.message.reply_text(
            f"✅ Ты вступил в гильдию *{guild['name']}*!", parse_mode="Markdown")

    @staticmethod
    @guard_handler()
    async def leave(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        db: Database = ctx.bot_data["db"]
        uid   = update.effective_user.id
        guild = await db.get_player_guild(uid)
        if not guild:
            await update.message.reply_text("Ты не в гильдии."); return
        if guild["owner_id"] == uid:
            await update.message.reply_text(
                "Ты основатель — нельзя выйти. Передай права или расформируй гильдию."); return
        await db.leave_guild(uid)
        await update.message.reply_text(
            f"👋 Ты вышел из гильдии *{guild['name']}*.", parse_mode="Markdown")

    @staticmethod
    @guard_handler()
    async def top(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        db: Database = ctx.bot_data["db"]
        rows  = await db.get_guild_leaderboard(10)
        if not rows:
            await update.message.reply_text("Гильдий пока нет."); return
        medals = ["🥇","🥈","🥉"] + ["🔹"]*10
        lines  = ["🏰 *ТОП ГИЛЬДИЙ*\n"]
        for i, g in enumerate(rows):
            lines.append(f"{medals[i]} *{g['name']}* — {g['wins']} побед")
        await update.message.reply_text("\n".join(lines), parse_mode="Markdown")

    @staticmethod
    @guard_handler()
    async def info_cb(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        q = update.callback_query; await q.answer()
        db: Database = ctx.bot_data["db"]
        uid   = q.from_user.id
        guild = await db.get_player_guild(uid)
        if not guild:
            await q.edit_message_text("Ты не в гильдии."); return

        members = await db.get_guild_members(guild["id"])
        lines   = [
            f"🏰 *{guild['name']}*\n"
            f"🏆 Побед: {guild['wins']}\n"
            f"👥 Участников: {len(members)}/20\n\n"
            f"*Члены:*"
        ]
        for i, m in enumerate(members[:10], 1):
            crown = "👑 " if m["user_id"] == guild["owner_id"] else ""
            lines.append(f"{i}. {crown}{m['first_name']} Ур.{m['level']} | {m['mmr']}⭐")

        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("◀️ Назад", callback_data="guild_menu")]
        ])
        await q.edit_message_text("\n".join(lines), parse_mode="Markdown", reply_markup=kb)


async def _build_menu(db: Database, uid: int) -> tuple[str, InlineKeyboardMarkup]:
    guild = await db.get_player_guild(uid)
    if guild:
        members = await db.get_guild_members(guild["id"])
        txt = (
            f"🏰 *Моя гильдия: {guild['name']}*\n"
            f"👥 Участников: {len(members)}/20\n"
            f"🏆 Побед: {guild['wins']}"
        )
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("📋 Состав", callback_data="guild_info")],
            [InlineKeyboardButton("🏆 Топ гильдий", callback_data="guild_top_cb")],
            [InlineKeyboardButton("◀️ Профиль", callback_data="profile")],
        ])
    else:
        txt = (
            "🏰 *ГИЛЬДИИ*\n\n"
            "Ты не в гильдии.\n\n"
            "• /guild_create [название] — создать (500💰)\n"
            "• /guild_join [название] — вступить\n"
            "• /guild_top — топ гильдий"
        )
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("🏆 Топ гильдий", callback_data="guild_top_cb")],
            [InlineKeyboardButton("◀️ Профиль", callback_data="profile")],
        ])
    return txt, kb
