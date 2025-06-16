import sqlite3
import datetime
import json


def init_db():
    """
    """
    conn = sqlite3.connect("rd_users.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
                   id INTEGER PRIMARY KEY,
                   status TEXT,
                   date_joined TEXT,
                   date_subscribed TEXT,
                   sites TEXT,
                   categories TEXT
                   )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS payments (
                   id INTEGER PRIMARY KEY,
                   reference TEXT
                   )
    """)

    conn.commit()
    conn.close()


def add_user_to_db(user_id):

    date_joined = datetime.datetime.now().isoformat()
    sites =["linkedin",]
    categories = ["others",]

    conn = sqlite3.connect("rd_users.db")
    cursor = conn.cursor()

    cursor.execute("""
    INSERT OR IGNORE INTO users (
                   id,
                   status,
                   date_joined,
                   date_subscribed,
                   sites,
                   categories
                   ) VALUES (?, ?, ?, ?, ?, ?)
    """, (
        user_id,
        "trial",
        date_joined,
        date_joined,
        json.dumps(sites),
        json.dumps(categories),
    ))

    conn.commit()
    conn.close()


def get_user_info(user_id):
    """
    """
    conn = sqlite3.connect("rd_users.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))

    user = cursor.fetchone()

    conn.close()

    if user:
        return {
            "id": user[0],
            "status": user[1],
            "date_joined": user[2],
            "date_subscribed": user[3],
            "sites": user[4],
            "categories": user[5]
        }
    else:
        return None


def check_user(user_id):
    conn = sqlite3.connect("rd_users.db")
    cursor = conn.cursor()

    cursor.execute("""
    SELECT * FROM users WHERE id = ?
    """, (user_id,))
    user = cursor.fetchone()
    conn.close()

    if user:
        return user[0]
    
    return None


def edit_user_categories(categories, user_id):
    conn = sqlite3.connect("rd_users.db")
    cursor = conn.cursor()

    cursor.execute("UPDATE users SET categories = ? WHERE id = ?", (categories, user_id,))

    conn.commit()
    conn.close()


def get_all_users():
    conn = sqlite3.connect("rd_users.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()

    # cursor.close()
    conn.close()

    return users