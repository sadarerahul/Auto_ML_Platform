from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from backend.routes import (
    root_routes,
    upload_routes,
    clean_routes,
    visualize_routes,
    outlier_routes
)


app = FastAPI()

# Mount static files
app.mount("/static", StaticFiles(directory="frontend/static"), name="static")

# Register routers
app.include_router(root_routes.router)
app.include_router(upload_routes.router)
app.include_router(clean_routes.router)
app.include_router(visualize_routes.router)
app.include_router(outlier_routes.router)
