from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from backend.routes import (
    root_routes,
    upload_routes,
    clean_routes,
    visualize_routes,
    outlier_routes,
<<<<<<< HEAD
    regression_switch,
=======
>>>>>>> d3d66fe132d82d8db1f5671b4cc9181bb1224be0
    regression_feature_selection,
    regression_split,
    regression_scale,
    regression_model_selection,
<<<<<<< HEAD
    regression_predication,
    regression_smoothing
=======
    regression_predication
>>>>>>> d3d66fe132d82d8db1f5671b4cc9181bb1224be0
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
<<<<<<< HEAD
app.include_router(regression_switch.router)
=======
>>>>>>> d3d66fe132d82d8db1f5671b4cc9181bb1224be0
app.include_router(regression_feature_selection.router)
app.include_router(regression_split.router)
app.include_router(regression_scale.router)
app.include_router(regression_model_selection.router)
<<<<<<< HEAD
app.include_router(regression_predication.router)
app.include_router(regression_smoothing.router)
=======
app.include_router(regression_predication.router)
>>>>>>> d3d66fe132d82d8db1f5671b4cc9181bb1224be0
