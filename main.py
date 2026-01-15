from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles


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

@app.get('/api/posts')
def get_posts(request: Request):
    return templates.TemplateResponse(request, 'posts.html', {"posts":posts} )
