from fastapi import APIRouter, Request, Form, UploadFile, File
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path
import os, pandas as pd, uuid

from backend.utils.regression.session_state import get_active_dataset
from backend.utils.regression.context import get_sidebar_context
from backend.utils.regression import predict as pred_utils
from backend.services import dataset_service
from backend.config import MAX_DATASETS

router = APIRouter()
TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), "../../../frontend/templates")
templates = Jinja2Templates(directory=TEMPLATE_DIR)

TMP_UPLOAD = Path("frontend/static/tmp_uploads")
TMP_UPLOAD.mkdir(parents=True, exist_ok=True)


@router.get("/regression/predict", response_class=HTMLResponse)
async def predict_page(request: Request):
    active = get_active_dataset()
    files = dataset_service.list_files()

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


@router.post("/regression/predict", response_class=HTMLResponse)
async def perform_prediction(
    request: Request,
    model_key: str = Form(...),
    data_source: str = Form(...),
    upload_file: UploadFile = File(None)
):
    active = get_active_dataset()
    files = dataset_service.list_files()
    data_name = None

    try:
        if data_source == "x_test":
            df = pred_utils._load_split("X_test_scaled")
            df.attrs["source_name"] = "X_test_scaled"
            need_metrics = True
            data_name = "X_test_scaled"
        else:
            if not upload_file:
                raise ValueError("❌ Please upload a CSV file.")
            tmp_path = TMP_UPLOAD / f"{uuid.uuid4().hex}_{upload_file.filename}"
            tmp_path.write_bytes(await upload_file.read())
            df = pd.read_csv(tmp_path)
            df.attrs["source_name"] = upload_file.filename
            need_metrics = False
            data_name = upload_file.filename

        preds_df, metrics, out_fp = pred_utils.predict(model_key, df, include_metrics=need_metrics)
        preview_html = preds_df.head(10).to_html(classes="table table-dark table-sm", index=False)

        short_name = os.path.basename(out_fp)
        if len(short_name) > 80:
            short_name = short_name[:70] + "..."

        message = f"✅ Predictions saved to <code>{short_name}</code>"
        if metrics:
            message += " | " + " | ".join(f"{k.upper()}: <code>{v}</code>" for k, v in metrics.items())

    except Exception as e:
        preview_html, message = None, f"❌ Error: {e}"

    return templates.TemplateResponse(
        "regression/predict.html",
        {
            "request": request,
            "page": "predict",
            "models": pred_utils.list_models(),
            "results_table": preview_html,
            "selected_model": model_key,
            "data_name": data_name,
            "message": message,
            "files": files,
            "active_file": active,
            "max_datasets": MAX_DATASETS,
            **get_sidebar_context(active_file=active),
        },
    )