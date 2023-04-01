import httpx
import pytest
from sqlalchemy import select, insert
from .conftest import async_session_test
from auth.hash_password import HashPassword
from auth.jwt_handler import create_access_token
from models.users import User, user_channel
from models.channels import Channel
from schemas.channels import ChannelIn

hash_password = HashPassword()

@pytest.fixture(scope='module')
async def access_token() -> str:
    return create_access_token('test_user')

@pytest.fixture(scope='module')
async def access_token_other_user() -> str:
    return create_access_token('kirill')

@pytest.fixture(autouse=True, scope='module')
async def mock_data():
    async with async_session_test() as session:
        password1 = '12345'
        hashed_password1 = hash_password.create_hash(password=password1)
        await session.execute(insert(User).values(username='test_user', password=hashed_password1, email='test_user@gmail.com'))

        password2 = 'qwerty'
        hashed_password2 = hash_password.create_hash(password2)
        await session.execute(insert(User).values(username='kirill', password=hashed_password2, email='kirill@gmail.com'))

        user_id = await session.execute(select(User.id).where(User.username == 'test_user'))
        user_id = user_id.scalar()
        channel = ChannelIn(name='test_channel', avatar='test_avatar', description='test_desc')
        await session.execute(insert(Channel).values(user_id=user_id, **channel.dict()))

        await session.commit()

async def test_channel_get_all(default_client: httpx.AsyncClient) -> None:
    response = await default_client.get('/channels/')
    assert response.status_code == 200
    assert response.json()[0]['name'] == 'test_channel'

async def test_channel_get_by_id(default_client: httpx.AsyncClient) -> None:
    async with async_session_test() as session:
        id = await session.execute(select(Channel.id))
        response = await default_client.get(f'/channels/{id.scalar()}')
        assert response.status_code == 200
        assert response.json()['name'] == 'test_channel'

async def test_channel_create(default_client: httpx.AsyncClient, access_token: str) -> None:
    payload = {
        'name': 'new_test_channel',
        'avatar': 'new_test_avatar',
        'description': 'new_test_desc'
    }
    headers = {
        'accept': 'application/json',
        'content-type': 'application/json',
        'authorization': f'Bearer {access_token}'
    }
    test_response = {
        'message': 'Channel created successfully'
    }
    response = await default_client.post('/channels/', json=payload, headers=headers)
    assert response.status_code == 200
    assert response.json() == test_response

async def test_channel_create_without_authorization(default_client: httpx.AsyncClient) -> None:
    payload = {
        'name': 'new_test_channel',
        'avatar': 'new_test_avatar',
        'description': 'new_test_desc'
    }
    headers = {
        'accept': 'application/json',
        'content-type': 'application/json',
    }
    test_response = {
        "detail": "Not authenticated"
    }
    response = await default_client.post('/channels/', json=payload, headers=headers)
    assert response.status_code == 401
    assert response.json() == test_response

async def test_channel_follow(default_client: httpx.AsyncClient, access_token_other_user: str) -> None:
    async with async_session_test() as session:
        id = await session.execute(select(Channel.id))
        headers = {
            'accept': 'application/json',
            'authorization': f'Bearer {access_token_other_user}'
        }
        test_response = {
            "message": "You followed this channel successfully"
        }
        response = await default_client.post(f'/channels/follow/{id.scalar()}', headers=headers)
        assert response.status_code == 200
        assert response.json() == test_response

async def test_channel_unfollow(default_client: httpx.AsyncClient, access_token_other_user: str) -> None:
    async with async_session_test() as session:
        id = await session.execute(select(Channel.id))
        id = id.scalar()
        user_id = await session.execute(select(User.id).where(User.username == 'kirill'))
        user_id = user_id.scalar()
        await session.execute(insert(user_channel).values(user_id=user_id, channel_id=id))
        await session.commit()
        headers = {
            'accept': 'application/json',
            'authorization': f'Bearer {access_token_other_user}'
        }
        test_response = {
            "message": "You unfollowed this channel successfully"
        }
        response = await default_client.post(f'/channels/follow/{id}', headers=headers)
        assert response.status_code == 200
        assert response.json() == test_response

async def test_channel_follow_own(default_client: httpx.AsyncClient, access_token: str) -> None:
    async with async_session_test() as session:
        id = await session.execute(select(Channel.id))
        headers = {
            'accept': 'application/json',
            'authorization': f'Bearer {access_token}'
        }
        test_response = {
            "detail": "You can`t follow your channels"
        }
        response = await default_client.post(f'/channels/follow/{id.scalar()}', headers=headers)
        assert response.status_code == 406
        assert response.json() == test_response

async def test_channel_put(default_client: httpx.AsyncClient, access_token: str) -> None:
    async with async_session_test() as session:
        id = await session.execute(select(Channel.id))
        payload = {
            'name': 'new_test_channel',
            'avatar': 'new_test_avatar',
            'description': 'new_test_desc'
        }
        headers = {
            'accept': 'application/json',
            'content-type': 'application/json',
            'authorization': f'Bearer {access_token}'
        }
        response = await default_client.put(f'/channels/{id.scalar()}', json=payload, headers=headers)
        assert response.status_code == 200
        assert response.json()['name'] == payload['name']

async def test_channel_put_stranger(default_client: httpx.AsyncClient, access_token_other_user: str) -> None:
    async with async_session_test() as session:
        id = await session.execute(select(Channel.id))
        payload = {
            'name': 'new_test_channel',
            'avatar': 'new_test_avatar',
            'description': 'new_test_desc'
        }
        headers = {
            'accept': 'application/json',
            'content-type': 'application/json',
            'authorization': f'Bearer {access_token_other_user}'
        }
        test_response = {
            "detail": "User doesn`t have such a channel"
        }
        response = await default_client.put(f'/channels/{id.scalar()}', json=payload, headers=headers)
        assert response.status_code == 404
        assert response.json() == test_response

async def test_channel_delete(default_client: httpx.AsyncClient, access_token: str) -> None:
    async with async_session_test() as session:
        id = await session.execute(select(Channel.id))
        headers = {
            'access': 'application/json',
            'authorization': f'Bearer {access_token}'
        }
        test_response = {
            "message": "Channel deleted successfully"
        }
        response = await default_client.delete(f'/channels/{id.scalar()}', headers=headers)
        assert response.status_code == 200
        assert response.json() == test_response

async def test_channel_delete_stranger(default_client: httpx.AsyncClient,
                                       access_token_other_user: str) -> None:
    async with async_session_test() as session:
        id = await session.execute(select(Channel.id))
        headers = {
            'access': 'application/json',
            'authorization': f'Bearer {access_token_other_user}'
        }
        test_response = {
            "detail": "User doesn`t have such a channel"
        }
        response = await default_client.delete(f'/channels/{id.scalar()}', headers=headers)
        assert response.status_code == 404
        assert response.json() == test_response
