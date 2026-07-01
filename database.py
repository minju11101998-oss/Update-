"""База данных — SQLite через aiosqlite"""

import aiosqlite
import json
import time
from config import DB_PATH


class Database:
    def __init__(self):
        self.path = DB_PATH
        self._db: aiosqlite.Connection | None = None

    async def init(self):
        self._db = await aiosqlite.connect(self.path)
        self._db.row_factory = aiosqlite.Row
        await self._create_tables()
        await self._migrate()

    async def _create_tables(self):
        await self._db.executescript("""
        CREATE TABLE IF NOT EXISTS players (
            user_id           INTEGER PRIMARY KEY,
            username          TEXT,
            first_name        TEXT,
            class_id          TEXT DEFAULT 'warrior',
            level             INTEGER DEFAULT 1,
            exp               INTEGER DEFAULT 0,
            gold              INTEGER DEFAULT 200,
            wins              INTEGER DEFAULT 0,
            losses            INTEGER DEFAULT 0,
            mmr               INTEGER DEFAULT 1000,
            streak            INTEGER DEFAULT 0,
            is_banned         INTEGER DEFAULT 0,
            last_class_change INTEGER DEFAULT 0,
            last_daily        INTEGER DEFAULT 0,
            daily_streak      INTEGER DEFAULT 0,
            last_battle       INTEGER DEFAULT 0,
            passive_id        TEXT DEFAULT '',
            title_id          TEXT DEFAULT '',
            created_at        DATETIME DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS equipment_slots (
            user_id  INTEGER,
            slot     TEXT,
            item_id  TEXT,
            PRIMARY KEY (user_id, slot)
        );

        CREATE TABLE IF NOT EXISTS inventory (
            id       INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id  INTEGER,
            item_id  TEXT
        );

        CREATE TABLE IF NOT EXISTS consumables (
            user_id  INTEGER,
            item_id  TEXT,
            amount   INTEGER DEFAULT 0,
            PRIMARY KEY (user_id, item_id)
        );

        CREATE TABLE IF NOT EXISTS enchantments (
            user_id  INTEGER,
            slot     TEXT,
            ench_id  TEXT,
            PRIMARY KEY (user_id, slot)
        );

        CREATE TABLE IF NOT EXISTS battles (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            player1_id INTEGER,
            player2_id INTEGER,
            winner_id  INTEGER,
            rounds     INTEGER,
            is_bot     INTEGER DEFAULT 0,
            log        TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS achievements (
            user_id  INTEGER,
            ach_id   TEXT,
            earned_at INTEGER DEFAULT 0,
            PRIMARY KEY (user_id, ach_id)
        );

        CREATE TABLE IF NOT EXISTS guilds (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            name      TEXT UNIQUE,
            owner_id  INTEGER,
            wins      INTEGER DEFAULT 0,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS guild_members (
            user_id  INTEGER PRIMARY KEY,
            guild_id INTEGER
        );

        CREATE TABLE IF NOT EXISTS quests (
            user_id    INTEGER,
            quest_id   TEXT,
            progress   INTEGER DEFAULT 0,
            completed  INTEGER DEFAULT 0,
            claimed    INTEGER DEFAULT 0,
            PRIMARY KEY (user_id, quest_id)
        );

        CREATE TABLE IF NOT EXISTS duel_requests (
            from_id    INTEGER,
            to_id      INTEGER,
            created_at INTEGER,
            PRIMARY KEY (from_id, to_id)
        );
        """)
        await self._db.commit()

    async def _migrate(self):
        """Безопасно добавить новые колонки в существующую БД"""
        new_cols = [
            ("players", "mmr",               "INTEGER DEFAULT 1000"),
            ("players", "streak",             "INTEGER DEFAULT 0"),
            ("players", "last_daily",         "INTEGER DEFAULT 0"),
            ("players", "daily_streak",       "INTEGER DEFAULT 0"),
            ("players", "last_battle",        "INTEGER DEFAULT 0"),
            ("players", "passive_id",         "TEXT DEFAULT ''"),
            ("players", "title_id",           "TEXT DEFAULT ''"),
            ("players", "last_class_change",  "INTEGER DEFAULT 0"),
            ("battles", "is_bot",             "INTEGER DEFAULT 0"),
        ]
        for table, col, definition in new_cols:
            try:
                await self._db.execute(
                    f"ALTER TABLE {table} ADD COLUMN {col} {definition}")
                await self._db.commit()
            except Exception:
                pass

    # ── Игрок ────────────────────────────────────────────────────────────────

    async def get_player(self, uid: int) -> dict | None:
        async with self._db.execute(
            "SELECT * FROM players WHERE user_id = ?", (uid,)
        ) as cur:
            row = await cur.fetchone()
            return dict(row) if row else None

    async def create_player(self, uid: int, username: str, first_name: str, class_id: str):
        await self._db.execute(
            """INSERT OR IGNORE INTO players
               (user_id, username, first_name, class_id, gold, mmr)
               VALUES (?, ?, ?, ?, 200, 1000)""",
            (uid, username, first_name, class_id)
        )
        await self._db.commit()

    async def update_player(self, uid: int, **kwargs):
        if not kwargs: return
        sets = ", ".join(f"{k} = ?" for k in kwargs)
        vals = list(kwargs.values()) + [uid]
        await self._db.execute(f"UPDATE players SET {sets} WHERE user_id = ?", vals)
        await self._db.commit()

    async def get_leaderboard_mmr(self, limit: int = 10) -> list[dict]:
        async with self._db.execute(
            """SELECT user_id, username, first_name, level, mmr, wins, losses
               FROM players WHERE is_banned = 0
               ORDER BY mmr DESC, wins DESC LIMIT ?""", (limit,)
        ) as cur:
            return [dict(r) for r in await cur.fetchall()]

    async def get_leaderboard_wins(self, limit: int = 10) -> list[dict]:
        async with self._db.execute(
            """SELECT user_id, username, first_name, level, wins, losses, mmr
               FROM players WHERE is_banned = 0
               ORDER BY wins DESC, level DESC LIMIT ?""", (limit,)
        ) as cur:
            return [dict(r) for r in await cur.fetchall()]

    async def get_all_players(self) -> list[dict]:
        async with self._db.execute(
            "SELECT * FROM players WHERE is_banned = 0"
        ) as cur:
            return [dict(r) for r in await cur.fetchall()]

    async def count_players(self) -> int:
        async with self._db.execute("SELECT COUNT(*) FROM players") as cur:
            return (await cur.fetchone())[0]

    async def count_battles(self) -> int:
        async with self._db.execute("SELECT COUNT(*) FROM battles") as cur:
            return (await cur.fetchone())[0]

    # ── Экипировка ───────────────────────────────────────────────────────────

    async def get_equipped(self, uid: int) -> dict:
        async with self._db.execute(
            "SELECT slot, item_id FROM equipment_slots WHERE user_id = ?", (uid,)
        ) as cur:
            return {r["slot"]: r["item_id"] for r in await cur.fetchall()}

    async def equip_item(self, uid: int, slot: str, item_id: str):
        await self._db.execute(
            """INSERT INTO equipment_slots (user_id, slot, item_id) VALUES (?, ?, ?)
               ON CONFLICT(user_id, slot) DO UPDATE SET item_id = excluded.item_id""",
            (uid, slot, item_id)
        )
        await self._db.commit()

    async def unequip_item(self, uid: int, slot: str):
        await self._db.execute(
            "DELETE FROM equipment_slots WHERE user_id = ? AND slot = ?", (uid, slot))
        await self._db.commit()

    async def add_to_inventory(self, uid: int, item_id: str):
        await self._db.execute(
            "INSERT INTO inventory (user_id, item_id) VALUES (?, ?)", (uid, item_id))
        await self._db.commit()

    async def get_inventory(self, uid: int) -> list[str]:
        async with self._db.execute(
            "SELECT item_id FROM inventory WHERE user_id = ?", (uid,)
        ) as cur:
            return [r["item_id"] for r in await cur.fetchall()]

    async def has_item(self, uid: int, item_id: str) -> bool:
        async with self._db.execute(
            "SELECT 1 FROM inventory WHERE user_id = ? AND item_id = ? LIMIT 1",
            (uid, item_id)
        ) as cur:
            return bool(await cur.fetchone())

    # ── Зачарования ──────────────────────────────────────────────────────────

    async def get_enchantments(self, uid: int) -> dict:
        async with self._db.execute(
            "SELECT slot, ench_id FROM enchantments WHERE user_id = ?", (uid,)
        ) as cur:
            return {r["slot"]: r["ench_id"] for r in await cur.fetchall()}

    async def set_enchantment(self, uid: int, slot: str, ench_id: str):
        await self._db.execute(
            """INSERT INTO enchantments (user_id, slot, ench_id) VALUES (?, ?, ?)
               ON CONFLICT(user_id, slot) DO UPDATE SET ench_id = excluded.ench_id""",
            (uid, slot, ench_id))
        await self._db.commit()

    # ── Расходники ───────────────────────────────────────────────────────────

    async def get_consumables(self, uid: int) -> dict:
        async with self._db.execute(
            "SELECT item_id, amount FROM consumables WHERE user_id = ? AND amount > 0",
            (uid,)
        ) as cur:
            return {r["item_id"]: r["amount"] for r in await cur.fetchall()}

    async def add_consumable(self, uid: int, item_id: str, amount: int = 1):
        await self._db.execute(
            """INSERT INTO consumables (user_id, item_id, amount) VALUES (?, ?, ?)
               ON CONFLICT(user_id, item_id) DO UPDATE SET amount = amount + ?""",
            (uid, item_id, amount, amount))
        await self._db.commit()

    async def use_consumable(self, uid: int, item_id: str) -> bool:
        async with self._db.execute(
            "SELECT amount FROM consumables WHERE user_id = ? AND item_id = ?",
            (uid, item_id)
        ) as cur:
            row = await cur.fetchone()
        if not row or row["amount"] <= 0:
            return False
        await self._db.execute(
            "UPDATE consumables SET amount = amount - 1 WHERE user_id = ? AND item_id = ?",
            (uid, item_id))
        await self._db.commit()
        return True

    # ── Достижения ───────────────────────────────────────────────────────────

    async def get_achievements(self, uid: int) -> list[str]:
        async with self._db.execute(
            "SELECT ach_id FROM achievements WHERE user_id = ?", (uid,)
        ) as cur:
            return [r["ach_id"] for r in await cur.fetchall()]

    async def grant_achievement(self, uid: int, ach_id: str) -> bool:
        """Выдать достижение. Возвращает True если новое."""
        async with self._db.execute(
            "SELECT 1 FROM achievements WHERE user_id = ? AND ach_id = ?",
            (uid, ach_id)
        ) as cur:
            if await cur.fetchone():
                return False
        await self._db.execute(
            "INSERT INTO achievements (user_id, ach_id, earned_at) VALUES (?, ?, ?)",
            (uid, ach_id, int(time.time())))
        await self._db.commit()
        return True

    # ── Бои ──────────────────────────────────────────────────────────────────

    async def save_battle(self, p1: int, p2: int, winner: int,
                          rounds: int, log: list, is_bot: bool = False):
        await self._db.execute(
            """INSERT INTO battles
               (player1_id, player2_id, winner_id, rounds, is_bot, log)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (p1, p2, winner, rounds, int(is_bot),
             json.dumps(log, ensure_ascii=False)))
        await self._db.commit()

    async def get_last_battles(self, uid: int, limit: int = 5) -> list[dict]:
        async with self._db.execute(
            """SELECT * FROM battles
               WHERE player1_id = ? OR player2_id = ?
               ORDER BY created_at DESC LIMIT ?""",
            (uid, uid, limit)
        ) as cur:
            return [dict(r) for r in await cur.fetchall()]

    # ── Квесты ───────────────────────────────────────────────────────────────

    async def get_quests(self, uid: int) -> dict:
        async with self._db.execute(
            "SELECT quest_id, progress, completed, claimed FROM quests WHERE user_id = ?",
            (uid,)
        ) as cur:
            return {r["quest_id"]: dict(r) for r in await cur.fetchall()}

    async def update_quest(self, uid: int, quest_id: str, progress: int,
                           completed: int = 0):
        await self._db.execute(
            """INSERT INTO quests (user_id, quest_id, progress, completed)
               VALUES (?, ?, ?, ?)
               ON CONFLICT(user_id, quest_id)
               DO UPDATE SET progress = ?, completed = ?""",
            (uid, quest_id, progress, completed, progress, completed))
        await self._db.commit()

    async def claim_quest(self, uid: int, quest_id: str):
        await self._db.execute(
            "UPDATE quests SET claimed = 1 WHERE user_id = ? AND quest_id = ?",
            (uid, quest_id))
        await self._db.commit()

    # ── Гильдии ──────────────────────────────────────────────────────────────

    async def create_guild(self, name: str, owner_id: int) -> bool:
        try:
            await self._db.execute(
                "INSERT INTO guilds (name, owner_id) VALUES (?, ?)",
                (name, owner_id))
            cur = await self._db.execute("SELECT last_insert_rowid()")
            gid = (await cur.fetchone())[0]
            await self._db.execute(
                "INSERT OR REPLACE INTO guild_members (user_id, guild_id) VALUES (?, ?)",
                (owner_id, gid))
            await self._db.commit()
            return True
        except Exception:
            return False

    async def get_guild(self, guild_id: int) -> dict | None:
        async with self._db.execute(
            "SELECT * FROM guilds WHERE id = ?", (guild_id,)
        ) as cur:
            row = await cur.fetchone()
            return dict(row) if row else None

    async def get_guild_by_name(self, name: str) -> dict | None:
        async with self._db.execute(
            "SELECT * FROM guilds WHERE name = ?", (name,)
        ) as cur:
            row = await cur.fetchone()
            return dict(row) if row else None

    async def get_player_guild(self, uid: int) -> dict | None:
        async with self._db.execute(
            """SELECT g.* FROM guilds g
               JOIN guild_members gm ON g.id = gm.guild_id
               WHERE gm.user_id = ?""", (uid,)
        ) as cur:
            row = await cur.fetchone()
            return dict(row) if row else None

    async def join_guild(self, uid: int, guild_id: int):
        await self._db.execute(
            "INSERT OR REPLACE INTO guild_members (user_id, guild_id) VALUES (?, ?)",
            (uid, guild_id))
        await self._db.commit()

    async def leave_guild(self, uid: int):
        await self._db.execute(
            "DELETE FROM guild_members WHERE user_id = ?", (uid,))
        await self._db.commit()

    async def get_guild_members(self, guild_id: int) -> list[dict]:
        async with self._db.execute(
            """SELECT p.user_id, p.first_name, p.level, p.wins, p.mmr
               FROM players p
               JOIN guild_members gm ON p.user_id = gm.user_id
               WHERE gm.guild_id = ?
               ORDER BY p.mmr DESC""", (guild_id,)
        ) as cur:
            return [dict(r) for r in await cur.fetchall()]

    async def get_guild_leaderboard(self, limit: int = 10) -> list[dict]:
        async with self._db.execute(
            "SELECT * FROM guilds ORDER BY wins DESC LIMIT ?", (limit,)
        ) as cur:
            return [dict(r) for r in await cur.fetchall()]

    async def update_guild(self, guild_id: int, **kwargs):
        if not kwargs: return
        sets = ", ".join(f"{k} = ?" for k in kwargs)
        vals = list(kwargs.values()) + [guild_id]
        await self._db.execute(f"UPDATE guilds SET {sets} WHERE id = ?", vals)
        await self._db.commit()

    # ── Дуэли ────────────────────────────────────────────────────────────────

    async def create_duel(self, from_id: int, to_id: int):
        await self._db.execute(
            """INSERT OR REPLACE INTO duel_requests (from_id, to_id, created_at)
               VALUES (?, ?, ?)""",
            (from_id, to_id, int(time.time())))
        await self._db.commit()

    async def get_duel(self, from_id: int, to_id: int) -> dict | None:
        async with self._db.execute(
            "SELECT * FROM duel_requests WHERE from_id = ? AND to_id = ?",
            (from_id, to_id)
        ) as cur:
            row = await cur.fetchone()
            return dict(row) if row else None

    async def delete_duel(self, from_id: int, to_id: int):
        await self._db.execute(
            "DELETE FROM duel_requests WHERE from_id = ? AND to_id = ?",
            (from_id, to_id))
        await self._db.commit()

    # ── Кузница ──────────────────────────────────────────────────────────────

    async def get_forges(self, uid: int) -> dict:
        try:
            async with self._db.execute(
                "SELECT slot, level FROM forge WHERE user_id = ?", (uid,)
            ) as cur:
                return {r["slot"]: r["level"] for r in await cur.fetchall()}
        except Exception:
            return {}

    async def set_forge(self, uid: int, slot: str, level: int):
        await self._db.execute(
            """INSERT INTO forge (user_id, slot, level) VALUES (?, ?, ?)
               ON CONFLICT(user_id, slot) DO UPDATE SET level = excluded.level""",
            (uid, slot, level))
        await self._db.commit()

    async def _ensure_extra_tables(self):
        await self._db.executescript("""
        CREATE TABLE IF NOT EXISTS forge (
            user_id INTEGER,
            slot    TEXT,
            level   INTEGER DEFAULT 0,
            PRIMARY KEY (user_id, slot)
        );
        """)
        # Колонки для перековки
        for col in ["respec_str", "respec_end", "respec_agi", "respec_int"]:
            try:
                await self._db.execute(
                    f"ALTER TABLE players ADD COLUMN {col} INTEGER DEFAULT 0")
            except Exception:
                pass
        await self._db.commit()
