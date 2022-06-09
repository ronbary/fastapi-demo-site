from fastapi import FastAPI, Response, status, HTTPException, Depends ,APIRouter
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app import models, schemas , utils , oauth2
from app.database import engine, get_db
from sqlalchemy.orm import Session


router = APIRouter(tags=['Authentication'])

# The user_credentials is of type OAuth2PasswordRequestForm , we can check the username field that
# was passed in the request form body
# The OAuth2PasswordRequestForm store the first field in a field called "username"

@router.post('/sqlalchemy/login',response_model=schemas.Token)
def login(user_credentials: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):

    # username
    # password
    user = db.query(models.User).filter(models.User.email == user_credentials.username).first()

    if (not user) or (not utils.verify(user_credentials.password,user.password)):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"Invalid Credentials")
    # create a token
    # return the token
    access_token = oauth2.create_access_token(data = {"user_id": user.id})

    return {"access_token": access_token, "token_type": "bearer"}