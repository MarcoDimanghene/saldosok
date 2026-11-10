from sqlalchemy import Column, DateTime, ForeignKey, Integer, String

from database.database import Base


class PasswordReset(Base):
    __tablename__ = "restablecimientos_password"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False, index=True)
    token_hash = Column(String(64), nullable=False, unique=True)
    expires_at = Column(DateTime(timezone=True), nullable=False)
