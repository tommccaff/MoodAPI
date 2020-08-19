from datetime import datetime

MOOD_TYPES = [ 'happy', 'sad', 'angry', 'OK']
MOOD_TYPE_INVALID = "Invalid mood type: must be happy, sad, angry, or OK."

JWT_SECRET_KEY = "c07e154e8067407c909be11132e7d1bcee77542afd6c26ba613e2ffd9c3375ea"
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_TIME_MINUTES = 10
JWT_EXPIRED_MSG = "Your JWT token is expired. Please Renew the JWT token."
JWT_INVALID_MSG = "Invalid JWT token."
TOKEN_INVALID_CREDENTIALS_MSG = "Invalid username or password."

TOKEN_DESCRIPTION = (
    "Returns JWT token if username and password are correct"
)
TOKEN_SUMMARY = "Returns JWT token."
DATA_NOT_RETURNED = "Mood not inserted, no data returned."


# DB_HOST = "142.93.119.241"
# DB_USER = "MoodsAdmin"
DB_HOST = "localhost"
DB_USER = "postgres"

DB_PASSWORD = "Tommccaff1"
DB_NAME = "moodsdb"
DB_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"

EPOCH = datetime.utcfromtimestamp(0)