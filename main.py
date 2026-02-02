import email
from pyexpat import model
from turtle import mode
from typing import Annotated
from unittest import result

from fastapi import (Depends, FastAPI, HTTPException, Request, staticfiles,
                     status)
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from sqlalchemy.orm import Session
from starlette.exceptions import HTTPException as starlettehttpexception

import models
from database import Base, engine, get_db
from schemas import PostCreate, PostResponse, UserCreate, UserResponse

Base.metadata.create_all(bind=engine)

templates=Jinja2Templates(directory='templates')

app=FastAPI()

app.mount('/static',StaticFiles(directory='static'), name='static')
app.mount('/media', StaticFiles(directory='media'), name='media')

@app.post(
    '/api/signup',
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate, db: Annotated[Session, Depends(get_db)]):
    result= db.execute(
        select(models.User).where(models.User.username == user.username),
        )
    existing_user = result.scalars().first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Username already exists',
        )
    result= db.execute(
        select(models.User).where(models.User.email == user.email),
        )
    existing_email = result.scalars().first()
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Email already exists',
        )
    new_user=models.User(
        username=user.username,
        email= user.email,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user

@app.get('/api/users/{user_id}',response_model=UserResponse)
def get_user(user_id: int, db: Annotated[Session, Depends(get_db)]):
    result = db.execute(
        select(models.User).where(models.User.id == user_id),
        )
    user=result.scalars().first()

    if user:
        return user
    
    raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='User does not exist',
        )

@app.get('/api/users/{user_id}/posts', response_model=list[PostResponse])
def get_user_posts(user_id: int, db: Annotated[Session, Depends(get_db)]):
    result = db.execute(
        select(models.User).where(models.User.id == user_id),
        )
    user=result.scalars().first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='User does not exist',
        )

    result = db.execute(
        select(models.Posts).where(models.Posts.user_id == user_id),
        )
    
    posts=result.scalars().all()

    return posts

@app.get('/api/posts',response_model=list[PostResponse])
def get_posts(db: Annotated[Session,Depends(get_db)]):
    result = db.execute(
        select(models.Posts)
    )
    posts=result.scalars().all()
    return posts

@app.get('/api/post/{post_id}',response_model=PostResponse)
def get_posts(post_id: int, db: Annotated[Session, Depends(get_db)]):
    result= db.execute(
        select(models.Posts).where(models.Posts.id == post_id)
    )
    post=result.scalars().first()
    if post:
        return post
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

@app.post(
    '/api/posts',
    response_model=list[PostResponse],
    status_code=status.HTTP_201_CREATED)
def create_post(post: PostCreate, db: Annotated[Session, Depends(get_db)]):
    result = db.execute(
        select(models.User).where(models.User.id == user_id)
    )
    user=result.scalars().first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='User does not exist',
        )
    
    new_post=models.Posts(
        user_id= post.user_id,
        title = post.title,
        content = post.content,
    )
    db.add(new_post)
    db.commit()
    db.refresh(new_post)

    return new_post

@app.get("/", include_in_schema=False,name='home')
@app.get("/post", include_in_schema=False,name='post')
def home(request: Request, db: Annotated[Session,Depends(get_db)]):

    result = db.execute(
        select(models.Posts)
    )
    posts=result.scalars().all()
    return templates.TemplateResponse(request, 'home.html', {"posts":posts,"title": "AI"},)

@app.get('/posts/{post_id}', include_in_schema=False)
def get_post(request: Request, post_id: int, db: Annotated[Session,Depends(get_db)]):
    result= db.execute(
        select(models.Posts).where(models.Posts.id == post_id)
    )
    post=result.scalars().first()
    if post:
        return templates.TemplateResponse(request, 'posts.html', {"post":post, "title": post['title'][:50]})
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

@app.get('/Users/{user_id}/posts', include_in_schema=False)
def get_user_posts(request: Request, user_id: int, db: Annotated[Session, Depends(get_db)]):
    result = db.execute(
        select(models.User).where(models.User.id == user_id)
    )
    user=result.scalars().first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='User does not exist',
        )
    
    result = db.execute(
        select(models.Posts).where(models.Posts.user_id == user_id)
    )
    posts=result.scalars().all()

    return templates.TemplateResponse(
        request, 'user_posts.html', {'posts':posts, 'title':f"{user.username}'s posts" }
    )


@app.exception_handler(starlettehttpexception)
def general_http_exception_handler(request: Request, exception: starlettehttpexception):
    message=(
        exception.detail
        if exception.detail
        else "An error occured"
    )
    if request.url.path.startswith('/api'):
        return JSONResponse(
            status_code=exception.status_code,
            content={'detail': message}
        )
    return templates.TemplateResponse(
        request,
        "error.html",
        {
            
            "status_code": exception.status_code,
            "title": exception.status_code,
            "message": message,
        },
        status_code=exception.status_code
    )

@app.exception_handler(RequestValidationError)
def request_validation_exception_handler(request: Request, exception: RequestValidationError):
    if request.url.path.startswith('/api'):
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            content={'detail': exception.errors()}
        )
    return templates.TemplateResponse(
        request,
        "error.html",
        {
            'status_code': status.HTTP_422_UNPROCESSABLE_CONTENT,
            'title': status.HTTP_422_UNPROCESSABLE_CONTENT,
            "message": "Invalid Request! Please check your input"          
        },
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
    )

