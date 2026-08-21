import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from app.database.database import engine, Base, SessionLocal
from app.services.demo_service import DemoService
from app.models import User, ResearchPaper, Analysis

print("Creating database tables...")
Base.metadata.create_all(bind=engine)
print("Tables created.")

print("Generating demo PDFs...")
DemoService.generate_sample_pdfs()
print("Demo PDFs generated.")

print("Seeding initial database data...")
db = SessionLocal()
DemoService.seed_initial_data(db)

users_count = db.query(User).count()
papers_count = db.query(ResearchPaper).count()
print(f"Users in DB: {users_count}")
print(f"Papers in DB: {papers_count}")
db.close()
print("Backend test completed successfully!")
