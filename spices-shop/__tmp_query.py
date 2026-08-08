import sqlite3, os
p = r'c:\Users\HP\Desktop\Backup\Desktop\websites\spices-shop\halari_spices.db'
out = r'c:\Users\HP\Desktop\Backup\Desktop\websites\spices-shop\__tmp_query_output.txt'
conn = sqlite3.connect(p)
cur = conn.cursor()
rows = cur.execute("SELECT id, order_number, payment_reference, payment_status, total_amount FROM orders WHERE payment_status='paid' ORDER BY id DESC LIMIT 5").fetchall()
with open(out, 'w', encoding='utf-8') as f:
    f.write('rows=' + str(rows) + '\n')
    if rows:
        cols = [d[0] for d in cur.description]
        f.write('columns=' + str(cols) + '\n')
conn.close()
