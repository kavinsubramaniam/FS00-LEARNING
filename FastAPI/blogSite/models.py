from pydantic import BaseModel

class Blog(BaseModel):
    blog_id: int
    author_id: int
    title: str
    description: str
    publication_date: str

class User(BaseModel):
    user_id: int
    name: str
    email: str
    password: str