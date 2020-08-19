from fastapi import FastAPI, Depends
from utils.db_functions import db_get_user_moods, db_insert_mood, db_get_current_streak
from fastapi.security import OAuth2PasswordRequestForm
from models.jwt_user import JWTUser
from utils.security import authenticate_user, create_jwt_token, check_jwt_token
from fastapi import HTTPException
from starlette.status import HTTP_401_UNAUTHORIZED, HTTP_422_UNPROCESSABLE_ENTITY
from utils.const import MOOD_TYPES, MOOD_TYPE_INVALID, TOKEN_INVALID_CREDENTIALS_MSG, DATA_NOT_RETURNED

app = FastAPI()

@app.get("/") # Requires no authorization
async def health_check():
    return {"OK"}

@app.post("/token") # Requires correct username and password, returns JWT token to be used in further requests
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    jwt_user_dict = {"username": form_data.username,"password":form_data.password}
    jwt_user = JWTUser(**jwt_user_dict)
    user = await authenticate_user(jwt_user)

    if user is None:
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail=TOKEN_INVALID_CREDENTIALS_MSG)

    jwt_token = create_jwt_token(user)
    return {"token": jwt_token}


@app.post("/mood/{moodin}") # Requires authorization from JWT token
async def insert_user_mood(moodin: str, jwt: str = Depends(check_jwt_token)):
    print(moodin, jwt)
    if (moodin in MOOD_TYPES):
        print("Element Exists")
        moods = await db_insert_mood(jwt, moodin)
        if moods is not None:
           return {"Moods": moods}
        else:
          return {"result": "Mood not inserted."}

    else:
        raise HTTPException(status_code=HTTP_422_UNPROCESSABLE_ENTITY, detail=MOOD_TYPE_INVALID)

@app.get("/mood") # Requires authorization from JWT token
async def insert_user_mood(jwt: str = Depends(check_jwt_token)):
    print(jwt)
    moods = await db_get_user_moods(jwt)
    streak_dict = await db_get_current_streak(jwt)
    final_output = {}
    final_output["current_streak"] = streak_dict["current_streak"]
    final_output["longest_streak"] = streak_dict["longest_streak"] # Returning longest_streak even though it wasn't specifically asked for.
    if (streak_dict["percentile"] >= 0.5):
        final_output["percentile"] = streak_dict["percentile"]
    final_output["moods"] = moods
    if moods is not None:
        return final_output
    else:
        return {"result": DATA_NOT_RETURNED}

