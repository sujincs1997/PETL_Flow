import requests
from backend.database import engine
from backend.models.user import User
from backend.api.auth import get_password_hash
from sqlalchemy.orm import Session

BASE_URL = "http://localhost:8000/api"

def create_test_user():
    with Session(engine) as db:
        user = db.query(User).filter(User.username == "testuser").first()
        if user:
            print("Test user already exists.")
            return
        
        hashed = get_password_hash("TestPass123!")
        new_user = User(
            username="testuser",
            email="test@example.com",
            password_hash=hashed,
            role="Admin"
        )
        db.add(new_user)
        db.commit()
        print("Test user 'testuser' created successfully in the SQLite database.")

def check_nodes():
    # 1. Login to get token
    login_payload = {"username": "testuser", "password": "TestPass123!"}
    try:
        resp = requests.post(f"{BASE_URL}/auth/login", json=login_payload)
        if resp.status_code != 200:
            print("Failed to login. Status:", resp.status_code)
            return
        token = resp.json()["access_token"]
    except Exception as e:
        print("Login request failed:", e)
        return

    # 2. Get registered nodes
    headers = {"Authorization": f"Bearer {token}"}
    try:
        resp = requests.get(f"{BASE_URL}/nodes", headers=headers)
        if resp.status_code != 200:
            print("Failed to fetch nodes. Status:", resp.status_code)
            return
        
        nodes = resp.json()
        print(f"Successfully fetched {len(nodes)} registered nodes.")
        
        # Check for our new nodes
        types = [n["type"] for n in nodes]
        
        assert "AttributeCreator" in types, "AttributeCreator is missing from API registry!"
        assert "SpatialRelator" in types, "SpatialRelator is missing from API registry!"
        
        # Print metadata of new nodes
        attr_creator = next(n for n in nodes if n["type"] == "AttributeCreator")
        spatial_relator = next(n for n in nodes if n["type"] == "SpatialRelator")
        
        print("\n--- AttributeCreator Metadata ---")
        print(attr_creator)
        print("\n--- SpatialRelator Metadata ---")
        print(spatial_relator)
        print("\nVerification successful! Both nodes are correctly registered and served by the backend API.")
        
    except Exception as e:
        print("Failed to query nodes:", e)

if __name__ == "__main__":
    create_test_user()
    check_nodes()
