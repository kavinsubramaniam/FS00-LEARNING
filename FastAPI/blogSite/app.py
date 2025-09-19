from fastapi import FastAPI
from models import Blog, User
from sqlalchemy import create_engine

app = FastAPI()

DATABASE_URL = "sqlite:///blogDataBase.db"
engine = create_engine(DATABASE_URL)
conn = engine.connect()

# @app.post("/create-user")

# @app.post("/create-blog")
# @app.get("/blog/{id}")
# @app.put("/blog/update/{id}")
# @app.delete("/blog/delete/{id}")
