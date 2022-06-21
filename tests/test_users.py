import pytest
from jose import jwt
from app import schemas  # use the UserOut in order to check the response quicker
from app.config import settings

def test_root(client):
    res = client.get("/")
    # print(res.json())               # to print the json that return from the response
    print(res.json().get('message'))
    assert res.json().get('message') == 'Hello from roni ...  this is my FastAPI site , cool!'
    assert res.status_code == 200  # here testing the status code


def test_create_user(client):
    res = client.post("/sqlalchemy/users/",
                      json={"email": "soso123@gmail.com", "password": "1234"})
    # print(res.json())
    # assert res.json().get("email") == "soso123@gmail.com"  # check the email field should return at the json response

    new_user = schemas.UserOut(**res.json())  # the way to extract the json into python object deserialize it.
    assert new_user.email == "soso123@gmail.com"
    assert res.status_code == 201


def test_login_user(test_user,client):
    # res = client.post(
    #     "/sqlalchemy/login",data={"username": "soso123@gmail.com", "password": "1234"})
    res = client.post(
        "/sqlalchemy/login",data={"username": test_user['email'], "password": test_user['password']})

    # add also more checks on the token and id that return from the login response
    login_res = schemas.Token(**res.json())
    payload = jwt.decode(login_res.access_token, settings.secret_key , algorithms=[settings.algorithm])
    id = payload.get("user_id")

    assert id == test_user['id']
    assert login_res.token_type == "bearer"

    # print(res.json())
    assert res.status_code == 200


@pytest.mark.parametrize("email,password,status_code",[
    ('wrongemail@gmail.com','1234',403),
    ('soso123@gmail.com', 'wrongpassword', 403),
    ('wrongemail@gmail.com', 'wrongpassword', 403),
    (None, '1234', 422),
    ('soso123@gmail.com', None, 422)
])
def test_incorrect_login(test_user,client,email,password,status_code):
    res = client.post(
        "/sqlalchemy/login", data={"username": email, "password": password})

    assert res.status_code == status_code
    # assert res.json().get('detail') == 'Invalid Credentials'