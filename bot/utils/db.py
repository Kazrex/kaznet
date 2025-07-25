import aiosqlite
import logging
from bot.config import DB_PATH

async def init_db():
    """Дерекқорды және кестелерді құрады."""
    async with aiosqlite.connect(DB_PATH) as db:
        with open("database/init_db.sql", "r") as f:
            await db.executescript(f.read())
        await db.commit()
    logging.info("Database initialized.")

async def get_user(telegram_id):
    """Пайдаланушыны telegram_id бойынша табады."""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("SELECT * FROM users WHERE telegram_id = ?", (telegram_id,))
        return await cursor.fetchone()

async def add_user(telegram_id, username, full_name):
    """Жаңа пайдаланушыны қосады."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT OR IGNORE INTO users (telegram_id, username, full_name) VALUES (?, ?, ?)",
            (telegram_id, username, full_name)
        )
        await db.commit()

async def update_user_city(telegram_id, city):
    """Пайдаланушының таңдаған қаласын жаңартады."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE users SET selected_city = ? WHERE telegram_id = ?", (city, telegram_id))
        await db.commit()

async def add_ad_to_db(state_data):
    """Жаңа хабарландыруды дерекқорға қосады."""
    async with aiosqlite.connect(DB_PATH) as db:
        user_cursor = await db.execute("SELECT id FROM users WHERE telegram_id = ?", (state_data['user_id'],))
        user_db_id = (await user_cursor.fetchone())[0]

        await db.execute(
            """INSERT INTO ads (user_id, title, description, price, contact, photo_id, city, category)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                user_db_id,
                state_data['title'],
                state_data['description'],
                state_data['price'],
                state_data['contact'],
                state_data.get('photo'), # Фото болмауы мүмкін
                state_data['city'],
                state_data['category']
            )
        )
        await db.commit()

async def get_user_ads_from_db(telegram_id):
    """Пайдаланушының барлық хабарландыруларын алады."""
    async with aiosqlite.connect(DB_PATH) as db:
        user_cursor = await db.execute("SELECT id FROM users WHERE telegram_id = ?", (telegram_id,))
        user_db_id_tuple = await user_cursor.fetchone()
        if not user_db_id_tuple:
            return []
        
        user_db_id = user_db_id_tuple[0]
        cursor = await db.execute("SELECT title, description, price, created_at FROM ads WHERE user_id = ? ORDER BY created_at DESC", (user_db_id,))
        return await cursor.fetchall()