import argparse
import sys
from app.database.database import SessionLocal, Base, engine
from app.models.user import User
from app.core.security import get_password_hash, verify_password

def setup_admin(email: str = "admin@researchx.com", password: str = "Admin@2026", name: str = "System Administrator"):
    """
    CLI utility to securely initialize or update the ResearchX administrator account in SQLite.
    Never exposes passwords in plain text and securely hashes using bcrypt.
    """
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        clean_email = email.lower().strip()
        admin_user = db.query(User).filter(User.email == clean_email).first()
        
        if not admin_user:
            admin_user = User(
                name=name,
                email=clean_email,
                password_hash=get_password_hash(password),
                role="ADMIN",
                status="active",
                auth_provider="local"
            )
            db.add(admin_user)
            db.commit()
            db.refresh(admin_user)
            print(f"[SUCCESS] Created administrator account: {clean_email} (ID: {admin_user.id}, Role: ADMIN)")
        else:
            admin_user.name = name or admin_user.name
            admin_user.role = "ADMIN"
            admin_user.status = "active"
            admin_user.password_hash = get_password_hash(password)
            db.commit()
            db.refresh(admin_user)
            print(f"[SUCCESS] Updated administrator account password: {clean_email} (ID: {admin_user.id}, Role: ADMIN)")

        return True
    except Exception as e:
        print(f"[ERROR] Administrator setup failed: {e}", file=sys.stderr)
        return False
    finally:
        db.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Initialize or update ResearchX Administrator Account")
    parser.add_argument("--email", default="admin@researchx.com", help="Administrator email (default: admin@researchx.com)")
    parser.add_argument("--password", default="Admin@2026", help="Administrator password (default: Admin@2026)")
    parser.add_argument("--name", default="System Administrator", help="Administrator display name")
    
    args = parser.parse_args()
    setup_admin(args.email, args.password, args.name)
