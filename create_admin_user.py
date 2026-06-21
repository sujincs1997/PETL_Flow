import sys, os
sys.path.append('d:/SUJIN/Professional/ETL_Flow')

from backend.database import SessionLocal
from backend.models.user import User
from backend.api.auth import get_password_hash


def create_admin():
    db = SessionLocal()
    if db.query(User).filter(User.username == 'admin').first():
        print('admin user already exists')
        return
    admin = User(
        username='admin',
        email='admin@example.com',
        password_hash=get_password_hash('admin123'),
        role='Admin'
    )
    db.add(admin)
    db.commit()
    print('admin user created')

if __name__ == '__main__':
    create_admin()
