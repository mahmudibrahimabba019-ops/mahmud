import psycopg2

db_url = 'postgresql://halari_spices_db_user:qPIneXBbPUuk0bz9zcuFbnFqWSXvmX0d@dpg-da2cee6417fc73e8fvr0-a.ohio-postgres.render.com/halari_spices_db'
conn = psycopg2.connect(db_url)
cur = conn.cursor()

# Get current Mint price
cur.execute("SELECT id, name, price FROM products WHERE name ILIKE '%Mint%' ORDER BY id LIMIT 1")
row = cur.fetchone()

if row:
    product_id, product_name, current_price = row
    new_price = current_price + 500
    
    print(f'Found: {product_name} (ID: {product_id})')
    print(f'Current Price: ₦{current_price}')
    print(f'New Price: ₦{new_price}')
    
    # Update the price
    cur.execute("UPDATE products SET price = %s WHERE id = %s", (new_price, product_id))
    conn.commit()
    
    print(f'✓ Price updated successfully')
    
    # Verify update
    cur.execute("SELECT price FROM products WHERE id = %s", (product_id,))
    updated_price = cur.fetchone()[0]
    print(f'Verified new price in DB: ₦{updated_price}')
else:
    print('Mint product not found')

cur.close()
conn.close()
