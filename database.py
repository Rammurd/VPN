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

cursor.execute('''
    CREATE TABLE IF NOT EXISTS keys (
        key_id INTEGER PRIMARY KEY,
        user_id INTEGER,
        key_text TEXT,
        server_location TEXT,
        FOREIGN KEY (user_id) REFERENCES users (user_id)
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

def add_access_key(user_id, key_text, server_location):
    conn = sqlite3.connect('user_data.db')
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO keys (user_id, key_text, server_location)
        VALUES (?, ?, ?)
    ''', (user_id, key_text, server_location))

    conn.commit()
    conn.close()



def get_access_key(user_id):
    conn = sqlite3.connect('user_data.db')
    cursor = conn.cursor()

    cursor.execute('''
        SELECT key_text FROM keys
        WHERE user_id = ?
    ''', (user_id,))

    access_keys = cursor.fetchall()

    conn.close()

    return [key[0] for key in access_keys] if access_keys else []

# Вспомогательная функция для получения key_text для server_location
def get_key_text(user_id, server_location):
    conn = sqlite3.connect('user_data.db')
    cursor = conn.cursor()

    cursor.execute('''
        SELECT key_text FROM keys
        WHERE user_id = ? AND server_location = ?
    ''', (user_id, server_location))

    key_text = cursor.fetchone()

    conn.close()

    return key_text[0] if key_text else None


def get_server_locations(user_id):
    conn = sqlite3.connect('user_data.db')
    cursor = conn.cursor()

    cursor.execute('''
        SELECT DISTINCT server_location FROM keys
        WHERE user_id = ?
    ''', (user_id,))

    server_locations = cursor.fetchall()

    conn.close()

    return [location[0] for location in server_locations] if server_locations else []