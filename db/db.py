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
    categories = ["others","content writing","software development","virtual assistant","customer service","data entry","design","ai/ml engineering","project management", "social media management"]

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


def get_user_categories(user_id):
    conn = sqlite3.connect("rd_users.db")
    cursor = conn.cursor()

    cursor.execute("SELECT categories FROM users WHERE id = ?", (user_id,))
    categories = cursor.fetchone()

    if categories is None or categories[0] is None:
        return set()

    return set(json.loads(categories[0]))


def get_all_users():
    conn = sqlite3.connect("rd_users.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users WHERE status != ?", ("expired"))
    users = cursor.fetchall()

    # cursor.close()
    conn.close()

    return users


def get_expired_users():
    conn = sqlite3.connect("rd_users.db")
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM users WHERE status = ?", ("expired",))
    expired_ids = cursor.fetchall()

    conn.close()

    return expired_ids


def get_trial_users():
    conn = sqlite3.connect("rd_users.db")
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM users WHERE status = ?", ("trial",))
    trial_ids = cursor.fetchall()

    conn.close()

    return trial_ids
    

def delete_user_by_id(id):
    """
    """
    conn = sqlite3.connect("rd_users.db")
    cursor = conn.cursor()

    cursor.execute("DELETE FROM users WHERE id = ?", (id,))

    conn.commit()
    conn.close()


def count_users():
    """
    """
    conn = sqlite3.connect("rd_users.db")
    cursor = conn.cursor()

    cursor.execute("SELECT status, COUNT (*) FROM users GROUP BY status")
    count = cursor.fetchall()
    conn.close()

    status_count = dict(count)
    total_count = sum(status_count.values())

    return total_count, status_count


def verify_subscription(id):
    """
    """
    conn = sqlite3.connect("rd_users.db", timeout=30)
    cursor = conn.cursor()

    cursor.execute("""SELECT * FROM users WHERE id = ?""", (id,))
    user = cursor.fetchone()

    if user[1] != "paid":
        return False
    
    conn.close()

    return True


def complete_payment(id: int, reference: str):
    conn = sqlite3.connect("rd_users.db", timeout=30)
    cursor = conn.cursor()

    cursor.execute("""SELECT * FROM payments WHERE id = ?""", (id,))
    payment = cursor.fetchone()
    
    if payment == None:
        cursor.execute("""
        INSERT INTO payments (id, reference) VALUES (?, ?)
        """, (id, reference,))
    else:
        cursor.execute("""UPDATE payments SET reference = ? WHERE id = ?""", (reference, id))
    
    cursor.execute("""UPDATE users SET status = ?, date_subscribed = ? WHERE id = ?""", ("paid", datetime.datetime.now().isoformat(), id))
    
    conn.commit()
    conn.close()

    return {
        "status": "paid"
    }


def set_expired():
    datenow = datetime.datetime.now()

    conn = sqlite3.connect("rd_users.db")
    cursor = conn.cursor()

    cursor.execute("""SELECT * FROM users WHERE status != ?""", ("expired",)) 
    users = cursor.fetchall()
    for user in users:
        if (user[1] == "paid"):
            days_allowed = datetime.timedelta(days=30)
            user_time = datetime.datetime.fromisoformat(user[3])
        elif (user[1] == "trial"):
            days_allowed = datetime.timedelta(days=2)
            user_time = datetime.datetime.fromisoformat(user[2])
        if (datenow - user_time > days_allowed):
            cursor.execute("""UPDATE users SET status = ? WHERE id = ?""", ("expired", user[0]))
    
    conn.commit()
    conn.close()

    return "ok"
