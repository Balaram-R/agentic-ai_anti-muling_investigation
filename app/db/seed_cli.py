from app.db.session import SessionLocal
from app.db.seed import seed
if __name__=="__main__":
    with SessionLocal() as db: seed(db)
    print("Seed complete.")
