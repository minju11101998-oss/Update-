"""
Матчмейкинг с ограничением разницы уровней.
- Ищет противника с разницей уровней <= LEVEL_DIFF_MAX
- Если за MATCHMAKING_TIMEOUT секунд никого — бой с ботом
- Если разница уровней слишком большая — тоже бот
"""

import asyncio
import logging
from config import MATCHMAKING_TIMEOUT, MATCHMAKING_LEVEL_DIFF

logger = logging.getLogger(__name__)


class MatchmakingManager:
    def __init__(self, app):
        self.app  = app
        # user_id → {chat_id, level, task}
        self.queue: dict[int, dict] = {}

    def in_queue(self, user_id: int) -> bool:
        return user_id in self.queue

    async def add_to_queue(self, user_id: int, chat_id: int, level: int) -> int | None:
        """
        Добавить игрока в очередь.
        Ищет противника с разницей уровней <= MATCHMAKING_LEVEL_DIFF.
        Возвращает opponent_id если нашёл, иначе None (ждём таймер).
        """
        best_match    = None
        best_diff     = 999

        for waiting_id, info in list(self.queue.items()):
            if waiting_id == user_id:
                continue
            diff = abs(info["level"] - level)
            if diff <= MATCHMAKING_LEVEL_DIFF and diff < best_diff:
                best_match = waiting_id
                best_diff  = diff

        if best_match is not None:
            # Нашли подходящего противника
            self._cancel_timer(best_match)
            del self.queue[best_match]
            logger.info(
                f"Матч: {user_id}(Ур.{level}) vs {best_match}"
                f"(Ур.{self.queue.get(best_match, {}).get('level', '?')})"
                f" разница {best_diff}"
            )
            return best_match

        # Никого подходящего — встаём в очередь
        task = asyncio.create_task(
            self._timeout_task(user_id, chat_id)
        )
        self.queue[user_id] = {
            "chat_id": chat_id,
            "level":   level,
            "task":    task,
        }
        logger.info(f"Игрок {user_id}(Ур.{level}) в очереди. Всего: {len(self.queue)}")
        return None

    async def _timeout_task(self, user_id: int, chat_id: int):
        """Таймаут — бой с ботом"""
        await asyncio.sleep(MATCHMAKING_TIMEOUT)
        if user_id in self.queue:
            del self.queue[user_id]
            from handlers.battle import BattleHandler
            await BattleHandler.start_vs_bot(self.app, user_id, chat_id)

    def remove_from_queue(self, user_id: int):
        if user_id in self.queue:
            self._cancel_timer(user_id)
            del self.queue[user_id]

    def _cancel_timer(self, user_id: int):
        info = self.queue.get(user_id)
        if info and "task" in info:
            info["task"].cancel()

    def queue_size(self) -> int:
        return len(self.queue)

    def queue_info(self) -> list[dict]:
        """Для админ панели — список игроков в очереди"""
        return [
            {"user_id": uid, "level": info["level"]}
            for uid, info in self.queue.items()
        ]

