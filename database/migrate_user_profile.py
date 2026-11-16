from sqlalchemy import create_engine, text

from database.config import settings


engine = create_engine(settings.DATABASE_URL)

with engine.connect() as connection:
    connection.execute(
        text(
            "ALTER TABLE usuarios "
            "ADD COLUMN IF NOT EXISTS perfil VARCHAR(20) NOT NULL DEFAULT 'venta'"
        )
    )
    connection.commit()
    result = connection.execute(
        text(
            "SELECT column_name, data_type, column_default "
            "FROM information_schema.columns "
            "WHERE table_name = 'usuarios' AND column_name = 'perfil'"
        )
    ).fetchone()
    print(f"Columna 'perfil' lista: {result}")
