FROM python:3.11-slim

# 파이썬 캐시 생성 방지 및 버퍼링 없는 로그 출력
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

# 의존성 파일 먼저 복사 후 설치 (빌드 속도 최적화)
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# 나머지 소스 코드 복사
COPY . /app/