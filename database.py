import sqlite3
from datetime import datetime

# Создаем базу данных
conn = sqlite3.connect('user_data.db')
cursor = conn.cursor()

# Создаем таблицу для пользователей, если она не существует
cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        username TEXT,
        registration_date TEXT,
        purchase_date TEXT,
        has_paid BOOLEAN DEFAULT 0
    )
''')

conn.commit()
conn.close()


def add_user(user_id, username):
    conn = sqlite3.connect('user_data.db')
    cursor = conn.cursor()

    registration_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute('''
        INSERT INTO users (user_id, username, registration_date, purchase_date, has_paid)
        VALUES (?, ?, ?, ?,?)
    ''', (user_id, username, registration_date, None, False))

    conn.commit()
    conn.close()


def update_purchase_date(user_id):
    conn = sqlite3.connect('user_data.db')
    cursor = conn.cursor()

    purchase_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute('''
        UPDATE users
        SET purchase_date = ?
        WHERE user_id = ?
    ''', (purchase_date, user_id))

    cursor.execute('''
           UPDATE users
           SET has_paid = 1
           WHERE user_id = ?
       ''', (user_id,))

    conn.commit()
    conn.close()


def get_user_data(user_id):
    conn = sqlite3.connect('user_data.db')
    cursor = conn.cursor()

    cursor.execute('''
        SELECT * FROM users
        WHERE user_id = ?
    ''', (user_id,))

    user_data = cursor.fetchone()

    conn.close()

    return user_data
