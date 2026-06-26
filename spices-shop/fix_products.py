from database import SessionLocal
import models
from main import PRODUCTS

db = SessionLocal()

print(f"Current products in database: {db.query(models.Product).count()}")

for product_data in PRODUCTS:
    existing = db.query(models.Product).filter(models.Product.id == product_data["id"]).first()
    if existing:
        print(f"Updating: {product_data['name']}")
        existing.name = product_data["name"]
        existing.category = product_data["category"]
        existing.price = product_data["price"]
        existing.image = product_data["image"]
    else:
        print(f"Adding: {product_data['name']}")
        new_product = models.Product(
            id=product_data["id"],
            name=product_data["name"],
            category=product_data["category"],
            price=product_data["price"],
            image=product_data["image"],
            stock_quantity=100,
            low_stock_threshold=10
        )
        db.add(new_product)

db.commit()
print(f"Now products in database: {db.query(models.Product).count()}")
db.close()
