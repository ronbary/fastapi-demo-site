from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import settings         # import the settings class that holds all the environment variables



#######################################################################
## Example how to connect to the DB with ORM and python

# SQLALCHEMY_DATABASE_URL = "postgresql://user:password@db_hostname:db_port/db_name"

# SQLALCHEMY_DATABASE_URL = "postgresql://postgres:1234@localhost/fastapi"

# use the environment variables to build the connection string to postgres
SQLALCHEMY_DATABASE_URL = f"postgresql://{settings.database_username}:{settings.database_password}@" \
                          f"{settings.database_hostname}:{settings.database_port}/{settings.database_name}"

engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()     # this Base class will be base Class to define the model ORM table classes

#######################################################################


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
