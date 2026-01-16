from pydantic import BaseModel


class PostCreate(BaseModel):
    title: str
    content: str


class PostResponse(PostCreate):
    title: str
    content: str
