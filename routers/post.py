from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from app import models, schemas, oauth2
from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter
from app.database import engine, get_db

# set the prefix to each route to be -> /sqlalchemy/posts/
# like a const , this way we don't have to specify the prefix for each route
router = APIRouter(
    prefix="/sqlalchemy/posts",
    tags=['Posts']  # this will separate the documentation on the swagger
)


# example how to use the ORM with sqlalchemy package to do the same get_posts /posts that we
# did with regular SQL and postgres
# to talk with the postgres DB
# we pass the get_db  this will get the session with the DB

# we can add query parameter e.g: limit parameter that limit the number of Post results
# skip - parameter to specify how many items to skip from the begining
#


# @router.get("/",
#         response_model=List[schemas.PostOut])  # we return a List of Post per each post entry like that List[Post]


@router.get("/",
            response_model=List[schemas.PostOut])  # we return a List of Post per each post entry like that List[Post]
def get_posts(db: Session = Depends(get_db),
              current_user: int = Depends(oauth2.get_current_user),
              limit: int = 10, skip: int = 0,
              search: Optional[str] = ""):
    print(f"search query parameter = {search}")
    print(f"limit query parameter = {limit}")
    print(f"user email: {current_user.email}")

    # specify the model to return from the db using the (ORM)
    # in our case we want to return the "Post" model that map to table --> posts2 in the db
    # it's abstract all the sql from us

    # this will return all the posts for all users based on the limit query parameter (specify how much to return)
    # skip define how many results to skip
    # search - will filter and return only title that contains the "search"  e.g : {{URL}}sqlalchemy/posts?search=hello
    # to search with space between words use -> %20  as a space , e.g: {{URL}}sqlalchemy/posts?search=hello%20roni
    # this will search for 'hello roni' string in the title

    posts = db.query(models.Post).filter(models.Post.title.contains(search)).limit(limit).offset(skip).all()

    # search - will filter and return only content that contains the "search"
    # posts = db.query(models.Post).filter(models.Post.content.contains(search)).limit(limit).offset(skip).all()

    # this will return just posts for the login user id.

    # posts = db.query(models.Post).filter(
    #         models.Post.owner_id == current_user.id).all()

    # return posts

    # return the join of posts2 with user_votes same
    posts = db.query(models.Post, func.count(models.Vote.post_id).label("votes")).join(
        models.Vote, models.Vote.post_id == models.Post.id, isouter=True).group_by(models.Post.id) \
        .filter(models.Post.title.contains(search)).limit(limit).offset(skip).all()

    # print(results)

    return posts

    # this model return the query sql
    # posts = db.query(models.Post)
    # print(posts.statement)
    # return {"status": "successful"}


# implement the create posts using orm and sqlalchemy lib
@router.post("/", status_code=status.HTTP_201_CREATED,
             response_model=schemas.Post)  # define to return back the Post model
def create_posts(post: schemas.PostCreate, db: Session = Depends(get_db),
                 current_user: int = Depends(oauth2.get_current_user)):
    # new_post = models.Post(title=post.title,content=post.content,published=post.published)

    # putting extra dependency to the Create Post operation
    # the parameter "user_id" create the dependency that force the user to be logged in
    # This line in the function parameter create the dependency ->  "user_id: int = Depends(oauth2.get_current_user)"
    print(f"user email: {current_user.email}")

    # unpack the post dictionary this way we don't need to code all the fields in this dictionary manually
    new_post = models.Post(owner_id=current_user.id, **post.dict())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post


# implement the get posts {id} using orm and sqlalchemy lib
@router.get("/{id}", response_model=schemas.PostOut)
def get_post(id: int, db: Session = Depends(get_db),
             current_user: int = Depends(oauth2.get_current_user)):
    print(f"user email: {current_user.email}")
    # return the post using that match the id

    #post = db.query(models.Post).filter(models.Post.id == id).first()

    # return also the number of votes for this post using JOIN between tables ( posts and user_votes  )
    post = db.query(models.Post, func.count(models.Vote.post_id).label("votes")).join(
        models.Vote, models.Vote.post_id == models.Post.id, isouter=True).group_by(models.Post.id).\
        filter(models.Post.id == id).first()


    if not post:  # chekcif post is null , it's like comparing to None
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id: {id} not found")

    # This filter will prevent to get other post from other users , and let
    # you get only post for the login user id.

    # if post.owner_id != current_user.id:
    #     raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
    #                         detail=f"not authorized to perform requested operation")

    return post


# implement the delete posts {id} using orm and sqlalchemy lib
@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int, db: Session = Depends(get_db),
                current_user: int = Depends(oauth2.get_current_user)):
    # deleting post
    print(f"user email: {current_user.email}")
    post_query = db.query(models.Post).filter(models.Post.id == id)

    post = post_query.first()

    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id : {id} not exist")

    if post.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"not authorized to perform requested operation")

    post_query.delete(synchronize_session=False)
    db.commit()

    # post deleted . notify the user with 204 no content
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# implement the PUT update a posts with {id} using orm and sqlalchemy lib
@router.put("/{id}", response_model=schemas.Post)
def update_post(id: int, updated_post: schemas.PostCreate,
                db: Session = Depends(get_db),
                current_user: int = Depends(oauth2.get_current_user)):  # Post is our Model class act as our Schema

    print(f"user email: {current_user.email}")
    post_query = db.query(models.Post).filter(models.Post.id == id)

    post = post_query.first()

    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with is {id} does not exist")

    if post.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"not authorized to perform requested operation")

    post_query.update(updated_post.dict(), synchronize_session=False)
    db.commit()

    return post_query.first()
