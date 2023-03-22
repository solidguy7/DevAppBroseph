from fastapi import APIRouter
from models.comments import Comment
from database.database import Database

comment_router = APIRouter(tags=['Comments'])
