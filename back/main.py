from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Base de datos y configuración
from database.database import Base, engine
from database.config import settings  # Asegura que las variables de entorno se carguen al inicio

# Modelos
from back import models  # Asegura que SQLAlchemy reconozca todos los modelos antes de create_all

# Routers
from back.routes import auth, companies, dashboard, extract, imports, invoices, payments, tenants, user

# Crea las tablas faltantes en la base de datos
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="SaldosOk API",
    description="Backend de automatización de facturación y conciliación de saldos",
    version="1.0.0",
)

# CORS: permite el frontend configurado y el servidor local de Vite.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        settings.FRONTEND_URL,
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 1. Registrar el router de Autenticación
app.include_router(auth.router)
app.include_router(dashboard.router)

# 2. Registrar los routers del resto del sistema
app.include_router(companies.router)
app.include_router(user.router)
app.include_router(tenants.router)
app.include_router(invoices.router)
app.include_router(extract.router)
app.include_router(imports.router)
app.include_router(payments.router)


@app.get("/", tags=["Root"])
def root():
    return {"message": "SaldosOk API funcionando correctamente"}
