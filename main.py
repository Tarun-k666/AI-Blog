from fastapi import FastAPI, Request, HTTPException, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException as starlettehttpexception
from schemas import PostCreate, PostResponse

posts: list[dict] = [
    {
        "id": 1,
        "author": "Tarun Kumar",
        "title": "Getting Started with AI",
        "content": "This post explains the basics of artificial intelligence and how to begin learning it.",
        "date_posted": "2026-01-10"
    },
    {
        "id": 2,
        "author": "Ananya Sharma",
        "title": "Python Automation Tips",
        "content": "Learn how to automate daily tasks using Python scripts and improve productivity.",
        "date_posted": "2026-01-12"
    },
    {
        "id": 3,
        "author": "Rahul Verma",
        "title": "Data Science Roadmap",
        "content": "A step-by-step roadmap to transition into a data science career.",
        "date_posted": "2026-01-14"
    }
]

templates=Jinja2Templates(directory='templates')

app=FastAPI()

app.mount('/static',StaticFiles(directory='static'), name='static')

@app.get("/", include_in_schema=False,name='home')
@app.get("/post", include_in_schema=False,name='post')
def home(request: Request):
    return templates.TemplateResponse(request, 'home.html', {"posts":posts,"title": "AI"},)

@app.get('/posts/{post_id}', include_in_schema=False)
def get_post(request: Request, post_id: int):
    for post in posts:
        if post.get("id") == post_id:
            return templates.TemplateResponse(request, 'posts.html', {"post":post, "title": post['title'][:50]})
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

@app.get('/api/posts',response_model=list[PostResponse])
def get_posts():
    return posts

@app.get('/api/post/{post_id}',response_model=PostResponse)
def get_posts(post_id: int):
    for post in posts:
        if post.get("id") == post_id:
            return post
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

@app.post(
    '/api/posts',
    response_model=PostCreate,
    status_code=status.HTTP_201_CREATED)
def create_post(post: PostCreate):
    new_id= max(p["id"] for id in posts)+1 if posts else 1
    new_post={
        "id":new_id,
        "author":post.author,
        "title":post.title,
        "content":post.content,
        "date_posted": "January 1 2025",
    }
    posts.append(new_post)

    return new_post


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

