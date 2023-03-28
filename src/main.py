from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from routes.users import user_router
from routes.channels import channel_router
from routes.posts import post_router
from routes.comments import comment_router
from models.users import User
from models.channels import Channel
from models.posts import Post
from models.comments import Comment
from database.connection import Settings

app = FastAPI()

settings = Settings()

origins = ['*']

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(user_router, prefix='/users')
app.include_router(channel_router, prefix='/channels')
app.include_router(post_router, prefix='/posts')
app.include_router(comment_router, prefix='/comments')

@app.on_event('startup')
async def init_db() -> None:
    await settings.init_models()

if __name__ == '__main__':
    uvicorn.run('main:app', host='0.0.0.0', port=8000, reload=True)
