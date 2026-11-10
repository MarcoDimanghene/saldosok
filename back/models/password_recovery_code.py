from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.sql import func

from database.database import Base


class PasswordRecoveryCode(Base):
    __tablename__ = "codigos_recuperacion_password"
    __table_args__ = (UniqueConstraint("user_id", name="uq_recovery_code_user"),)

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False, index=True)
    code_hash = Column(String(64), nullable=False, unique=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
