from fastapi import FastAPI, HTTPException
from app.schemas import PostCreate, PostResponse

app = FastAPI()

text_posts = {
    1: {"title": "First Post", "content": "This is my first post!"},
    2: {"title": "Second Post", "content": "This is my second post!"},
    3: {"title": "Third Post", "content": "This is my third post!"},
    4: {"title": "Fourth Post", "content": "This is my fourth post!"},
    5: {"title": "Fifth Post", "content": "This is my fifth post!"},
    6: {"title": "Sixth Post", "content": "This is my sixth post!"},
    7: {"title": "Seventh Post", "content": "This is my seventh post!"},
    8: {"title": "Eighth Post", "content": "This is my eighth post!"},
    9: {"title": "Ninth Post", "content": "This is my ninth post!"},
    10: {"title": "Tenth Post", "content": "This is my tenth post!"},
}


@app.get("/posts")
def get_all_posts(limit: int = None):
    if limit:
        return dict(list(text_posts.items())[:limit])
    return text_posts


@app.get("/posts/{id}")
def get_post(id: int) -> PostResponse:
    if id not in text_posts:
        raise HTTPException(status_code=404, detail="Post not found")

    return text_posts.get(id, {"error": "Post not found"})


@app.post("/posts")
def create_post(post: PostCreate) -> PostResponse:
    new_post = {
        "title": post.title,
        "content": post.content,
    }
    text_posts[max(text_posts.keys()) + 1] = new_post
    return new_post
