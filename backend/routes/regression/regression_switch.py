from fastapi import APIRouter, Form
from fastapi.responses import RedirectResponse
from backend.utils.regression.session_state import set_active_dataset

router = APIRouter()

@router.post("/regression/switch_dataset")
async def switch_dataset(selected_dataset: str = Form(...)):
    # ✅ Set the selected dataset as active
    set_active_dataset(selected_dataset)

    # ❌ Do NOT auto-create any cleaned file here
    # Cleaned datasets are generated explicitly during preprocessing

    return RedirectResponse(url="/regression/upload", status_code=303)