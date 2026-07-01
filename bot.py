"""⚔️ ARENA BATTLE — Полная версия"""

import logging
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    MessageHandler, filters,
)
from config import BOT_TOKEN
from database import Database
from handlers.start import StartHandler
from handlers.arena import ArenaHandler
from handlers.equipment import EquipmentHandler
from handlers.profile import ProfileHandler
from handlers.admin import AdminHandler
from handlers.changeclass import ClassChangeHandler
from handlers.battle import BattleHandler
from handlers.daily import DailyHandler
from handlers.achievements import AchievementsHandler
from handlers.quests import QuestsHandler
from handlers.guild import GuildHandler
from handlers.duel import DuelHandler
from handlers.passives import PassivesHandler
from handlers.enchant import EnchantHandler
from handlers.forge import ForgeHandler
from handlers.respec import RespecHandler
from handlers.shop import ShopHandler
from handlers.tournament import TournamentHandler
from handlers.stats_handler import StatsHandler
from matchmaking import MatchmakingManager

logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(message)s",
    level=logging.INFO
)


async def post_init(app: Application):
    db = Database()
    await db.init()
    await db._ensure_extra_tables()
    app.bot_data["db"] = db
    app.bot_data["matchmaking"] = MatchmakingManager(app)


def main():
    app = (
        Application.builder()
        .token(BOT_TOKEN)
        .post_init(post_init)
        .build()
    )

    # ── Команды ──────────────────────────────────────────────────────────────
    app.add_handler(CommandHandler("start",            StartHandler.handle))
    app.add_handler(CommandHandler("profile",          ProfileHandler.show))
    app.add_handler(CommandHandler("top",              ProfileHandler.leaderboard))
    app.add_handler(CommandHandler("arena",            ArenaHandler.enter))
    app.add_handler(CommandHandler("cancel",           ArenaHandler.cancel_search))
    app.add_handler(CommandHandler("equipment",        EquipmentHandler.show_shop))
    app.add_handler(CommandHandler("changeclass",      ClassChangeHandler.show))
    app.add_handler(CommandHandler("daily",            DailyHandler.claim))
    app.add_handler(CommandHandler("achievements",     AchievementsHandler.show))
    app.add_handler(CommandHandler("quests",           QuestsHandler.show))
    app.add_handler(CommandHandler("guild",            GuildHandler.show))
    app.add_handler(CommandHandler("guild_create",     GuildHandler.create))
    app.add_handler(CommandHandler("guild_join",       GuildHandler.join))
    app.add_handler(CommandHandler("guild_leave",      GuildHandler.leave))
    app.add_handler(CommandHandler("guild_top",        GuildHandler.top))
    app.add_handler(CommandHandler("duel",             DuelHandler.send))
    app.add_handler(CommandHandler("passives",         PassivesHandler.show))
    app.add_handler(CommandHandler("enchant",          EnchantHandler.show))
    app.add_handler(CommandHandler("forge",            ForgeHandler.show))
    app.add_handler(CommandHandler("respec",           RespecHandler.show))
    app.add_handler(CommandHandler("shop",             ShopHandler.show))
    app.add_handler(CommandHandler("tournament",       TournamentHandler.show))
    app.add_handler(CommandHandler("tournament_start", TournamentHandler.start_registration))
    app.add_handler(CommandHandler("mystats",          StatsHandler.show))
    app.add_handler(CommandHandler("history",          StatsHandler.history))
    # Админ
    app.add_handler(CommandHandler("admin",            AdminHandler.panel))
    app.add_handler(CommandHandler("give_gold",        AdminHandler.give_gold))
    app.add_handler(CommandHandler("ban",              AdminHandler.ban_user))
    app.add_handler(CommandHandler("unban",            AdminHandler.unban_user))
    app.add_handler(CommandHandler("broadcast",        AdminHandler.broadcast))
    app.add_handler(CommandHandler("stats",            AdminHandler.bot_stats))
    app.add_handler(CommandHandler("set_level",        AdminHandler.set_level))

    # ── Callbacks ────────────────────────────────────────────────────────────
    # Регистрация
    app.add_handler(CallbackQueryHandler(StartHandler.class_select,        pattern="^class:"))
    # Смена класса
    app.add_handler(CallbackQueryHandler(ClassChangeHandler.show_cb,       pattern="^changeclass$"))
    app.add_handler(CallbackQueryHandler(ClassChangeHandler.preview,        pattern="^cc_view:"))
    app.add_handler(CallbackQueryHandler(ClassChangeHandler.confirm,        pattern="^cc_confirm:"))
    # Экипировка
    app.add_handler(CallbackQueryHandler(EquipmentHandler.show_inventory,   pattern="^inventory$"))
    app.add_handler(CallbackQueryHandler(EquipmentHandler.show_slot,        pattern="^slot:"))
    app.add_handler(CallbackQueryHandler(EquipmentHandler.buy_item,         pattern="^buy:"))
    app.add_handler(CallbackQueryHandler(EquipmentHandler.equip_item,       pattern="^equip:"))
    app.add_handler(CallbackQueryHandler(EquipmentHandler.unequip_item,     pattern="^unequip:"))
    # Бой
    app.add_handler(CallbackQueryHandler(BattleHandler.action,              pattern="^battle:"))
    # Арена / Профиль
    app.add_handler(CallbackQueryHandler(ArenaHandler.enter_cb,             pattern="^arena$"))
    app.add_handler(CallbackQueryHandler(ProfileHandler.show_cb,            pattern="^profile$"))
    # Достижения / Квесты
    app.add_handler(CallbackQueryHandler(AchievementsHandler.show_cb,       pattern="^achievements$"))
    app.add_handler(CallbackQueryHandler(QuestsHandler.show_cb,             pattern="^quests$"))
    app.add_handler(CallbackQueryHandler(QuestsHandler.claim,               pattern="^quest_claim:"))
    # Гильдии
    app.add_handler(CallbackQueryHandler(GuildHandler.show_cb,              pattern="^guild_menu$"))
    app.add_handler(CallbackQueryHandler(GuildHandler.info_cb,              pattern="^guild_info$"))
    # Дуэли
    app.add_handler(CallbackQueryHandler(DuelHandler.accept,                pattern="^duel_accept:"))
    app.add_handler(CallbackQueryHandler(DuelHandler.decline,               pattern="^duel_decline:"))
    # Пассивки
    app.add_handler(CallbackQueryHandler(PassivesHandler.show_cb,           pattern="^passives$"))
    app.add_handler(CallbackQueryHandler(PassivesHandler.choose,            pattern="^passive_choose:"))
    # Зачарования
    app.add_handler(CallbackQueryHandler(EnchantHandler.show_cb,            pattern="^enchant_menu$"))
    app.add_handler(CallbackQueryHandler(EnchantHandler.choose_slot,        pattern="^enchant_slot:"))
    app.add_handler(CallbackQueryHandler(EnchantHandler.apply,              pattern="^enchant_apply:"))
    # Кузница
    app.add_handler(CallbackQueryHandler(ForgeHandler.show_cb,              pattern="^forge_menu$"))
    app.add_handler(CallbackQueryHandler(ForgeHandler.upgrade,              pattern="^forge_up:"))
    # Перековка
    app.add_handler(CallbackQueryHandler(RespecHandler.show_cb,             pattern="^respec_menu$"))
    app.add_handler(CallbackQueryHandler(RespecHandler.add_point,           pattern="^respec_add:"))
    app.add_handler(CallbackQueryHandler(RespecHandler.remove_point,        pattern="^respec_rm:"))
    app.add_handler(CallbackQueryHandler(RespecHandler.confirm,             pattern="^respec_confirm$"))
    app.add_handler(CallbackQueryHandler(RespecHandler.reset,               pattern="^respec_reset$"))
    # Магазин
    app.add_handler(CallbackQueryHandler(ShopHandler.show_cb,               pattern="^shop_menu$"))
    app.add_handler(CallbackQueryHandler(ShopHandler.buy,                   pattern="^shop_buy:"))
    app.add_handler(CallbackQueryHandler(ShopHandler.my_items,              pattern="^shop_items$"))
    # Турнир
    app.add_handler(CallbackQueryHandler(TournamentHandler.show,            pattern="^tournament_menu$"))
    app.add_handler(CallbackQueryHandler(TournamentHandler.register,        pattern="^tournament_reg$"))
    # Статистика
    app.add_handler(CallbackQueryHandler(StatsHandler.show_cb,              pattern="^mystats$"))
    app.add_handler(CallbackQueryHandler(StatsHandler.history_cb,           pattern="^history$"))
    # Админ
    app.add_handler(CallbackQueryHandler(AdminHandler.panel_cb,             pattern="^admin:"))
    app.add_handler(CallbackQueryHandler(AdminHandler.confirm_broadcast,    pattern="^broadcast_confirm$"))
    # Текст
    app.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND, AdminHandler.handle_broadcast_text
    ))

    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
