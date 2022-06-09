# utils files
from passlib.context import CryptContext

# for the encryption of the passwords in the db
# define which hash algorithm we want to use ( in this case "bcrypt" )
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash(password: str):
    return pwd_context.hash(password)

def verify(plain_password, hashed_password):
    return pwd_context.verify(plain_password,hashed_password)