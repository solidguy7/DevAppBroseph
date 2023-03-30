import httpx

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

async def test_user_exists_before_sign_up(default_client: httpx.AsyncClient) -> None:
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
        'detail': 'User with email provided exists already.'
    }
    response = await default_client.post('/users/signup', json=payload, headers=headers)
    assert response.status_code == 409
    assert response.json() == test_response

async def test_user_with_credentials_after_sign_up(default_client: httpx.AsyncClient) -> None:
    payload = {
        'username': 'unknown_test',
        'password': '12345'
    }
    headers = {
        'accept': 'application/json',
        'content-type': 'application/x-www-form-urlencoded'
    }
    test_response = {
        'detail': 'User with such credentials does not exist'
    }
    response = await default_client.post('/users/signin', data=payload, headers=headers)
    assert response.status_code == 404
    assert response.json() == test_response

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