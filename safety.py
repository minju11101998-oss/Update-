"""
Утилиты надёжности — используются во всех хендлерах.

Главный принцип: критичный шаг (списание/выдача награды) и
ответ пользователю должны быть РАЗДЕЛЕНЫ от необязательных шагов
(ачивки, квесты, дроп). Если необязательный шаг падает — пользователь
всё равно должен увидеть результат основного действия.
"""

import logging
import functools
import traceback

logger = logging.getLogger("safety")


async def safe_call(coro_func, *args, default=None, label="unknown", **kwargs):
    """
    Выполнить корутину безопасно. Если упадёт — залогировать и вернуть default.
    Использовать для НЕОБЯЗАТЕЛЬНЫХ шагов (ачивки, квесты, дроп, статистика).

    Пример:
        ach_msgs = await safe_call(check_achievements, db, uid, player,
                                    default=[], label="check_achievements")
    """
    try:
        return await coro_func(*args, **kwargs)
    except Exception as e:
        logger.error(f"[safe_call:{label}] {e}\n{traceback.format_exc()}")
        return default


def guard_handler(fallback_text: str = "⚠️ Произошла ошибка. Попробуй ещё раз."):
    """
    Декоратор для callback/command хендлеров.
    Гарантирует, что пользователь получит хоть какой-то ответ,
    даже если внутри хендлера вылетит необработанное исключение.

    Использование:
        @guard_handler()
        @staticmethod
        async def show(update, ctx):
            ...

    Работает и с update.message, и с update.callback_query.
    """
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(update, ctx, *args, **kwargs):
            try:
                return await func(update, ctx, *args, **kwargs)
            except Exception as e:
                logger.error(
                    f"[guard_handler:{func.__qualname__}] {e}\n{traceback.format_exc()}"
                )
                try:
                    if getattr(update, "callback_query", None):
                        await update.callback_query.answer(
                            fallback_text, show_alert=True)
                    elif getattr(update, "message", None):
                        await update.message.reply_text(fallback_text)
                except Exception:
                    # Если даже отправка ошибки не удалась — только лог
                    logger.error(
                        f"[guard_handler:{func.__qualname__}] failed to notify user")
        return wrapper
    return decorator


async def safe_notify_achievements(db, uid: int, player: dict) -> str:
    """
    Безопасно проверить ачивки и вернуть готовый текст-приставку
    (с двумя \\n перед собой) либо пустую строку.
    """
    try:
        from handlers.achievements import check_achievements
        msgs = await check_achievements(db, uid, player)
        return ("\n\n" + "\n".join(msgs)) if msgs else ""
    except Exception as e:
        logger.error(f"[safe_notify_achievements] {e}")
        return ""


async def safe_update_quests(db, uid: int, won: bool):
    """Безопасно обновить квесты после боя"""
    try:
        from handlers.quests import update_battle_quests
        await update_battle_quests(db, uid, won)
    except Exception as e:
        logger.error(f"[safe_update_quests] {e}")


async def safe_roll_drop(db, uid: int, level: int, is_winner: bool, is_bot: bool) -> str:
    """Безопасно выдать дроп предмета, вернуть готовый текст или пустую строку"""
    try:
        from handlers.loot import roll_drop, format_drop
        items = await roll_drop(db, uid, level, is_winner, is_bot)
        return format_drop(items)
    except Exception as e:
        logger.error(f"[safe_roll_drop] {e}")
        return ""


async def safe_roll_materials(db, uid: int, level: int, victory_token: bool = False) -> str:
    """Безопасно выдать материалы крафта, вернуть готовый текст или пустую строку"""
    try:
        from handlers.craft import roll_materials, format_materials, MATERIALS
        mats = await roll_materials(db, uid, level)
        if victory_token:
            await db.add_material(uid, "victory_token", 1)
            mats.append(MATERIALS["victory_token"]["name"])
        return format_materials(mats)
    except Exception as e:
        logger.error(f"[safe_roll_materials] {e}")
        return ""
