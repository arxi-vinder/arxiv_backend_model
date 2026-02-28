import datetime

from passlib.context import CryptContext
import jwt
import dotenv
import os

dotenv.load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY") 
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = 30


pwd_context = CryptContext(
    schemes=["argon2"], 
    deprecated="auto"
)

def hash_pwd(password:str):
    return pwd_context.hash(password)

def verify_pwd(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.datetime.now() + datetime.timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt