import requests
from backend.database import engine
from backend.models.user import User
from backend.api.auth import get_password_hash
from sqlalchemy.orm import Session

def create_user():
    with Session(engine) as db:
        if db.query(User).filter(User.username == "testuser").first():
            print("User already exists")
            return
        hashed = get_password_hash("TestPass123!")
        user = User(username="testuser", email="test@example.com", password_hash=hashed, role="Admin")
        db.add(user)
        db.commit()
        db.refresh(user)
        print("Created user", user.id)

def login():
    resp = requests.post("http://localhost:8000/api/auth/login", json={"username": "testuser", "password": "TestPass123!"})
    print("Login response status:", resp.status_code)
    print("Response body:", resp.text)

if __name__ == "__main__":
    create_user()
    login()
