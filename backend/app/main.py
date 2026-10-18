from fastapi import FastAPI
from app.db.session import init_db, SessionLocal
from app.scenarios.banca.router import router as banca_router
from app.scenarios.banca.seed_data import seed_banca
from app.scenarios.ecommerce.router import router as ecommerce_router
from app.scenarios.ecommerce.seed_data import seed_ecommerce
from app.scenarios.soporte.router import router as soporte_router
from app.scenarios.soporte.seed_data import seed_soporte
from app.scenarios.salud.router import router as salud_router
from app.scenarios.salud.seed_data import seed_salud
from app.routers.logs import router as logs_router
from app.routers.admin_banca import router as admin_banca_router
from app.routers.admin_ecommerce import router as admin_ecommerce_router
from app.routers.admin_soporte import router as admin_soporte_router
from app.routers.admin_salud import router as admin_salud_router
from app.routers.resolution import router as resolution_router

app = FastAPI(title="LLM Chain Lab")

app.include_router(banca_router)
app.include_router(ecommerce_router)
app.include_router(soporte_router)
app.include_router(salud_router)
app.include_router(logs_router)
app.include_router(admin_banca_router)
app.include_router(admin_ecommerce_router)
app.include_router(admin_soporte_router)
app.include_router(admin_salud_router)
app.include_router(resolution_router)


@app.on_event("startup")
def startup():
    init_db()
    db = SessionLocal()
    try:
        seed_banca(db)
        seed_ecommerce(db)
        seed_soporte(db)
        seed_salud(db)
    finally:
        db.close()


@app.get("/health")
def health():
    return {"status": "ok"}
