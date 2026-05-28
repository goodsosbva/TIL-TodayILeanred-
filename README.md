# TIL FastAPI App

FastAPI로 만든 TIL(Today I Learned) 기록 API 서버입니다.

회원가입, 로그인, JWT 인증, TIL 노트 CRUD, 태그 조회, 요청 로깅, DB 마이그레이션, Celery 기반 환영 메일 발송까지 한 흐름으로 구현했습니다. 단순히 코드만 둔 프로젝트가 아니라, 기능별 구현 흐름을 Markdown 문서로 같이 정리해서 나중에 다시 봐도 구조를 따라갈 수 있게 했습니다.

## 주요 기능

- 사용자 회원가입, 조회, 수정, 삭제
- 비밀번호 암호화 저장
- JWT 기반 로그인 및 인증 처리
- 로그인한 사용자 기준 TIL 노트 작성, 조회, 수정, 삭제
- 태그 기반 TIL 노트 조회
- 회원가입 후 환영 메일 비동기 발송
- Celery + Redis 작업 큐 구성
- 요청 단위 로깅 미들웨어
- SQLAlchemy 기반 DB 모델 관리
- Alembic 마이그레이션 관리
- 기능별 구현 흐름 문서화

## 기술 스택

- Python 3.13
- FastAPI
- SQLAlchemy
- Alembic
- MySQL
- Celery
- Redis
- JWT
- Passlib / bcrypt
- Poetry

## 프로젝트 구조

```text
.
├── TIL_app/
│   ├── common/              # 인증, 로깅, Celery 메시징
│   ├── note/                # TIL 노트 도메인, 서비스, 저장소, 컨트롤러
│   ├── user/                # 사용자 도메인, 서비스, 저장소, 컨트롤러
│   ├── utils/               # 암호화, DB 유틸
│   ├── migrations/          # Alembic 마이그레이션
│   ├── 설명/                # 기능별 설명 문서
│   ├── main.py              # FastAPI 앱 진입점
│   ├── config.py            # 환경변수 설정
│   ├── database.py          # DB 연결 설정
│   ├── middlewares.py       # 요청 로깅 미들웨어
│   └── pyproject.toml       # 의존성 설정
├── fastapi-ca/              # FastAPI 학습용 예제 코드
└── README.md
```

## 실행 준비

필요한 환경은 아래와 같습니다.

- Python 3.13 이상
- MySQL
- Redis
- Gmail 앱 비밀번호
- Poetry

`TIL_app` 디렉터리 안에서 실행합니다.

```bash
cd TIL_app
poetry install
```

## 환경변수

`TIL_app/.env` 파일을 만들고 아래 값을 채웁니다.

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

`EMAIL_PASSWORD`는 Gmail 계정 비밀번호가 아니라 앱 비밀번호를 사용합니다.

## 실행 방법

Redis를 먼저 실행합니다.

```bash
docker run -d --name til-redis -p 6379:6379 redis:7-alpine
```

DB 마이그레이션을 적용합니다.

```bash
poetry run alembic upgrade head
```

Celery worker를 실행합니다. Windows 환경에서는 `--pool=solo` 옵션을 사용합니다.

```bash
poetry run celery -A common.messaging.celery worker --loglevel=info --pool=solo
```

FastAPI 서버를 실행합니다.

```bash
poetry run uvicorn main:app --reload
```

서버가 실행되면 아래 주소에서 API 문서를 볼 수 있습니다.

```text
http://127.0.0.1:8000/docs
```

## API 예시

회원가입:

```bash
curl -X POST http://127.0.0.1:8000/user \
  -H "Content-Type: application/json" \
  -d '{"name":"홍길동","email":"user@example.com","password":"password123","memo":"첫 가입"}'
```

로그인:

```bash
curl -X POST http://127.0.0.1:8000/user/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"password123"}'
```

TIL 작성:

```bash
curl -X POST http://127.0.0.1:8000/notes \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ACCESS_TOKEN" \
  -d '{"title":"FastAPI 학습","content":"오늘은 DI와 Celery를 연결했다.","memo_date":"20260519","tags":["fastapi","celery"]}'
```

## 문서 정리

구현하면서 기능별 흐름을 `TIL_app/설명` 아래에 정리했습니다.

- [전체 흐름](TIL_app/설명/00_전체_흐름.md)
- [환경설정](TIL_app/설명/01_환경설정.md)
- [회원가입과 Celery 메일 발송](TIL_app/설명/02_회원가입_메일_Celery.md)
- [로그인과 JWT](TIL_app/설명/03_로그인_JWT.md)
- [TIL 앱 기능](TIL_app/설명/04_TIL_앱_기능.md)
- [로깅](TIL_app/설명/05_로깅.md)
- [DB 마이그레이션](TIL_app/설명/06_DB_마이그레이션.md)
- [curl 예시](TIL_app/설명/07_curl_예시.md)
- [코드 흐름 중심 설명](TIL_app/설명/08_코드_흐름_중심_설명.md)
- [구현 흐름 정리](TIL_app/설명/09_구현_흐름.md)
- [구현 흐름 상세 문서](TIL_app/설명/구현흐름/README.md)

## 구현 흐름 요약

전체 흐름은 다음 순서로 이어집니다.

1. `.env`에서 DB, JWT, 메일, Redis 설정을 읽습니다.
2. FastAPI 앱이 시작되면서 사용자/노트 라우터와 로깅 미들웨어를 등록합니다.
3. 회원가입 요청이 들어오면 이메일 중복을 확인하고 비밀번호를 암호화합니다.
4. 사용자 정보를 DB에 저장한 뒤 Celery task로 환영 메일 발송을 넘깁니다.
5. 로그인 요청이 들어오면 비밀번호를 검증하고 JWT access token을 발급합니다.
6. TIL 노트 API는 JWT에서 사용자 정보를 확인한 뒤 해당 사용자 기준으로 동작합니다.
7. 노트와 태그는 SQLAlchemy 모델과 Repository 계층을 통해 저장됩니다.
8. DB 변경사항은 Alembic migration 파일로 관리합니다.

## 현재 상태

현재는 학습과 기능 구현을 중심으로 정리한 단계입니다.

- 기본 API 기능 구현 완료
- 주요 구현 흐름 문서화 완료
- 파이썬 문법 검사 완료
- 자동화 테스트 코드는 아직 추가 전

확인한 명령:

```bash
python -m compileall -q -x ".*[\\/](\\.venv|__pycache__)[\\/].*" TIL_app fastapi-ca
```
