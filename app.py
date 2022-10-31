from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi import Depends, FastAPI, HTTPException, status, Request
from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import JWTError, jwt
from pydantic import BaseModel
from typing import Union
from database import *
from webHook import *

# to get a string like this run: openssl rand -hex 32
SECRET_KEY = open("key.txt", "r").read().replace("\n", "")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1024

# -----------------------------------------------------------
# OAuth2 Setup
# -----------------------------------------------------------

class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Union[str, None] = None


class User(BaseModel):
    username: str
    email: Union[str, None] = None
    full_name: Union[str, None] = None
    disabled: Union[bool, None] = None


class UserInDB(User):
    hashed_password: str


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


# -----------------------------------------------------------
# Start the API
# -----------------------------------------------------------

app = FastAPI(docs_url=None)


# -----------------------------------------------------------
# OAuth2 Handling
# -----------------------------------------------------------

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def authenticate_user(username: str, password: str):
    user = getApiUser(username)
    if not user:
        return False
    if not verify_password(password, user['PasswordHash']):
        return False
    return user


def create_access_token(data: dict, expires_delta: Union[timedelta, None] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = getApiUser(username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(current_user: User = Depends(get_current_user)):
    if current_user['Deactivated'] == 1:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user['Username']}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


# -----------------------------------------------------------
# API access points
# -----------------------------------------------------------

# Testing endpoint
@app.get("/")
async def home(): #current_user: User = Depends(get_current_active_user)):
	return {"Playing with": "Duckies"}


# Get reviews of a course
@app.get("/course/{course_id}")
async def read_item(course_id, current_user: User = Depends(get_current_active_user)):
    return getCourseReviews(course_id)

# Get reviews of a course
@app.get("/rating/{course_id}")
async def read_item(course_id, current_user: User = Depends(get_current_active_user)):
    return getCourseRating(course_id)


# Get all reviews a user has written
@app.get("/user/{nethz}")
async def read_item(nethz, current_user: User = Depends(get_current_active_user)):
    return getReviewsFromUser(nethz)


@app.get("/latest")
async def read_item(current_user: User = Depends(get_current_active_user)):
    return getLatestReviews()

@app.get("/all")
async def read_item(current_user: User = Depends(get_current_active_user)):
    return getAllReviews()



# Get total number of reviews
@app.get("/stats/")
async def read_item(current_user: User = Depends(get_current_active_user)):
    return getStatsReviews()


# Delete a review
@app.post("/remove")
async def remove_data(course_id: str, nethz: str, current_user: User = Depends(get_current_active_user)):
    return removeCourseReviews(course_id, nethz)

# Delete a review
@app.post("/removeRatings")
async def remove_data(course_id: str, nethz: str, current_user: User = Depends(get_current_active_user)):
    return removeCourseRatings(course_id, nethz)


# Add a review
@app.post("/insert")
async def insert_data(course_id: str, nethz:str, review: str, current_user: User = Depends(get_current_active_user)):
    sendHook()
    return insertReview(course_id, nethz, review)

# Add a rating
@app.post("/insertRating")
async def insert_data(course_id: str, nethz:str, s1:str, s2:str, s3:str, s4:str, s5:str, current_user: User = Depends(get_current_active_user)):
    return insertRatings(course_id, nethz, s1, s2, s3, s4, s5)

# Update a review
@app.post("/update")
async def update_data(course_id: str, nethz:str, review: str, current_user: User = Depends(get_current_active_user)):
    sendHook()
    return updateReview(course_id, nethz, review)

# Update a rating
@app.post("/updateRating")
async def update_data(course_id: str, nethz:str, s1:str, s2:str, s3:str, s4:str, s5:str, current_user: User = Depends(get_current_active_user)):
    return updateRatings(course_id, nethz, s1, s2, s3, s4, s5)