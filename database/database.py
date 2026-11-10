from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from database.config import settings

# 1. Tomamos la URL directamente desde nuestro objeto de configuración
engine = create_engine(settings.DATABASE_URL)

# 2. Fábrica de sesiones
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 3. Base para los modelos ORM (sintaxis moderna recomendada en SQLAlchemy)
Base = declarative_base()

# 4. Dependencia para inyectar la sesión de DB en los endpoints de FastAPI
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()