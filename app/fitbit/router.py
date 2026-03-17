from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse
from app.fitbit.oauth import get_auth_url, exchange_code_for_token

router = APIRouter(prefix="/fitbit", tags=["Fitbit"])


@router.get("/login")
def fitbit_login():
    return RedirectResponse(get_auth_url())


@router.get("/callback")
def fitbit_callback(code: str):
    token_data = exchange_code_for_token(code)
    return {
        "status": "success",
        "token": token_data
    }
