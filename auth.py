import json
import base64
import requests
import os
from urls_air import OAUTH_URL
from dotenv import load_dotenv
from pathlib import Path

BASE_DIR = Path(__file__).parent
load_dotenv(os.path.join(BASE_DIR, "secrets.env"), override=True)
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
CLIENT_ID = os.getenv("CLIENT_ID")


# class VectaraAuthClient:
#     def __init__(self, auth_domain=OAUTH_URL, client_id=CLIENT_ID, client_secret=CLIENT_SECRET, redirect_uri=None):
#         self.token_endpoint = auth_domain #self.init(auth_domain, redirect_uri)
#         self.client_id = client_id
#         self.client_secret = client_secret
#         self.redirect_uri = redirect_uri

    # def init(self, auth_domain, redirect_uri):
    #     str_auth_domain = auth_domain
    #     if not str_auth_domain.endswith("/oauth2/token"):
    #         if not str_auth_domain.endswith("/"):
    #             str_auth_domain += "/"
    #         str_auth_domain += "oauth2/token"
    #     return str_auth_domain

def fetch_client_credentials_jwt():
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
    }

    data = {
        'grant_type': 'client_credentials',
        'client_id': CLIENT_ID,
        'redirect_uri': None,
    }

    auth_str = f"{CLIENT_ID}:{CLIENT_SECRET}"
    auth_str = base64.b64encode(auth_str.encode()).decode()

    headers['Authorization'] = f'Basic {auth_str}'

    response = requests.post(OAUTH_URL, headers=headers, data=data)

    if response.status_code == 200:
        response_data = json.loads(response.text)
        if 'access_token' in response_data:
            return response_data['access_token']
    else:
        print(f"Error while retrieving JWT Token: {response.text}")
        return None