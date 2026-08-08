import sqlite3, os
p = 'c:/Users/HP/Desktop/Backup/Desktop/websites/spices-shop/halari_spices.db'
out = 'c:/Users/HP/Desktop/Backup/Desktop/websites/spices-shop/db_inspect_output.txt'
print('path exists', os.path.exists(p))
conn = sqlite3.connect(p)
cur = conn.cursor()
print('tables', cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name").fetchall())
rows = cur.execute("SELECT id, order_number, payment_reference, payment_status, total_amount FROM orders WHERE payment_status='paid' ORDER BY id DESC LIMIT 5").fetchall()
with open(out, 'w', encoding='utf-8') as f:
    f.write('rows=' + str(rows) + '\n')
conn.close()
