import sqlite3

# Initialize database
def init_db():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    # Ads Table
    cursor.execute('''CREATE TABLE IF NOT EXISTS ads (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        content_type TEXT NOT NULL,
        content TEXT NOT NULL
    )''')

    # Groups/Channels Table
    cursor.execute('''CREATE TABLE IF NOT EXISTS groups_channels (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        chat_id INTEGER NOT NULL,
        name TEXT NOT NULL
    )''')

    # Collected Posts Table
    cursor.execute('''CREATE TABLE IF NOT EXISTS collected_posts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        group_name TEXT,
        post_content TEXT,
        is_reviewed INTEGER DEFAULT 0
    )''')

    conn.commit()
    conn.close()

# Ad Management Functions
def add_ad(content_type, content):
    conn = sqlite3.connect('ads_bot.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO ads (content_type, content) VALUES (?, ?)", (content_type, content))
    conn.commit()
    conn.close()

def fetch_ads():
    conn = sqlite3.connect('ads_bot.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM ads")
    ads = cursor.fetchall()
    conn.close()
    return ads

def delete_ad(ad_id):
    conn = sqlite3.connect('ads_bot.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM ads WHERE id = ?", (ad_id,))
    conn.commit()
    conn.close()

# Group/Channel Management Functions
def add_group_channel(chat_id, name):
    conn = sqlite3.connect('ads_bot.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO groups_channels (chat_id, name) VALUES (?, ?)", (chat_id, name))
    conn.commit()
    conn.close()

def fetch_groups():
    conn = sqlite3.connect('ads_bot.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM groups_channels")
    groups = cursor.fetchall()
    conn.close()
    return groups

# Post Collection Functions
def add_collected_post(group_name, post_content):
    conn = sqlite3.connect('ads_bot.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO collected_posts (group_name, post_content) VALUES (?, ?)", (group_name, post_content))
    conn.commit()
    conn.close()

def fetch_collected_posts():
    conn = sqlite3.connect('ads_bot.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM collected_posts WHERE is_reviewed = 0")
    posts = cursor.fetchall()
    conn.close()
    return posts

def mark_post_reviewed(post_id):
    conn = sqlite3.connect('ads_bot.db')
    cursor = conn.cursor()
    cursor.execute("UPDATE collected_posts SET is_reviewed = 1 WHERE id = ?", (post_id,))
    conn.commit()
    conn.close()
