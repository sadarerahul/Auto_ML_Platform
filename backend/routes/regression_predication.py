from fastapi import APIRouter, Request, Form, UploadFile, File
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import pandas as pd, os, uuid
from pathlib import Path
from backend.utils.regression.context import get_sidebar_context
from backend.utils.regression import predict as pred_utils
from backend.services import dataset_service
from backend.config import MAX_DATASETS

router = APIRouter()
TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), "../../frontend/templates")
templates = Jinja2Templates(directory=TEMPLATE_DIR)

TMP_UPLOAD = Path("frontend/static/tmp_uploads")
TMP_UPLOAD.mkdir(parents=True, exist_ok=True)

# ---------- GET ----------
@router.get("/regression/predict", response_class=HTMLResponse)
async def predict_page(request: Request):
    files  = dataset_service.list_files()
    active = files[-1] if files else None
    return templates.TemplateResponse(
        "regression/predict.html",
        {
            "request": request,
            "page": "predict",
            "models": pred_utils.list_models(),
            "files": files,
            "active_file": active,
            "max_datasets": MAX_DATASETS,
            **get_sidebar_context(active_file=active),
        },
    )

# ---------- POST ----------
@router.post("/regression/predict", response_class=HTMLResponse)
async def perform_prediction(
    request: Request,
    model_key: str = Form(...),
    data_source: str = Form(...),            # 'x_test' or 'upload'
    upload_file: UploadFile = File(None)     # maybe None
):
    files  = dataset_service.list_files()
    active = files[-1] if files else None

    # ----- choose dataframe -----
    if data_source == "x_test":
        df = pred_utils._load_split("X_test_scaled")
        need_metrics = True
        data_name = "X_test_scaled"
    else:
        if not upload_file:
            return templates.TemplateResponse(
                "regression/predict.html",
                {
                    "request": request,
                    "page": "predict",
                    "message": "❌ Please upload a CSV.",
                    "models": pred_utils.list_models(),
                    "files": files,
                    "active_file": active,
                    "max_datasets": MAX_DATASETS,
                    **get_sidebar_context(active_file=active),
                },
            )
        # save temp, read
        tmp_path = TMP_UPLOAD / f"{uuid.uuid4().hex}_{upload_file.filename}"
        tmp_path.write_bytes(await upload_file.read())
        df = pd.read_csv(tmp_path)
        need_metrics = False
        data_name = upload_file.filename

    # ----- prediction -----
    try:
        preds_df, metrics = pred_utils.predict(model_key, df, include_metrics=need_metrics)
        outfile = pred_utils.PRED_DIR / f"{model_key}_{data_name}_preds.csv"
        preds_df.to_csv(outfile, index=False)
        table_html = preds_df.head(10).to_html(classes="table table-dark table-sm", index=False)
        message = f"✅ Predictions saved to {outfile.name}"
        if metrics:
            message += f" | MSE: {metrics['mse']:.3f}, R²: {metrics['r2']:.3f}"
    except Exception as e:
        table_html, message = None, f"❌ Error: {e}"

    return templates.TemplateResponse(
        "regression/predict.html",
        {
            "request": request,
            "page": "predict",
            "models": pred_utils.list_models(),
            "results_table": table_html,
            "selected_model": model_key,
            "data_name": data_name,
            "message": message,
            "files": files,
            "active_file": active,
            "max_datasets": MAX_DATASETS,
            **get_sidebar_context(active_file=active),
        },
    )
