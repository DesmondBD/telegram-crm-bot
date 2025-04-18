from datetime import datetime
import os
import sqlite3

class DB:
    def __init__(self, db_path="db/orders.db"):
        self.db_path = db_path

    def get_orders_by_status(self, status: str):
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("SELECT * FROM orders WHERE status = ?", (status,))
        results = cur.fetchall()
        conn.close()
        return results

    def update_comment(self, order_id: str, comment: str):
        print(f"Updating comment for order_id: {order_id}")  # Debug log
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("UPDATE orders SET comment = ? WHERE id = ?", (comment, order_id))
        conn.commit()
        conn.close()

    def update_media(self, order_id: str, file_id: str):
        print(f"Updating media for order_id: {order_id}")  # Debug log
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("UPDATE orders SET media = ? WHERE id = ?", (file_id, order_id))
        conn.commit()
        conn.close()

    def update_status(self, order_id: str, status: str):
        print(f"Updating status for order_id: {order_id} to status: {status}")  # Debug log
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("UPDATE orders SET status = ? WHERE id = ?", (status, order_id))
        conn.commit()
        conn.close()

    def clean_invalid_media(self):
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("UPDATE orders SET media = NULL WHERE media IS NOT NULL AND LENGTH(media) < 20")
        conn.commit()
        conn.close()

DB_PATH = "db/orders.db"

def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS orders (
        id TEXT PRIMARY KEY,
        name TEXT,
        phone TEXT,
        address TEXT,
        description TEXT,
        status TEXT,
        media TEXT,
        comment TEXT,
        created_at TEXT
    )
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS order_updates (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id TEXT,
        update_type TEXT,
        media TEXT,
        comment TEXT,
        timestamp TEXT,
        FOREIGN KEY(order_id) REFERENCES orders(id)
    )
    """)
    conn.commit()
    conn.close()

def add_order(order_data: dict):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    # Проверка на существование
    cur.execute("SELECT id FROM orders WHERE id = ?", (order_data["id"],))
    if cur.fetchone():
        print(f"🔁 Заказ уже существует: {order_data['id']}")
        conn.close()
        return
    # Добавление нового заказа
    cur.execute("""
        INSERT INTO orders (id, name, phone, address, description, status, media, comment, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        order_data["id"],
        order_data["name"],
        order_data["phone"],
        order_data["address"],
        order_data["description"],
        order_data.get("status", "новая"),
        order_data.get("media"),
        "",
        datetime.now().isoformat()
    ))
    conn.commit()
    conn.close()

def update_status(order_id: str, status: str):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("UPDATE orders SET status = ? WHERE id = ?", (status, order_id))
    conn.commit()
    conn.close()

def get_order_by_id(order_id: str):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT * FROM orders WHERE id = ?", (order_id,))
    result = cur.fetchone()
    conn.close()
    return result

def add_order_update(order_id: str, update_type: str, media: str = None, comment: str = None):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO order_updates (order_id, update_type, media, comment, timestamp)
        VALUES (?, ?, ?, ?, ?)
    """, (
        order_id,
        update_type,
        media,
        comment,
        datetime.now().isoformat()
    ))
    conn.commit()
    conn.close()

def get_updates_by_order_id(order_id: str):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        SELECT update_type, media, comment, timestamp
        FROM order_updates
        WHERE order_id = ?
        ORDER BY timestamp ASC
    """, (order_id,))
    results = cur.fetchall()
    conn.close()
    return results

def get_order(order_id: str):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT id, name, phone, address, description, status, media FROM orders WHERE id = ?", (order_id,))
    row = cur.fetchone()
    conn.close()

    if row:
        return {
            "id": row[0],
            "name": row[1],
            "phone": row[2],
            "address": row[3],
            "description": row[4],
            "status": row[5],
            "media": row[6]
        }
    return None

if __name__ == "__main__":
    init_db()
    print("✅ База данных создана и готова к работе.")
    db = DB()
    db.clean_invalid_media()
    print("🧹 Проблемные media удалены.")