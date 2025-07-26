import aiosqlite
import logging
from datetime import datetime, timedelta
from bot.config import DB_PATH

# ... (init_db, get_user, add_user, update_user_city функциялары өзгеріссіз қалады) ...

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


# --- ЖАҢАРТЫЛҒАН ЖӘНЕ ЖАҢА ФУНКЦИЯЛАР ---

async def add_ad_to_db(state_data):
    """Жаңа хабарландыруды дерекқорға қосады."""
    async with aiosqlite.connect(DB_PATH) as db:
        user_cursor = await db.execute("SELECT id FROM users WHERE telegram_id = ?", (state_data['user_id'],))
        user_db_id = (await user_cursor.fetchone())[0]

        expires_at = datetime.now() + timedelta(days=7)

        cursor = await db.execute(
            """INSERT INTO ads (user_id, title, description, price, contact, photo_id, city, category, expires_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                user_db_id,
                state_data['title'],
                state_data['description'],
                state_data['price'],
                state_data['contact'],
                state_data.get('photo'),
                state_data['city'],
                state_data['category'],
                expires_at
            )
        )
        await db.commit()
        return cursor.lastrowid

async def get_user_ads_from_db(telegram_id):
    """Пайдаланушының барлық хабарландыруларын алады (мерзімімен бірге)."""
    async with aiosqlite.connect(DB_PATH) as db:
        user_cursor = await db.execute("SELECT id FROM users WHERE telegram_id = ?", (telegram_id,))
        user_db_id_tuple = await user_cursor.fetchone()
        if not user_db_id_tuple:
            return []
        
        user_db_id = user_db_id_tuple[0]
        cursor = await db.execute(
            "SELECT title, price, created_at, expires_at FROM ads WHERE user_id = ? AND status = 'active' ORDER BY created_at DESC", 
            (user_db_id,)
        )
        return await cursor.fetchall()

async def get_ads_by_city_paginated(city: str, page: int = 1, page_size: int = 5):
    """Қала бойынша хабарландыруларды беттеп қайтарады (ТОП-тар бірінші)."""
    offset = (page - 1) * page_size
    async with aiosqlite.connect(DB_PATH) as db:
        total_cursor = await db.execute("SELECT COUNT(*) FROM ads WHERE city = ? AND status = 'active'", (city,))
        total_ads = (await total_cursor.fetchone())[0]
        
        ads_cursor = await db.execute(
            """SELECT id, title, description, price, contact, photo_id, is_top FROM ads 
               WHERE city = ? AND status = 'active' 
               ORDER BY is_top DESC, created_at DESC LIMIT ? OFFSET ?""",
            (city, page_size, offset)
        )
        ads = await ads_cursor.fetchall()
        
        return ads, total_ads

async def get_ads_for_expiry_check():
    """Мерзімі бітуге жақын немесе біткен хабарландыруларды алады."""
    now = datetime.now()
    one_hour_later = now + timedelta(hours=1)
    async with aiosqlite.connect(DB_PATH) as db:
        # Ескерту жіберетіндер (1 сағат қалды және әлі ескертілмеген)
        notify_cursor = await db.execute(
            """SELECT a.id, u.telegram_id, a.title FROM ads a
               JOIN users u ON a.user_id = u.id
               WHERE a.expires_at BETWEEN ? AND ? AND a.status = 'active'""",
            (now, one_hour_later)
        )
        ads_to_notify = await notify_cursor.fetchall()

        # Өшірілетіндер (мерзімі біткен)
        delete_cursor = await db.execute(
            """SELECT a.id, u.telegram_id, a.title FROM ads a
               JOIN users u ON a.user_id = u.id
               WHERE a.expires_at < ? AND a.status != 'expired'""",
            (now,)
        )
        ads_to_delete = await delete_cursor.fetchall()
        
        return ads_to_notify, ads_to_delete

async def update_ad_status(ad_id: int, status: str):
    """Хабарландыру статусын жаңартады."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE ads SET status = ? WHERE id = ?", (status, ad_id))
        await db.commit()

async def extend_ad(ad_id: int):
    """Хабарландыру мерзімін 7 күнге ұзартады."""
    new_expires_at = datetime.now() + timedelta(days=7)
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE ads SET expires_at = ?, status = 'active' WHERE id = ?", (new_expires_at, ad_id))
        await db.commit()

async def set_ad_top(ad_id: int, days: int):
    """Хабарландыруға ТОП статус береді."""
    top_expires_at = datetime.now() + timedelta(days=days)
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE ads SET is_top = 1, top_expires_at = ? WHERE id = ?",
            (top_expires_at, ad_id)
        )
        await db.commit()