from fastapi import FastAPI, HTTPException, File, UploadFile, Form, Depends
from app.schemas import PostCreate, PostResponse
from app.db import Post, create_db_and_tables, get_async_session
from sqlalchemy.ext.asyncio import AsyncSession
from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_db_and_tables()
    yield


app = FastAPI(lifespan=lifespan)


@app.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    cpation: str = Form(""),
    session: AsyncSession = Depends(get_async_session),
):
    post = Post(
        caption=cpation,
        url=f"/files/{file.filename}",
        file_type=file.content_type,
        file_name=file.filename,
    )
    session.add(post)
    await session.commit()
