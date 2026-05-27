# curl 예시

이 문서는 MINGW64 bash 기준입니다. PowerShell에서는 줄바꿈 문자가 `\`가 아니라 백틱입니다.

## 회원가입

```bash
curl -X POST http://127.0.0.1:8000/user \
  -H "Content-Type: application/json" \
  -d '{"name":"홍길동","email":"goodsosbva8549+til1@gmail.com","password":"password123"}'
```

## 로그인

```bash
curl -X POST http://127.0.0.1:8000/user/login \
  -H "Content-Type: application/json" \
  -d '{"email":"goodsosbva8549+til1@gmail.com","password":"password123"}'
```

응답에서 `access_token`을 복사합니다.

## TIL 작성

```bash
curl -X POST http://127.0.0.1:8000/notes \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ACCESS_TOKEN" \
  -d '{"title":"FastAPI 학습","content":"오늘은 Celery와 로깅을 붙였다.","memo_date":"20260519","tags":["fastapi","celery","logging"]}'
```

## TIL 목록 조회

```bash
curl -X GET "http://127.0.0.1:8000/notes?page=1&items_per_page=10" \
  -H "Authorization: Bearer ACCESS_TOKEN"
```

## 태그로 조회

```bash
curl -X GET "http://127.0.0.1:8000/notes/tags/fastapi/notes?page=1&items_per_page=10" \
  -H "Authorization: Bearer ACCESS_TOKEN"
```

## TIL 수정

```bash
curl -X PUT http://127.0.0.1:8000/notes/NOTE_ID \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ACCESS_TOKEN" \
  -d '{"title":"FastAPI 복습","content":"JWT, Celery, Logging 흐름을 복습했다.","tags":["fastapi","review"]}'
```

## TIL 삭제

```bash
curl -X DELETE http://127.0.0.1:8000/notes/NOTE_ID \
  -H "Authorization: Bearer ACCESS_TOKEN"
```