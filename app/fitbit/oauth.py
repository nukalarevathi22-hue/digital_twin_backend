import requests
import os
import base64
from dotenv import load_dotenv

load_dotenv()

FITBIT_CLIENT_ID = os.getenv("FITBIT_CLIENT_ID")
FITBIT_CLIENT_SECRET = os.getenv("FITBIT_CLIENT_SECRET")
FITBIT_REDIRECT_URI = os.getenv("FITBIT_REDIRECT_URI")

AUTH_URL = "https://www.fitbit.com/oauth2/authorize"
TOKEN_URL = "https://api.fitbit.com/oauth2/token"


def get_auth_url():
    scope = "heartrate activity profile"
    return (
        f"{AUTH_URL}"
        f"?response_type=code"
        f"&client_id={FITBIT_CLIENT_ID}"
        f"&redirect_uri={FITBIT_REDIRECT_URI}"
        f"&scope={scope}"
    )


def exchange_code_for_token(code: str):
    auth_header = base64.b64encode(
        f"{FITBIT_CLIENT_ID}:{FITBIT_CLIENT_SECRET}".encode()
    ).decode()

    headers = {
        "Authorization": f"Basic {auth_header}",
        "Content-Type": "application/x-www-form-urlencoded"
    }

    data = {
        "grant_type": "authorization_code",
        "redirect_uri": FITBIT_REDIRECT_URI,
        "code": code
    }

    response = requests.post(TOKEN_URL, headers=headers, data=data)
    response.raise_for_status()
    return response.json()
