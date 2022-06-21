import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.config import settings
from app.database import get_db, Base
from app.main import app
from app.oauth2 import create_access_token
from app import models

#  hardcoded the db connection string
# SQLALCHEMY_DATABASE_URL = 'postgresql://postgres:1234@localhost:5432/fastapi_test'

SQLALCHEMY_DATABASE_URL = f"postgresql://{settings.database_username}:{settings.database_password}@" \
                          f"{settings.database_hostname}:{settings.database_port}/{settings.database_name}_test"

# when creating postgres db in heroku
# it creates by default db URL connection string
# so we basically can use just the
# hard coded URL , but it's better to use it like separate variables like in my application

# SQLALCHEMY_DATABASE_URL = {settings.database_url}


engine = create_engine(SQLALCHEMY_DATABASE_URL)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# this line tell sqlalchemy to build db tables according to our model
# Base.metadata.create_all(bind=engine)


#######################################################################


# the TestClient is method from Fastapi lib and it acts like the
# request object in python
# client = TestClient(app)

# @pytest.fixture(scope="function")
@pytest.fixture(scope="function")
def session():
    # run our code before we run our test

    print("my session fixture run")

    # we can drop all tables after our test finish to run
    Base.metadata.drop_all(bind=engine)
    # create the tables in the db before test run
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


# the scop tell when it will run this fixture per each function / session/ module

@pytest.fixture(scope="function")
def client(session):
    def override_get_db():

        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)  # yield keyword is like return


# create fixture to return new user data
# this way any test that depend on creation on new user  like our "test_login_user"
# will call this fixture as an input parameter and will be independent
@pytest.fixture
def test_user(client):
    user_data = {"email": "soso123@gmail.com",
                 "password": "1234"}
    res = client.post("/sqlalchemy/users/", json=user_data)
    # print(res.json())
    assert res.status_code == 201
    new_user = res.json()
    new_user['password'] = user_data['password']
    return new_user

# create another user in db
@pytest.fixture
def test_user2(client):
    user_data = {"email": "sami123@gmail.com",
                 "password": "1234"}
    res = client.post("/sqlalchemy/users/", json=user_data)
    # print(res.json())
    assert res.status_code == 201
    new_user = res.json()
    new_user['password'] = user_data['password']
    return new_user


@pytest.fixture()
def token(test_user):
    return create_access_token({"user_id": test_user['id']})


@pytest.fixture()
def authorized_client(client, token):
    client.headers = {
        **client.headers,
        "Authorization": f"Bearer {token}"
    }

    return client


@pytest.fixture()
def test_posts(test_user,session,test_user2):
    posts_data= [{
        "title": "first tile",
        "content": "first content",
        "owner_id": test_user['id']
    }, {
        "title": "2nd tile",
        "content": "2nd content",
        "owner_id": test_user['id']
    }, {
        "title": "3rd tile",
        "content": "3rd content",
        "owner_id": test_user['id']
    },{
        "title": "4rd tile",
        "content": "4rd content",
        "owner_id": test_user2['id']
    }]

    # convert the dictionary of posts data to post models
    def create_post_model(post):
        return models.Post(**post)

    post_map = map(create_post_model, posts_data)
    posts = list(post_map)     # convert to list of posts

    session.add_all(posts)

    # session.add_all([models.Post(title="first title", content="first content",
    #                              owner_id=test_user['id']),
    #                  models.Post(title="2nd title", content="2nd content",
    #                              owner_id=test_user['id']),
    #                  models.Post(title="3rd title", content="3rd content",
    #                              owner_id=test_user['id'])])

    session.commit()

    session.query(models.Post).all()
    return posts

