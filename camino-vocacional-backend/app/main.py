from fastapi import FastAPI
from app.infrastructure.catalog_router import router as catalog_router

app = FastAPI(
    title="Camino Vocacional API",
    description="Backend API for Camino Vocacional applying Clean & Hexagonal Architecture principles.",
    version="1.0.0"
)

# Include the catalog router with the standard API v1 prefix
app.include_router(catalog_router, prefix="/api/v1")

@app.get("/")
def health_check():
    """
    Health check endpoint to verify the server is running properly.
    """
    return {"status": "healthy"}
