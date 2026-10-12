import aiosqlite
import time
from config import DB_PATH

ALL_INTERESTS = [
    "Ролевые игры", "Мемы",
    "Одиночество", "Флирт",
    "Игры", "Музыка",
    "Путешествия", "Аниме",
    "Фильмы", "Питомцы",
    "Книги", "Спорт"
]

async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                gender TEXT DEFAULT NULL,
                target_gender TEXT DEFAULT 'ANY',
                interests TEXT DEFAULT '',
                is_banned INTEGER DEFAULT 0,
                is_vip INTEGER DEFAULT 0,
                is_premium INTEGER DEFAULT 0,
                premium_till INTEGER DEFAULT 0,
                vip_till INTEGER DEFAULT 0,
                companion_id INTEGER DEFAULT 0,
                last_companion_id INTEGER DEFAULT 0,
                state TEXT DEFAULT 'idle',
                total_chats INTEGER DEFAULT 0,
                likes INTEGER DEFAULT 0,
                dislikes INTEGER DEFAULT 0,
                reports_count INTEGER DEFAULT 0,
                joined_at INTEGER
            )
        """)
        # Миграция колонок если их еще нет
        for col, col_type in [
            ("interests", "TEXT DEFAULT ''"),
            ("last_companion_id", "INTEGER DEFAULT 0"),
            ("likes", "INTEGER DEFAULT 0"),
            ("dislikes", "INTEGER DEFAULT 0"),
            ("is_premium", "INTEGER DEFAULT 0"),
            ("premium_till", "INTEGER DEFAULT 0"),
            ("vip_till", "INTEGER DEFAULT 0"),
        ]:
            try:
                await db.execute(f"ALTER TABLE users ADD COLUMN {col} {col_type}")
            except Exception:
                pass
        await db.commit()

async def get_user(user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM users WHERE user_id = ?", (user_id,)) as cursor:
            return await cursor.fetchone()

async def create_user(user_id: int, username: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            INSERT OR IGNORE INTO users (user_id, username, joined_at)
            VALUES (?, ?, ?)
        """, (user_id, username, int(time.time())))
        await db.commit()

async def update_user(user_id: int, **kwargs):
    if not kwargs:
        return
    fields = ", ".join([f"{k} = ?" for k in kwargs.keys()])
    values = list(kwargs.values()) + [user_id]
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(f"UPDATE users SET {fields} WHERE user_id = ?", values)
        await db.commit()

async def grant_subscription(user_id: int, days: int = None, is_vip: bool = False):
    user = await get_user(user_id)
    now = int(time.time())
    if is_vip:
        await update_user(user_id, is_vip=1, is_premium=1, vip_till=now + 3650 * 86400)
    elif days:
        current_till = user["premium_till"] if user and user["premium_till"] else now
        base = max(now, current_till)
        new_till = base + days * 86400
        await update_user(user_id, is_premium=1, premium_till=new_till)

async def toggle_interest(user_id: int, interest: str):
    user = await get_user(user_id)
    if not user:
        return []
    current = [i.strip() for i in (user["interests"] or "").split(",") if i.strip()]
    if interest in current:
        current.remove(interest)
    else:
        current.append(interest)
    new_str = ",".join(current)
    await update_user(user_id, interests=new_str)
    return current

async def clear_interests(user_id: int):
    await update_user(user_id, interests="")

async def find_companion(user_id: int, user_gender: str, target_gender: str, user_interests: list):
    """
    Подбор собеседника с приоритетом общих интересов и VIP:
    """
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row

        query = """
            SELECT user_id, gender, target_gender, interests, is_vip, is_premium FROM users
            WHERE state = 'searching'
              AND user_id != ?
              AND is_banned = 0
        """
        params = [user_id]

        if target_gender != 'ANY':
            query += " AND gender = ?"
            params.append(target_gender)

        if user_gender != 'ANY' and user_gender is not None:
            query += " AND (target_gender = 'ANY' OR target_gender = ?)"
            params.append(user_gender)

        async with db.execute(query, params) as cursor:
            candidates = await cursor.fetchall()

        if not candidates:
            return None

        # Ранжируем кандидатов: сначала VIP/Premium, затем максимальное совпадение интересов
        user_int_set = set(user_interests)

        def score(cand):
            cand_ints = set([i.strip() for i in (cand["interests"] or "").split(",") if i.strip()])
            common = len(user_int_set.intersection(cand_ints))
            vip_boost = 100 if (cand["is_vip"] or cand["is_premium"]) else 0
            return (vip_boost + common)

        best_cand = max(candidates, key=score)
        return best_cand

async def connect_users(u1: int, u2: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE users SET state = 'chatting', companion_id = ?, last_companion_id = ?, total_chats = total_chats + 1 WHERE user_id = ?", (u2, u2, u1))
        await db.execute("UPDATE users SET state = 'chatting', companion_id = ?, last_companion_id = ?, total_chats = total_chats + 1 WHERE user_id = ?", (u1, u1, u2))
        await db.commit()

async def disconnect_users(u1: int, u2: int = None):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE users SET state = 'idle', companion_id = 0 WHERE user_id = ?", (u1,))
        if u2:
            await db.execute("UPDATE users SET state = 'idle', companion_id = 0 WHERE user_id = ?", (u2,))
        await db.commit()

async def rate_user(target_id: int, is_like: bool):
    col = "likes" if is_like else "dislikes"
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(f"UPDATE users SET {col} = {col} + 1 WHERE user_id = ?", (target_id,))
        await db.commit()

async def report_user(target_id: int, reason: str = "general"):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE users SET reports_count = reports_count + 1 WHERE user_id = ?", (target_id,))
        # Автобан после 5 жалоб
        await db.execute("UPDATE users SET is_banned = 1 WHERE user_id = ? AND reports_count >= 5", (target_id,))
        await db.commit()
