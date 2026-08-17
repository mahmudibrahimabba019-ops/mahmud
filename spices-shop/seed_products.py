from main import PRODUCTS
from database import SessionLocal
from models import Product


def seed_products():
    db = SessionLocal()
    try:
        added = 0
        skipped = 0

        for product_data in PRODUCTS:
            existing = db.query(Product).filter(Product.id == product_data["id"]).first()
            if existing:
                skipped += 1
                continue

            product = Product(
                id=product_data["id"],
                name=product_data["name"],
                category=product_data["category"],
                price=product_data["price"],
                image=product_data["image"],
                stock_quantity=100,
                low_stock_threshold=10,
                is_active=True,
            )
            db.add(product)
            added += 1

        db.commit()
        print(f"Products added: {added}")
        print(f"Products skipped (already existed): {skipped}")
        print(f"Total processed: {added + skipped}")
    finally:
        db.close()


if __name__ == "__main__":
    seed_products()
