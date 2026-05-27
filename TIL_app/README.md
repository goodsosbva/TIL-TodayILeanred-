# TIL App

FastAPI로 만든 TIL(Today I Learned) 기록 API 서버입니다. 사용자는 회원가입과 로그인을 할 수 있고, 로그인 후 자기 TIL 노트를 작성, 조회, 수정, 삭제할 수 있습니다. 회원가입 환영 메일은 Celery와 Redis를 통해 비동기로 발송하고, 모든 요청은 미들웨어에서 유저 정보와 함께 로깅합니다.

## 주요 기능

- 사용자 회원가입, 목록 조회, 수정, 삭제
- JWT 기반 로그인
- TIL 노트 CRUD
- 태그 기반 TIL 조회
- Gmail SMTP 환영 메일 발송
- Celery + Redis 비동기 작업 큐
- 요청 로깅 미들웨어
- `.env` 기반 환경변수 설정
- Alembic DB 마이그레이션

## 프로젝트 구조

```text
TIL_app/
├── common/              # 인증, Celery 메시징, 로거
├── note/                # TIL 노트 도메인, 서비스, 저장소, 컨트롤러
├── user/                # 사용자 도메인, 서비스, 저장소, 컨트롤러, 메일 태스크
├── utils/               # 암호화, DB 유틸
├── migrations/          # Alembic 마이그레이션
├── 설명/                # 기능 단위 설명 문서
├── config.py            # .env 로딩 및 설정 객체
├── database.py          # SQLAlchemy 엔진/session 설정
├── main.py              # FastAPI 앱 엔트리포인트
├── middlewares.py       # 요청 로깅 미들웨어
└── pyproject.toml       # 의존성 설정
```

## 실행 전 준비

필요한 것:

- Python 3.13 이상
- MySQL
- Docker 또는 로컬 Redis
- Gmail 앱 비밀번호
- Poetry 또는 기존 `.venv`

## .env 예시

프로젝트 루트에 `.env` 파일을 둡니다. 실제 비밀번호와 토큰은 직접 넣어야 합니다.

```env
DATABASE_USERNAME=root
DATABASE_PASSWORD=your_db_password
DATABASE_HOST=127.0.0.1
DATABASE_PORT=3306
DATABASE_NAME=fastapi-ca
JWT_SECRET=your_long_random_secret
APP_HOST=127.0.0.1
APP_PORT=8000
EMAIL_SENDER=your_email@gmail.com
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=465
EMAIL_PASSWORD=your_gmail_app_password
CELERY_BROKER_URL=redis://127.0.0.1:6379/0
CELERY_BACKEND_URL=redis://127.0.0.1:6379/1
```

`EMAIL_PASSWORD`는 Gmail 일반 비밀번호가 아니라 앱 비밀번호입니다. 코드에서는 공백을 제거해서 사용합니다.

## 설치

Poetry를 쓰는 경우:

```bash
poetry install
```

이미 `.venv`를 쓰는 경우:

```bash
.venv/Scripts/python.exe -m pip install -r requirements.txt
```

현재 프로젝트는 `pyproject.toml`과 `poetry.lock` 기준으로 관리합니다.

## DB 마이그레이션

```bash
.venv/Scripts/alembic.exe upgrade head
```

생성되는 주요 테이블:

- `user`
- `note`
- `tag`
- `note_tag`

## Redis 실행

Docker 사용 시:

```bash
docker start til-redis
```

컨테이너가 없다면:

```bash
docker run -d --name til-redis -p 6379:6379 redis:7-alpine
```

## Celery worker 실행

Windows에서는 `--pool=solo`를 사용합니다.

```bash
.venv/Scripts/celery.exe -A common.messaging.celery worker --loglevel=info --pool=solo
```

## FastAPI 서버 실행

```bash
.venv/Scripts/uvicorn.exe main:app --reload
```

또는:

```bash
.venv/Scripts/python.exe main.py
```

## 기본 API 예시

회원가입:

```bash
curl -X POST http://127.0.0.1:8000/user \
  -H "Content-Type: application/json" \
  -d '{"name":"홍길동","email":"goodsosbva8549+til1@gmail.com","password":"password123"}'
```

로그인:

```bash
curl -X POST http://127.0.0.1:8000/user/login \
  -H "Content-Type: application/json" \
  -d '{"email":"goodsosbva8549+til1@gmail.com","password":"password123"}'
```

TIL 작성:

```bash
curl -X POST http://127.0.0.1:8000/notes \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ACCESS_TOKEN" \
  -d '{"title":"FastAPI 학습","content":"오늘은 DI와 Celery를 연결했다.","memo_date":"20260519","tags":["fastapi","celery"]}'
```

## 기능별 설명

자세한 구현 흐름은 `설명/` 디렉터리를 봅니다.

- `설명/00_전체_흐름.md`
- `설명/01_환경설정.md`
- `설명/02_회원가입_메일_Celery.md`
- `설명/03_로그인_JWT.md`
- `설명/04_TIL_앱_기능.md`
- `설명/05_로깅.md`
- `설명/06_DB_마이그레이션.md`
- `설명/07_curl_예시.md`
- `설명/08_코드_흐름_중심_설명.md`
- `설명/09_구현_흐름.md`
- `설명/구현흐름/README.md`