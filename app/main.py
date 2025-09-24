from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .admin import init_admin
from .config import settings
from .db import ping_db
from .routers import auth, blackouts, establishments, geo, products, reservations, resources, sales

app = FastAPI(title="Sintética API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.CORS_ORIGINS],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(geo.router, prefix="/geo", tags=["geo"])
app.include_router(establishments.router, prefix="/establishments", tags=["establishments"])
app.include_router(resources.router, prefix="/resources", tags=["resources"])
app.include_router(reservations.router, prefix="/reservations", tags=["reservations"])
app.include_router(products.router, prefix="/products", tags=["products"])
app.include_router(sales.router, prefix="/sales", tags=["sales"])
app.include_router(blackouts.router, prefix="/blackouts", tags=["blackouts"])


@app.get("/health")
def health():
    try:
        ping_db()
        return {"ok": True, "db": "up"}
    except Exception as e:
        return {"ok": True, "db": f"down: {type(e).__name__}", "detail": str(e)}


init_admin(app)

if __name__ == "__main__":
    import uvicorn

    # Bind to localhost for local development to avoid exposing publicly (ruff S104)
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=False)
