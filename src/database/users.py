from typing import Optional, Generator
from werkzeug.security import generate_password_hash, check_password_hash
from models.user import User
from sqlalchemy.orm import Session
from .init_db import get_db, SessionLocal

class UserService:
    def __init__(self, session: Optional[Session] = None):
        self.session = session

    @property
    def db(self) -> Session:
        """Get database session."""
        if self.session is None:
            # Создаем новую сессию вместо использования генератора
            return SessionLocal()
        return self.session

    def create_user(self, username: str, email: str, password: str,
                   first_name: Optional[str] = None, last_name: Optional[str] = None) -> User:
        """Create a new user."""
        user = User(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name
        )
        self.set_password(user, password)
        db = self.db
        try:
            db.add(user)
            db.commit()
            db.refresh(user)
            return user
        finally:
            if self.session is None:
                db.close()

    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID."""
        db = self.db
        try:
            return db.query(User).filter(User.id == user_id).first()
        finally:
            if self.session is None:
                db.close()

    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        db = self.db
        try:
            return db.query(User).filter(User.email == email).first()
        finally:
            if self.session is None:
                db.close()

    def get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username."""
        db = self.db
        try:
            return db.query(User).filter(User.username == username).first()
        finally:
            if self.session is None:
                db.close()

    def update_user(self, user_id: int, email: str, first_name: Optional[str] = None, last_name: Optional[str] = None) -> Optional[User]:
        """Update user information."""
        db = self.db
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                return None
                
            user.email = email
            user.first_name = first_name
            user.last_name = last_name
            
            db.commit()
            db.refresh(user)
            return user
        except Exception:
            db.rollback()
            raise
        finally:
            if self.session is None:
                db.close()

    def delete_user(self, user: User) -> bool:
        """Delete user."""
        db = self.db
        try:
            db.delete(user)
            db.commit()
            return True
        except Exception:
            db.rollback()
            return False
        finally:
            if self.session is None:
                db.close()

    @staticmethod
    def set_password(user: User, password: str) -> None:
        """Set password hash for user."""
        user.password_hash = generate_password_hash(password)

    @staticmethod
    def check_password(user: User, password: str) -> bool:
        """Check if provided password matches the hash."""
        return check_password_hash(user.password_hash, password)

    @staticmethod
    def get_full_name(user: User) -> str:
        """Get user's full name."""
        if user.first_name and user.last_name:
            return f"{user.first_name} {user.last_name}"
        return user.username

    @staticmethod
    def to_dict(user: User) -> dict:
        """Convert user object to dictionary."""
        return {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'is_active': user.is_active,
            'created_at': user.created_at.isoformat() if user.created_at else None,
            'updated_at': user.updated_at.isoformat() if user.updated_at else None
        } 