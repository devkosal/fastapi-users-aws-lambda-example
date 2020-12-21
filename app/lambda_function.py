import databases
import sqlalchemy
from fastapi import FastAPI, Request
from fastapi_users import FastAPIUsers, models
from fastapi_users.authentication import JWTAuthentication
from fastapi_users.db import SQLAlchemyBaseUserTable, SQLAlchemyUserDatabase
from sqlalchemy.ext.declarative import DeclarativeMeta, declarative_base
from sqlalchemy import Integer, String,  Date, Column
from typing import Optional
from pydantic import validator, conint
from datetime import date
from mangum import Mangum

# imports SECRET, db login details, project name, stage name (see README.md for sample varaibles)
from config import * 

import pymysql
pymysql.install_as_MySQLdb()

DATABASE_URL = f'mysql://{DB_USERNAME}:{DB_PASSWORD}@{DB_ADDRESS}/{DB_NAME}' if not testing else 'sqlite:///./test.db'

class User(models.BaseUser):
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip: Optional[int] = None
    country: Optional[str] = None
    # ge: greater than or equal to. le: less than or equal to
    country_code: Optional[conint(ge=1,le=999)] = 1
    phone_number: Optional[int] = None
    birth_date: Optional[date] = None # YYYY-MM-DD

class UserCreate(models.BaseUserCreate):
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip: Optional[int] = None
    country: Optional[str] = None
    # ge: greater than or equal to. le: less than or equal to
    country_code: Optional[conint(ge=1,le=999)] = 1
    phone_number: Optional[int] = None
    birth_date: Optional[date] = None # YYYY-MM-DD


class UserUpdate(User, models.BaseUserUpdate):
    pass


class UserDB(User, models.BaseUserDB):
    pass


database = databases.Database(DATABASE_URL)
Base: DeclarativeMeta = declarative_base()


class UserTable(Base, SQLAlchemyBaseUserTable):

    # overriding super class's table name and field(s)
    __tablename__ = "Users"
    email = Column(String(length=255), unique=True, index=True, nullable=False)

    # new fields
    address = Column(String(length=255), nullable=True)
    city = Column(String(length=255), nullable=True)
    state = Column(String(length=255), nullable=True)
    zip = Column(Integer(), nullable=True)
    country = Column(String(length=255), nullable=True)
    country_code = Column(Integer(), nullable=True)
    phone_number = Column(Integer(), nullable=True)
    birth_date = Column(Date(), nullable=True)


engine = sqlalchemy.create_engine(
    DATABASE_URL, connect_args={} # "check_same_thread": False
)
Base.metadata.create_all(engine)

users = UserTable.__table__
user_db = SQLAlchemyUserDatabase(UserDB, database, users)


def on_after_register(user: UserDB, request: Request):
    print(f"User {user.id} has registered.")


def on_after_forgot_password(user: UserDB, token: str, request: Request):
    print(f"User {user.id} has forgot their password. Reset token: {token}")


jwt_authentication = JWTAuthentication(
    secret=SECRET, lifetime_seconds=3600, tokenUrl="/auth/jwt/login"
)

app = FastAPI(
    title=PROJECT_NAME,
    openapi_prefix=STAGE_NAME # name of your stage on AWS
    )
fastapi_users = FastAPIUsers(
    user_db,
    [jwt_authentication],
    User,
    UserCreate,
    UserUpdate,
    UserDB,
)
app.include_router(
    fastapi_users.get_auth_router(jwt_authentication), prefix="/auth/jwt", tags=["auth"]
)
app.include_router(
    fastapi_users.get_register_router(on_after_register), prefix="/auth", tags=["auth"]
)
app.include_router(
    fastapi_users.get_reset_password_router(
        SECRET, after_forgot_password=on_after_forgot_password
    ),
    prefix="/auth",
    tags=["auth"],
)
app.include_router(fastapi_users.get_users_router(), prefix="/users", tags=["users"])


@app.on_event("startup")
async def startup():
    await database.connect()


@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()
    
@app.get("/")
def read_root():
    return root_response

lambda_handler = Mangum(app=app)