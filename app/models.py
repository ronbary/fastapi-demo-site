from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql.expression import text
from sqlalchemy.sql.sqltypes import TIMESTAMP

from .database import Base


# this is the model class that will be created by the ( ORM )
# for example we will create table "posts2"  same as original posts table
# that we create manually in the postgres db

class Post(Base):
    __tablename__ = "posts2"

    id = Column(Integer, primary_key=True, index=True, nullable=False)
    title = Column(String, nullable=False)
    content = Column(String, nullable=False)
    published = Column(Boolean, server_default='TRUE', nullable=False)  # this will set the default to--> true
    # on the postgres server
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))

    # adding foreign key user_id -> point to users table
    owner_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    # define relationship using this feature from sqlalchemy
    # if does it automatically for us return the "User" class based
    # on the owner_id relationship
    owner = relationship("User")


# create users table to store credentials

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, nullable=False)
    email = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))


# creating class model for the user votes
class Vote(Base):
    __tablename__ = "user_votes"

    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    post_id = Column(Integer, ForeignKey("posts2.id", ondelete="CASCADE"), primary_key=True)

