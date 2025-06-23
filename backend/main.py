from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from backend.routes import (
    root_routes,
    upload_routes,
    clean_routes,
    visualize_routes,
    outlier_routes,
    regression_switch,
    regression_feature_selection,
    regression_split,
    regression_scale,
    regression_model_selection,
    regression_predication,
    regression_smoothing
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
app.include_router(regression_switch.router)
app.include_router(regression_feature_selection.router)
app.include_router(regression_split.router)
app.include_router(regression_scale.router)
app.include_router(regression_model_selection.router)
app.include_router(regression_predication.router)
app.include_router(regression_smoothing.router)