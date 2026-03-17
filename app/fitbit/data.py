import requests

def get_heart_rate(access_token):
    url = "https://api.fitbit.com/1/user/-/activities/heart/date/today/1d.json"
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    return requests.get(url, headers=headers).json()
