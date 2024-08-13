from sqlalchemy import ForeignKey, Boolean, Column, Integer, String #SQLAlchemy에서 열의 타입을 정의하는 클래스드를 불러온다.
from sqlalchemy.orm import relationship
from database import Base #모델 클래스를 정의할 때 사용하는 선언적 기본 클래스

class User(Base):
  __tablename__ = 'users' #데이터 베이스 데이터 이름을 지정함
  
  id = Column(Integer, primary_key=True, index=True)
  username = Column(String(50), unique=True)
  
  posts = relationship('Post', back_populates='user')  # 1:N 관계, 여러 포스트를 가짐
  profile = relationship('Profile', back_populates='user', uselist=False)  # 1:1 관계
  
  #uselist = True 면 1:N 관계
  #uselist = False 면 1:1 관계

class Profile(Base):
    __tablename__ = 'profiles'
    
    id = Column(Integer, primary_key=True, index=True)
    bio = Column(String(255))
    user_id = Column(Integer, ForeignKey('users.id'))
    
    user = relationship('User', back_populates='profile')  # 단일 프로필 객체

class Post(Base):
  __tablename__ = 'posts'
  
  id = Column(Integer, primary_key=True, index=True)
  title = Column(String(50))
  content = Column(String(100))
  user_id = Column(Integer)
  
  user = relationship('User', back_populates='posts')  # 여러 포스트가 하나의 유저와 관련됨
    # back_populates를 사용해 User 객체의 posts 속성으로 해당 사용자가 작성한 모든 Post 객체를 가져올 수 있다.

class Comment(Base):
    __tablename__ = 'comments'  # 유저의 코멘트가 담겨질 db
    
    id = Column(Integer, primary_key=True, index=True)  
    content = Column(String(255))  # (최대 255자)
    post_id = Column(Integer, ForeignKey('posts.id'))  # 'posts' 테이블의 'id' 열을 참조하는 외래 키
    user_id = Column(Integer, ForeignKey('users.id'))  # 'users' 테이블의 'id' 열을 참조하는 외래 키
    
    post = relationship('Post', back_populates='comments')  # Comment와 Post 간의 관계를 설정함
    user = relationship('User', back_populates='comments')  # Comment와 User 간의 관계를 설정함
    