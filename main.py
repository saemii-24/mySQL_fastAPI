from fastapi import FastAPI, HTTPException, Depends, status
# FastAPI: FastAPI 애플리케이션을 생성하는 클래스.
# HTTPException: HTTP 예외를 발생시키는 데 사용됨. 예를 들어, 리소스를 찾을 수 없는 경우 404 오류를 반환할 때 사용.
# Depends: 종속성 주입을 위해 사용됨. 함수나 경로 작업에서 의존성을 선언할 때 사용.
# status: HTTP 상태 코드를 쉽게 참조할 수 있도록 도와줌. 예를 들어, status.HTTP_201_CREATED는 HTTP 201 상태 코드를 나타냄.

from pydantic import BaseModel #데이터 검증과 설정을 위한 기본 모델을 정의
from typing import Annotated #타입 힌팅을 더 명확하게 표현
import models #데이터베이스 모델을 정의하는 모듈을 가져옴
from database import engine, SessionLocal #데이터베이스와의 연결을 관리하는 engine 객체와 데이터베이스 세션을 생성하는 SessionLocal 팩토리 함수
from sqlalchemy.orm import Session #데이터베이스 세션을 관리하며, 데이터베이스 쿼리와 트랜잭션을 처리

app = FastAPI()
# 데이터베이스에 모든 테이블을 생성함
models.Base.metadata.create_all(bind=engine)

# 요청과 응답 본문을 정의하는 Pydantic 모델

class PostBase(BaseModel):
    title: str
    content: str
    user_id: int

class UserBase(BaseModel):
    username: str

#업데이트 시 필드가 선택적(optional)일 수 있기 때문에 str | None 타입을 사용
class PostUpdate(BaseModel):
    title: str | None = None
    content: str | None = None

class UserUpdate(BaseModel):
    username: str | None = None

# 데이터베이스 세션을 가져오는 종속성 정의
def get_db():
    db = SessionLocal()  # 새로운 데이터베이스 세션을 생성함
    try:
        yield db  # 요청 함수에 세션을 제공함
    finally:
        db.close()  # 작업이 끝나면 세션을 닫음

db_dependency = Annotated[Session, Depends(get_db)]

# 새로운 포스트를 생성하는 엔드포인트
@app.post("/posts/", status_code=status.HTTP_201_CREATED)
async def create_post(post: PostBase, db: db_dependency):
    db_post = models.Post(**post.dict())  # 새로운 Post 인스턴스를 생성함
    db.add(db_post)  # 세션에 포스트를 추가함
    db.commit()  # 트랜잭션을 커밋함
    db.refresh(db_post)  # 업데이트된 상태를 가져옴
    return db_post

# 새로운 사용자를 생성하는 엔드포인트
@app.post("/users/", status_code=status.HTTP_201_CREATED)
async def create_user(user: UserBase, db: db_dependency):
    db_user = models.User(username=user.username)  # 새로운 User 인스턴스를 생성함
    db.add(db_user)  # 세션에 사용자를 추가함
    db.commit()  # 트랜잭션을 커밋함
    db.refresh(db_user)  # 업데이트된 상태를 가져옴
    return db_user

# ID로 사용자를 조회하는 엔드포인트
@app.get("/users/{user_id}", status_code=status.HTTP_200_OK)
async def read_user(user_id: int, db: db_dependency):
    user = db.query(models.User).filter(models.User.id == user_id).first()  # 데이터베이스에서 사용자를 조회함
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="사용자를 찾을 수 없음")  # 사용자 미발견 시 예외 발생
    return user

# ID로 포스트를 조회하는 엔드포인트
@app.get("/posts/{post_id}", status_code=status.HTTP_200_OK)
async def read_post(post_id: int, db: db_dependency):
    post = db.query(models.Post).filter(models.Post.id == post_id).first()  # 데이터베이스에서 포스트를 조회함
    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="포스트를 찾을 수 없음")  # 포스트 미발견 시 예외 발생
    return post

# ID로 포스트를 업데이트하는 엔드포인트
@app.put("/posts/{post_id}", status_code=status.HTTP_200_OK)
async def update_post(post_id: int, post_update: PostUpdate, db: db_dependency):
    post = db.query(models.Post).filter(models.Post.id == post_id).first()  # 데이터베이스에서 포스트를 조회함
    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="포스트를 찾을 수 없음")  # 포스트 미발견 시 예외 발생
    
    # 제공된 필드가 있으면 업데이트함
    if post_update.title is not None:
        post.title = post_update.title
    if post_update.content is not None:
        post.content = post_update.content
    
    db.commit()  # 트랜잭션을 커밋함
    db.refresh(post)  # 업데이트된 상태를 가져옴
    return post

# ID로 사용자를 업데이트하는 엔드포인트
@app.put("/users/{user_id}", status_code=status.HTTP_200_OK)
async def update_user(user_id: int, user_update: UserUpdate, db: db_dependency):
    user = db.query(models.User).filter(models.User.id == user_id).first()  # 데이터베이스에서 사용자를 조회함
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="사용자를 찾을 수 없음")  # 사용자 미발견 시 예외 발생
    
    # 제공된 필드가 있으면 업데이트함
    if user_update.username is not None:
        user.username = user_update.username
    
    db.commit()  # 트랜잭션을 커밋함
    db.refresh(user)  # 업데이트된 상태를 가져옴
    return user

# ID로 포스트를 삭제하는 엔드포인트
@app.delete("/posts/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(post_id: int, db: db_dependency):
    post = db.query(models.Post).filter(models.Post.id == post_id).first()  # 데이터베이스에서 포스트를 조회함
    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="포스트를 찾을 수 없음")  # 포스트 미발견 시 예외 발생
    
    db.delete(post)  # 세션에서 포스트를 삭제함
    db.commit()  # 트랜잭션을 커밋함
    return {"detail": "포스트 삭제됨"}

# ID로 사용자를 삭제하는 엔드포인트
@app.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: int, db: db_dependency):
    user = db.query(models.User).filter(models.User.id == user_id).first()  # 데이터베이스에서 사용자를 조회함
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="사용자를 찾을 수 없음")  # 사용자 미발견 시 예외 발생
    
    db.delete(user)  # 세션에서 사용자를 삭제함
    db.commit()  # 트랜잭션을 커밋함
    return {"detail": "사용자 삭제됨"}
