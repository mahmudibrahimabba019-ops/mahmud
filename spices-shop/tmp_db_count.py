import psycopg2
conn = psycopg2.connect('postgresql://postgres:Mahmud019@localhost:5432/halari_spices')
cur = conn.cursor()
cur.execute("SELECT COUNT(*) FROM products")
print(cur.fetchone())
conn.close()
