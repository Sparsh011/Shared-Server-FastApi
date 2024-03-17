import os

import requests
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from google.oauth2 import id_token
from google.auth.transport import requests

import Constants

app = FastAPI()
load_dotenv()


@app.get("/login")
async def loginWithCode(code: str):
    url = Constants.ACCESS_TOKEN_BASE_URL + Constants.ACCESS_TOKEN_API_ROUTE
    headers = {
        "Accept": "application/json"
    }
    params = {
        "client_secret": os.getenv(Constants.GITHUB_CLIENT_SECRET_ENV_KEY),
        "code": code,
        "client_id": os.getenv(Constants.GITHUB_CLIENT_ID_ENV_KEY)
    }
    response = requests.post(url=url, headers=headers, params=params)

    if response.status_code == 200:
        data = response.json()
        if "access_token" in data:
            user_details = _getUserDetailsFrom(access_token=data["access_token"])
            # Access token is valid
            user_details["is_token_valid"] = True
            return user_details
        else:
            raise HTTPException(status_code=400, detail="Access token not found in response")
    else:
        raise HTTPException(status_code=response.status_code, detail="Failed to get access token")


def _getUserDetailsFrom(access_token):
    url = Constants.USER_DETAILS_BASE_URL + Constants.USER_DETAILS_API_ROUTE

    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    response = requests.get(url=url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        return {"access_token": access_token, "user_details": data}
    elif response.status_code == 400:
        response = {
            "response": {
                "is_token_valid": False,
                "message": "Access Token Not Found"
            }
        }
        return response
    else:
        response = {
            "response": {
                "is_token_valid": False,
                "message": "Access Token Not Found"
            }
        }
        return response


@app.get("/check-login-status")
async def isUserLoggedIn(access_token):
    try:
        user_details = _getUserDetailsFrom(access_token=access_token)
        # Access token is valid
        user_details["is_token_valid"] = True
        return user_details
    except Exception as e:
        # Access token is invalid
        response = {
            "is_token_valid": False,
            "message": str(e)
        }
        return response


@app.get("/verify-google-auth-token")
async def verifyGoogleAuthToken(token):
    try:
        response = {
            "user_details": id_token.verify_oauth2_token(
                token,
                requests.Request(),
                os.getenv(Constants.FIREBASE_WEB_SERVER_CLIENT_ID_KEY)
            ),
            "status": "Success"
        }
        return response
    except Exception as e:
        response = {
            "status": "Failed",
            "message": str(e)
        }
        return response