import httpx
import pytest

@pytest.mark.asyncio
async def test_sign_up(default_client: httpx.AsyncClient) -> None:
    payload = {
        'username': 'test',
        'password': '123',
        'email': 'test@gmail.com'
    }
    headers = {
        'accept': 'application/json',
        'content-type': 'application/json'
    }
    test_response = {
        'message': 'User created successfully'
    }
    response = await default_client.post('/users/signup', json=payload, headers=headers)
    assert response.status_code == 200
    assert response.json() == test_response

@pytest.mark.asyncio
async def test_sign_in(default_client: httpx.AsyncClient) -> None:
    payload = {
        'username': 'test',
        'password': '123'
    }
    headers = {
        'accept': 'application/json',
        'content-type': 'application/x-www-form-urlencoded'
    }
    response = await default_client.post('/users/signin', data=payload, headers=headers)
    assert response.status_code == 200
    assert response.json()['token_type'] == 'Bearer'