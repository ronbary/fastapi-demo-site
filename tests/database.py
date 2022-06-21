import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.config import settings
from app.database import get_db, Base
from app.main import app

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
