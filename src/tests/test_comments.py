import httpx
import pytest
from sqlalchemy import select, insert
from .conftest import async_session_test
from auth.jwt_handler import create_access_token
from auth.hash_password import HashPassword
from models.users import User
from models.channels import Channel
from models.posts import Post
from models.comments import Comment
from schemas.users import UserIn
from schemas.channels import ChannelIn
from schemas.posts import PostIn
from schemas.comments import CommentIn

hash_password = HashPassword()

@pytest.fixture(scope='module')
async def access_token() -> str:
    return create_access_token('user1')

@pytest.fixture(scope='module')
async def access_token_other_user() -> str:
    return create_access_token('user2')

@pytest.fixture(autouse=True, scope='module')
async def mock_data() -> None:
    async with async_session_test() as session:
        password = 'password'
        hashed_password = hash_password.create_hash(password=password)
        user = UserIn(username='user1', password=hashed_password, email='user1@gmail.com')
        await session.execute(insert(User).values(**user.dict()))

        password = 'password123'
        hashed_password = hash_password.create_hash(password=password)
        user = UserIn(username='user2', password=hashed_password, email='user2@gmail.com')
        await session.execute(insert(User).values(**user.dict()))

        user_id = await session.execute(select(User.id))
        channel = ChannelIn(name='channel', avatar='avatar', description='desc')
        await session.execute(insert(Channel).values(user_id=user_id.scalar(), **channel.dict()))

        channel_id = await session.execute(select(Channel.id))
        post = PostIn(name='post', description='desc')
        await session.execute(insert(Post).values(channel_id=channel_id.scalar(), **post.dict()))

        comment_user_id = await session.execute(select(User.id))
        comment_post_id = await session.execute(select(Post.id))
        comment = CommentIn(description='comment')
        await session.execute(insert(Comment).values(user_id=comment_user_id.scalar(),
                                                     post_id=comment_post_id.scalar(), **comment.dict()))

        await session.commit()

async def test_comment_get_all(default_client: httpx.AsyncClient) -> None:
    response = await default_client.get('/comments/')
    assert response.status_code == 200
    assert response.json()[0]['description'] == 'comment'

async def test_comment_get_by_id(default_client: httpx.AsyncClient) -> None:
    async with async_session_test() as session:
        id = await session.execute(select(Comment.id).where(Comment.description == 'comment'))
        response = await default_client.get(f'/comments/{id.scalar()}')
        assert response.status_code == 200
        assert response.json()['description'] == 'comment'

async def test_comment_create(default_client: httpx.AsyncClient, access_token: str) -> None:
    async with async_session_test() as session:
        id = await session.execute(select(Post.id))
        payload = {
            'description': 'new_comment'
        }
        headers = {
            'accept': 'application/json',
            'content-type': 'application/json',
            'authorization': f'Bearer {access_token}'
        }
        test_response = {
            'message': 'Comment created successfully'
        }
        response = await default_client.post(f'/comments/{id.scalar()}', json=payload, headers=headers)
        assert response.status_code == 200
        assert response.json() == test_response

async def test_comment_update(default_client: httpx.AsyncClient, access_token: str) -> None:
    async with async_session_test() as session:
        id = await session.execute(select(Comment.id))
        payload = {
            'description': 'new_comment'
        }
        headers = {
            'accept': 'application/json',
            'content-type': 'application/json',
            'authorization': f'Bearer {access_token}'
        }
        response = await default_client.put(f'/comments/{id.scalar()}', json=payload, headers=headers)
        assert response.status_code == 200
        assert response.json()['description'] == payload['description']

async def test_comment_update_stranger(default_client: httpx.AsyncClient, access_token_other_user: str) -> None:
    async with async_session_test() as session:
        id = await session.execute(select(Comment.id))
        payload = {
            'description': 'new_comment'
        }
        headers = {
            'accept': 'application/json',
            'content-type': 'application/json',
            'authorization': f'Bearer {access_token_other_user}'
        }
        test_response = {
            'detail': 'User doesn`t have such a comment'
        }
        response = await default_client.put(f'/comments/{id.scalar()}', json=payload, headers=headers)
        assert response.status_code == 404
        assert response.json() == test_response

async def test_comment_delete(default_client: httpx.AsyncClient, access_token: str) -> None:
    async with async_session_test() as session:
        id = await session.execute(select(Comment.id))
        headers = {
            'accept': 'application/json',
            'authorization': f'Bearer {access_token}'
        }
        test_response = {
            'message': 'Comment deleted successfully'
        }
        response = await default_client.delete(f'/comments/{id.scalar()}', headers=headers)
        assert response.status_code == 200
        assert response.json() == test_response

async def test_comment_delete_stranger(default_client: httpx.AsyncClient, access_token_other_user: str) -> None:
    async with async_session_test() as session:
        id = await session.execute(select(Comment.id))
        headers = {
            'accept': 'application/json',
            'authorization': f'Bearer {access_token_other_user}'
        }
        test_response = {
            'detail': 'User doesn`t have such a comment'
        }
        response = await default_client.delete(f'/comments/{id.scalar()}', headers=headers)
        assert response.status_code == 404
        assert response.json() == test_response
