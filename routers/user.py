from _cffi_backend import typeof

from app import utils, models, schemas
from sqlalchemy.orm import Session
from fastapi import FastAPI, Response, status, HTTPException, Depends,APIRouter
from app.database import engine, get_db


#############################################################################################
## start users operations

# set the prefix to each route to be -> /sqlalchemy/posts/
# like a const , this way we don't have to specify the prefix for each route
router = APIRouter(
    prefix="/sqlalchemy/users",
    tags=['Users']                      # this will separate the documentation on the swagger
)


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.UserOut)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    # hash the password - user.password

    print(f"email to create user :  {user.email}")


    # userExist = db.query(models.User).filter(models.User.email == user.email).first()
    # if userExist:
    #     print(f"user exists ... {userExist} for -> {user.email} ")
    #     raise HTTPException(status_code=status.HTTP_409_CONFLICT,detail=f"user with email: {user.email} already exist")

    print(f"before hash,  user: {user.email}     password:       {user.password}")

    hashed_password = utils.hash(user.password)

    print(f"hashed password:  {hashed_password}  {type(hashed_password)} ")

    user.password = hashed_password

    new_user = models.User(**user.dict())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


@router.get("/{id}", response_model=schemas.UserOut)
def get_user(id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"User with id: {id} not exist")
    return user
