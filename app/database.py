from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import settings         # import the settings class that holds all the environment variables



#######################################################################
## Example how to connect to the DB with ORM and python

# SQLALCHEMY_DATABASE_URL = "postgresql://user:password@db_hostname:db_port/db_name"

# SQLALCHEMY_DATABASE_URL = "postgresql://postgres:1234@localhost/fastapi"

# use the environment variables to build the connection string to postgres
# 1. in local mode all the environment variables taken from .env file
# 2. in production or heroku site server all the environment variables taken from the Config Vars under settings
# under the application dashboard.
SQLALCHEMY_DATABASE_URL = f"postgresql://{settings.database_username}:{settings.database_password}@" \
                          f"{settings.database_hostname}:{settings.database_port}/{settings.database_name}"



# when creating postgres db in heroku
# it creates by default db URL connection string
# so we basically can use just the
# hard coded URL , but it's better to use it like separate variables like in my application

#SQLALCHEMY_DATABASE_URL = {settings.database_url}


engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()     # this Base class will be base Class to define the model ORM table classes

#######################################################################


# Dependency
def get_db():

    print(SQLALCHEMY_DATABASE_URL)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
