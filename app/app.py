from fastapi import FastAPI, HTTPException, File, UploadFile, Form, Depends
from app.schemas import PostCreate, PostResponse
from app.db import Post, create_db_and_tables, get_async_session
from sqlalchemy.ext.asyncio import AsyncSession
from contextlib import asynccontextmanager
from sqlalchemy.future import select
from app.images import imagekit
import shutil
import os
import uuid
import tempfile


@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_db_and_tables()
    yield


app = FastAPI(lifespan=lifespan)


@app.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    caption: str = Form(""),
    session: AsyncSession = Depends(get_async_session),
):
    temp_file_path = None

    try:
        suffix = os.path.splitext(file.filename)[1]
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
            temp_file_path = temp_file.name
            shutil.copyfileobj(file.file, temp_file)

        with open(temp_file_path, "rb") as f:
            upload_result = imagekit.files.upload(
                file=f,
                file_name=file.filename,
                tags=["backend-upload"],
            )

        if not upload_result or not upload_result.url:
            raise HTTPException(status_code=400, detail="Image upload failed")

        content_type = file.content_type or ""
        file_type = "video" if content_type.startswith("video/") else "image"

        post = Post(
            caption=caption,
            url=upload_result.url,
            file_type=file_type,
            file_name=upload_result.name,
        )

        session.add(post)
        await session.commit()
        await session.refresh(post)

        return {
            "id": post.id,
            "caption": post.caption,
            "url": post.url,
            "file_type": post.file_type,
            "file_name": post.file_name,
            "created_at": post.created_at.isoformat() if post.created_at else None,
        }

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        if temp_file_path and os.path.exists(temp_file_path):
            os.unlink(temp_file_path)


@app.get("/feed")
async def get_feed(
    session: AsyncSession = Depends(get_async_session),
):
    result = await session.execute(select(Post).order_by(Post.created_at.desc()))
    posts = result.scalars().all()

    posts_data = []
    for post in posts:
        posts_data.append(
            {
                "id": post.id,
                "caption": post.caption,
                "url": post.url,
                "file_type": post.file_type,
                "file_name": post.file_name,
                "created_at": post.created_at.isoformat() if post.created_at else None,
            }
        )

    return {"posts": posts_data}
