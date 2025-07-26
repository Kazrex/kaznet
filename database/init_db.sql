-- Пайдаланушылар кестесі (өзгеріссіз)
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    telegram_id INTEGER UNIQUE NOT NULL,
    username TEXT,
    full_name TEXT,
    selected_city TEXT
);

-- Хабарландырулар кестесі (ЖАҢА БАҒАНДАРМЕН)
CREATE TABLE IF NOT EXISTS ads (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    price TEXT NOT NULL,
    contact TEXT NOT NULL,
    photo_id TEXT,
    city TEXT NOT NULL,
    category TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- ЖАҢА БАҒАНДАР --
    expires_at TIMESTAMP NOT NULL,          -- Хабарландырудың өшетін уақыты
    is_top BOOLEAN DEFAULT 0,               -- ТОП статусы (1 - иә, 0 - жоқ)
    top_expires_at TIMESTAMP,               -- ТОП статусының бітетін уақыты
    status TEXT DEFAULT 'active',           -- Статус: active, pending_deletion, expired
    
    FOREIGN KEY (user_id) REFERENCES users (id)
);