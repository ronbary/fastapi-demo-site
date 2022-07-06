import time
import uvicorn
from typing import List
from fastapi import FastAPI, Response, status, HTTPException
import psycopg2
from psycopg2.extras import RealDictCursor

################################################  import all the sqlalchemy and models related
# in order to create the ORM tables automatically
from starlette.middleware.cors import CORSMiddleware

from app import models , auth

from app.database import engine

from app.schemas import PostCreate, Post   # we placed our schemas class in separate file

from routers import post,user,vote       # import the post and user , vote implementation using the routers

from app.config import settings # import the settings class that holds all the environment variables

# this line tell sqlalchemy to build db tables according to our model
# models.Base.metadata.create_all(bind=engine)


# connect to the DB (host: localhost / dbname: fastapi / user: postgres / password: 1234)
# loop until we connect to the db

# while True:
#     try:
#         conn = psycopg2.connect(host='localhost', database='fastapi', user='postgres',
#                                 password='1234', cursor_factory=RealDictCursor)
#         cursor = conn.cursor()
#         print("Database connection was successful")
#         break
#     except Exception as error:
#         print("Connecting to database failed")
#         print(f"Error: ", error)
#         time.sleep(4)  # sleep 2 sec
#
#
# # for debugging : printing value from the settings class holds all the environment variables
# print(f"db name: {settings.database_name}")



app = FastAPI()


# For example the origins is a list of sites we allow people from other domain to talk with our site
# this is how you specify which sites can access our apis
# if we want to allow all sites just place ["*"]
# origins = [
#     "https://www.google.com",
#     "http://localhost",
#     "http://localhost:8080",
# ]

# in order to make our site more secure just specify the outside domains
# that can access our site

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



# print(__name__)

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
    # uvicorn.run(app, host="127.0.0.1", port=8000)


# the order of the path matters , when typing only the address
# http://127.0.0.1:8000/ the default will be GET / so if I have two methods with same path the first
# one will be executed


# split the implementation into separate file using routers
######################################################################################
# when application will look for routes first when hit here it will go to
# search under post.py and user.py for matching route if found then this will be the route to response
# otherwise will keep looking here on the main.py
app.include_router(post.router)
app.include_router(user.router)
app.include_router(auth.router)
app.include_router(vote.router)

# this is the decorator that connect the "GET" HTTP method to the FastAPI
# the / means it's the root of the URL server

@app.get("/",status_code=status.HTTP_200_OK)
def root():
    return {"message": "message": "Hello from roni all tests passed ...  successfully deployed from CI into Heroku , cool!!"}
    # return {"message": "Hello from roni ...  this is my FastAPI site , cool!"}


@app.get("/favicon.ico", include_in_schema=False) # this is to hide this route
def root():
    return {"message": "Hello from ron"}

######################################################################################################
### Implementation of GET / GET{id} / POST / PUT / DELETE with regular SQL with Postgres db.
######################################################################################################

# my_posts this will be my data dictionary that hold all the posts for this server
# later we gona take the posts from a DB

my_posts = [{"title": "title of post 1", "content": "content of post 1", "id": 1},
            {"title": "favorite foods", "content": "i like pizza", "id": 2}
            ]


def find_post(id):
    post_out = {}
    for post in my_posts:
        if id == post['id']:
            post_out = post
            break
    return post_out


# find the index in our posts if no found return -1
def find_index_post(id):
    index = -1
    for i, p in enumerate(my_posts):
        if p['id'] == id:
            index = i
    return index


# this will return our posts from fastapi db in postgres
@app.get("/posts", response_model=List[Post])
def get_posts():
    cursor.execute("""SELECT * from posts""")
    posts = cursor.fetchall()  # return all posts from db
    return posts


# get specific post using id from the db
@app.get("/posts/{id}", response_model=Post)
def get_post(id: int):  # using FastAPI to enforce is will be Integer

    cursor.execute(f"""SELECT * from posts where id = %s""", (str(id),))
    post = cursor.fetchone()

    # post = find_post(id)

    if not post:  # chekcif post is null , it's like comparing to None
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id: {id} not found")
    return post


# create the post based on our Model Class we defined as a schema Class "Post" see above
# now it's easier to pass that data using Class object
# we can control the status code also


# implement the create new post into the fastapi db
@app.post("/posts", status_code=status.HTTP_201_CREATED, response_model=Post)
def create_posts(post: PostCreate):  # Post is our Model class act as our Schema
    cursor.execute("""INSERT INTO posts (title,content,published) VALUES (%s,%s,%s) RETURNING * """,
                   (post.title, post.content, post.published))

    # get the return created row in the posts table in the db
    new_post = cursor.fetchone()
    # commit the changes
    conn.commit()

    return new_post

    # post_dict = post.dict()
    # post_dict['id'] = random.randrange(0, 1000000)
    # my_posts.append(post_dict)
    # return {"data": my_posts}


# delete specific post in the db

@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int):
    # deleting post
    cursor.execute("""DELETE FROM posts WHERE id = %s RETURNING * """, (str(id),))
    deleted_post = cursor.fetchone()
    conn.commit()

    if deleted_post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id : {id} not exist")

    # post deleted . notify the user with 204 no content
    return Response(status_code=status.HTTP_204_NO_CONTENT)

    # find the index
    # index = find_index_post(id)
    # if index == -1:
    #     raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"post with is {id} does not exist")

    # if index != -1:
    #     my_posts.pop(index)
    #     return Response(status_code=status.HTTP_204_NO_CONTENT)


# the PUT is the update for posts in the db
@app.put("/posts/{id}", response_model=Post)
def update_post(id: int, post: PostCreate):  # Post is our Model class act as our Schema

    cursor.execute("""UPDATE posts SET title = %s, content = %s, published = %s WHERE id = %s RETURNING * """,
                   (post.title, post.content, post.published, str(id)))
    # return the update row
    update_post = cursor.fetchone()

    if update_post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with is {id} does not exist")

    conn.commit()
    return update_post

# index = find_index_post(id)
# if index == -1:
#     raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with is {id} does not exist")
#
# post_dict = post.dict()
# post_dict['id'] = id
# my_posts[index] = post_dict
# return {"data": post_dict}


# @app.post("/createposts")
# def create_posts(payLoad: dict = Body(...)):
#     #print(payLoad)
#     return {"new post": f"tile: {payLoad['title']} content: {payLoad['content']}"}

#
# # create the post based on our Model Class we defined as a schema Class "Post" see above
# # now it's easier to pass that data using Class object
# @app.post("/posts")
# def create_posts(post: Post):  # Post is out Model class act as our Schema
#     # print(f"post Title:  {new_post.title} post content: {new_post.content}")
#     print(f"published:  {post.published}")
#     print(f"rating:  {post.rating}")
#     print(post)
#     print(post.dict())                  # we can convert our model class into dictionary
#     return {"new post" : "created new post."}
