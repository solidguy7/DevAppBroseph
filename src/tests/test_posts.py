import httpx
import pytest
from sqlalchemy import select, insert
from .conftest import async_session_test
from auth.jwt_handler import create_access_token
from auth.hash_password import HashPassword
from models.users import User, user_post
from models.channels import Channel
from models.posts import Post
from schemas.users import UserIn
from schemas.channels import ChannelIn
from schemas.posts import PostIn

hash_password = HashPassword()

@pytest.fixture(scope='module')
async def access_token() -> str:
    return create_access_token('ivan')

@pytest.fixture(scope='module')
async def access_token_other_user() -> str:
    return create_access_token('solidguy7')

@pytest.fixture(autouse=True, scope='module')
async def mock_data() -> None:
    async with async_session_test() as session:
        password = '123456789'
        hashed_password = hash_password.create_hash(password=password)
        user = UserIn(username='ivan', password=hashed_password, email='ivan@gmail.com')
        await session.execute(insert(User).values(**user.dict()))

        password = 'qwerty123'
        hashed_password = hash_password.create_hash(password)
        user = UserIn(username='solidguy7', password=hashed_password, email='solidguy7@gmail.com')
        await session.execute(insert(User).values(**user.dict()))

        user_id = await session.execute(select(User.id).where(User.username == 'ivan'))
        channel = ChannelIn(name='new_channel', avatar='new_avatar', description='new_desc')
        await session.execute(insert(Channel).values(user_id=user_id.scalar(), **channel.dict()))

        channel_user_id = await session.execute(select(User.id).where(User.username == 'ivan'))
        channel_id = await session.execute(select(Channel.id).where(Channel.user_id == channel_user_id.scalar()))
        post = PostIn(name='test_post', description='test_desc')
        await session.execute(insert(Post).values(channel_id=channel_id.scalar(), **post.dict()))

        await session.commit()

async def test_post_get_all(default_client: httpx.AsyncClient) -> None:
    response = await default_client.get('/posts/')
    assert response.status_code == 200
    assert response.json()[0]['name'] == 'test_post'

async def test_post_get_by_id(default_client: httpx.AsyncClient) -> None:
    async with async_session_test() as session:
        id = await session.execute(select(Post.id))
        response = await default_client.get(f'/posts/{id.scalar()}')
        assert response.status_code == 200
        assert response.json()['name'] == 'test_post'

async def test_post_create(default_client: httpx.AsyncClient, access_token: str) -> None:
    async with async_session_test() as session:
        id = await session.execute(select(Channel.id).where(Channel.name == 'new_channel'))
        payload = {
            'name': 'new_test_post',
            'description': 'new_test_desc'
        }
        headers = {
            'accept': 'application/json',
            'content-type': 'application/json',
            'authorization': f'Bearer {access_token}'
        }
        test_response = {
            'message': 'Post created successfully'
        }
        response = await default_client.post(f'/posts/{id.scalar()}', json=payload, headers=headers)
        assert response.status_code == 200
        assert response.json() == test_response

async def test_post_create_stranger(default_client: httpx.AsyncClient, access_token_other_user: str) -> None:
    async with async_session_test() as session:
        id = await session.execute(select(Channel.id))
        payload = {
            'name': 'new_test_post',
            'description': 'new_test_desc'
        }
        headers = {
            'accept': 'application/json',
            'content-type': 'application/json',
            'authorization': f'Bearer {access_token_other_user}'
        }
        test_response = {
            'detail': 'You don`t have such a post'
        }
        response = await default_client.post(f'/posts/{id.scalar()}', json=payload, headers=headers)
        assert response.status_code == 404
        assert response.json() == test_response

async def test_post_like(default_client: httpx.AsyncClient, access_token: str) -> None:
    async with async_session_test() as session:
        id = await session.execute(select(Post.id))
        headers = {
            'accept': 'application/json',
            'authorization': f'Bearer {access_token}'
        }
        test_response = {
            'message': 'You liked this post successfully'
        }
        response = await default_client.post(f'/posts/like/{id.scalar()}', headers=headers)
        assert response.status_code == 200
        assert response.json() == test_response

async def test_post_unlike(default_client: httpx.AsyncClient, access_token: str) -> None:
    async with async_session_test() as session:
        id = await session.execute(select(Post.id))
        id = id.scalar()
        user_id = await session.execute(select(User.id))
        user_id = user_id.scalar()
        await session.execute(insert(user_post).values(user_id=user_id, post_id=id))
        await session.commit()
        headers = {
            'accept': 'application/json',
            'authorization': f'Bearer {access_token}'
        }
        test_response = {
            'message': 'You unliked this post successfully'
        }
        response = await default_client.post(f'/posts/like/{id}', headers=headers)
        assert response.status_code == 200
        assert response.json() == test_response

async def test_post_update(default_client: httpx.AsyncClient, access_token: str) -> None:
    async with async_session_test() as session:
        id = await session.execute(select(Post.id))
        payload = {
            'name': 'new_test_post',
            'description': 'new_test_desc'
        }
        headers = {
            'accept': 'application/json',
            'content-type': 'application/json',
            'authorization': f'Bearer {access_token}'
        }
        response = await default_client.put(f'/posts/{id.scalar()}', json=payload, headers=headers)
        assert response.status_code == 200
        assert response.json()['name'] == payload['name']

async def test_post_update_stranger(default_client: httpx.AsyncClient, access_token_other_user: str) -> None:
    async with async_session_test() as session:
        id = await session.execute(select(Post.id))
        payload = {
            'name': 'new_test_post',
            'description': 'new_test_desc'
        }
        headers = {
            'accept': 'application/json',
            'content-type': 'application/json',
            'authorization': f'Bearer {access_token_other_user}'
        }
        test_response = {
            'detail': 'You don`t have such a post'
        }
        response = await default_client.put(f'/posts/{id.scalar()}', json=payload, headers=headers)
        assert response.status_code == 404
        assert response.json() == test_response

async def test_post_delete(default_client: httpx.AsyncClient, access_token: str) -> None:
    async with async_session_test() as session:
        id = await session.execute(select(Post.id))
        headers = {
            'accept': 'application/json',
            'authorization': f'Bearer {access_token}'
        }
        test_response = {
            'message': 'Post deleted successfully'
        }
        response = await default_client.delete(f'/posts/{id.scalar()}', headers=headers)
        assert response.status_code == 200
        assert response.json() == test_response

async def test_post_delete_stranger(default_client: httpx.AsyncClient, access_token_other_user: str) -> None:
    async with async_session_test() as session:
        id = await session.execute(select(Post.id))
        headers = {
            'accept': 'application/json',
            'authorization': f'Bearer {access_token_other_user}'
        }
        test_response = {
            'detail': 'You don`t have such a post'
        }
        response = await default_client.delete(f'/posts/{id.scalar()}', headers=headers)
        assert response.status_code == 404
        assert response.json() == test_response
