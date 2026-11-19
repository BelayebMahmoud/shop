from fastapi import FastAPI

from app.routers import auth, orders, products

app = FastAPI(title="Shop MVP", version="0.1.0")

for r in (auth.router, products.router, orders.router):
    app.include_router(r, prefix="/api")


@app.get("/api/health", tags=["meta"])
def health() -> dict[str, str]:
    return {"status": "ok"}
