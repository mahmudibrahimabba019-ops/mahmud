from database import SessionLocal
import models
from main import PRODUCTS

db = SessionLocal()

# Delete existing products (optional - only if needed)
# db.query(models.Product).delete()

# Add all products
for product_data in PRODUCTS:
    new_product = models.Product(
        id=product_data["id"],
        name=product_data["name"],
        category=product_data["category"],
        price=product_data["price"],
        image=product_data["image"],
        stock_quantity=100,
        low_stock_threshold=10
    )
    db.merge(new_product)  # merge instead of add to avoid duplicates

db.commit()
print(f"Products in database: {db.query(models.Product).count()}")
db.close()
