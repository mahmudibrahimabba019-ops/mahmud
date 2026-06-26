import sqlite3
conn = sqlite3.connect('halari_spices.db')
cursor = conn.cursor()
cursor.execute("SELECT id, order_number, payment_reference, payment_status, status FROM orders WHERE payment_reference='T569078360523568'")
print(cursor.fetchone())
conn.close()