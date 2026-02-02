FROM python:3.11-slim

#앞으로 이 컨테이너에서 실행되는 모든 작업은 /app 디렉토리에서 한다
WORKDIR /app

# uv 설치
RUN pip install --no-cache-dir uv

# 의존성 복사 (캐시 최적화)
COPY pyproject.toml uv.lock ./
RUN uv sync --system --no-dev

# 실제 코드 복사
# 사실 상 . /app과 같음
COPY . .

# FastAPI 실행
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
