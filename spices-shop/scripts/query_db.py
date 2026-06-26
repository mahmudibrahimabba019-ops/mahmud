import sqlite3

db_path = 'halari_spices.db'
out_path = 'scripts/db_output.txt'
try:
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("SELECT id, order_number, payment_reference, total_amount, created_at FROM orders ORDER BY id DESC LIMIT 10")
    rows = cur.fetchall()
    with open(out_path, 'w', encoding='utf-8') as f:
        if not rows:
            f.write('No orders found.\n')
        else:
            for r in rows:
                f.write(str(r) + '\n')
    conn.close()
    print('Wrote output to', out_path)
except Exception as e:
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write('Error: ' + str(e) + '\n')
    print('Error, wrote to', out_path)
