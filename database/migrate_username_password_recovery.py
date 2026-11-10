from sqlalchemy import create_engine, text

from back import models
from database.config import settings
from database.database import Base


def migrate() -> None:
    engine = create_engine(settings.DATABASE_URL)
    with engine.begin() as connection:
        connection.execute(text(
            "ALTER TABLE usuarios ADD COLUMN IF NOT EXISTS username VARCHAR(50)"
        ))
        connection.execute(text(
            "ALTER TABLE usuarios ADD COLUMN IF NOT EXISTS "
            "is_email_verified BOOLEAN NOT NULL DEFAULT TRUE"
        ))
        connection.execute(text(
            "UPDATE usuarios SET username = CONCAT('usuario', id) "
            "WHERE username IS NULL OR username = ''"
        ))
        connection.execute(text(
            "ALTER TABLE usuarios ALTER COLUMN username SET NOT NULL"
        ))
        connection.execute(text(
            "ALTER TABLE usuarios ALTER COLUMN email DROP NOT NULL"
        ))
        connection.execute(text(
            "CREATE UNIQUE INDEX IF NOT EXISTS ix_usuarios_username "
            "ON usuarios (username)"
        ))

    Base.metadata.create_all(
        bind=engine,
        tables=[
            models.EmailVerification.__table__,
            models.PasswordReset.__table__,
            models.PasswordRecoveryCode.__table__,
        ],
    )
    engine.dispose()


if __name__ == "__main__":
    migrate()
