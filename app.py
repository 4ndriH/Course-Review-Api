from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi import Depends, FastAPI, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
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
# API setup
# -----------------------------------------------------------

tags_metadata = [
    {
        "name": "RubberDucky",
        "description": "Testing endpoint"
    },
    {
        "name": "CR Home",
        "description": "Information displayed on the CourseReview Homepage."
    
    },
    {
        "name": "CR Course",
        "description": "Request course information."
    },
    {
        "name": "CR User",
        "description": "Restricted access points as they are user specific."
    },
]

app = FastAPI(
    title="CourseReview API",
    version="2.0.0",
    openapi_tags=tags_metadata
    )


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
) 


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


# -----------------------------------------------------------
# API access points
# -----------------------------------------------------------

# Testing endpoint
@app.get("/", tags=["RubberDucky"])
async def home():
	return {"Playing with": "Duckies"}


# CR Home endpoints
@app.get("/latestReviews", tags=["CR Home"])
async def read_item():
    return getLatestReviews()


@app.get("/allReviews", tags=["CR Home"])
async def read_item():
    return getAllCoursesWithReviews()


@app.get("/stats", tags=["CR Home"])
async def read_item():
    return getPublishedReviewStats()


# CR Course endpoints
@app.get("/course/{course_id}", tags=["CR Course"])
async def read_item(course_id):
    return getCourseReviews(course_id)


@app.get("/rating/{course_id}", tags=["CR Course"])
async def read_item(course_id):
    return getCourseRating(course_id)


# CR User endpoints
@app.get("/userReview/{user_id}", tags=["CR User"])
async def read_item(user_id, current_user: User = Depends(get_current_active_user)):
    return getReviewsFromUser(user_id)


@app.get("/userRating/{user_id}", tags=["CR User"])
async def read_item(user_id, current_user: User = Depends(get_current_active_user)):
    return getStarRatingsFromUser(user_id)


@app.post("/insertReview", tags=["CR User"])
async def insert_data(course_id: str, user_id: str, review: str, current_user: User = Depends(get_current_active_user)):
    sendHook()
    return insertReview(course_id, user_id, review)


@app.post("/updateReview", tags=["CR User"])
async def update_data(course_id: str, user_id: str, review: str, current_user: User = Depends(get_current_active_user)):
    sendHook()
    return updateReview(course_id, user_id, review)


@app.post("/removeReview", tags=["CR User"])
async def remove_data(course_id: str, user_id: str, current_user: User = Depends(get_current_active_user)):
    return removeCourseReview(course_id, user_id)


@app.post("/insertRating", tags=["CR User"])
async def insert_data(course_id: str, user_id: str, rating_id: str, rating: int, current_user: User = Depends(get_current_active_user)):
    return insertRating(course_id, user_id, rating_id, rating)


@app.post("/updateRating", tags=["CR User"])
async def update_data(course_id: str, user_id: str, rating_id: str, rating: int, current_user: User = Depends(get_current_active_user)):
    return updateRating(course_id, user_id, rating_id, rating)


@app.post("/removeRating", tags=["CR User"])
async def remove_data(course_id: str, user_id: str, rating_id: str, current_user: User = Depends(get_current_active_user)):
    return removeCourseRating(course_id, user_id, rating_id)


@app.post("/updateSemester", tags=["CR User"])
async def remove_data(course_id: str, user_id: str, semester: str, current_user: User = Depends(get_current_active_user)):
    return updateSemester(course_id, user_id, semester)


@app.post("/token", response_model=Token, tags=["CR Authentication"])
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
