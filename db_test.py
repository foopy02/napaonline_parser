import sqlite3
conn_items = sqlite3.connect('items.db')
b = conn_items.execute("""
            SELECT *
            FROM items
            ORDER BY id DESC
            """)
print(b.fetchone())