# 로그인과 JWT

이 문서는 로그인 API가 이메일/비밀번호를 검증하고 JWT access token을 만드는 코드 흐름을 설명합니다.

## 관련 파일

```text
user/interface/controllers/user_controller.py
user/application/user_service.py
user/infra/repository/user_repo.py
utils/crypto.py
common/auth.py
config.py
```

## 1. 로그인 전체 흐름 그림

```mermaid
sequenceDiagram
    participant Client
    participant Controller as user_controller
    participant Service as UserService
    participant Repo as UserRepository
    participant Crypto
    participant Auth as common/auth.py

    Client->>Controller: POST /user/login
    Controller->>Controller: JSON 또는 form에서 email/password 추출
    Controller->>Service: login(email,password)
    Service->>Repo: find_by_email(email)
    Repo-->>Service: User
    Service->>Crypto: verify(password, user.password)
    Crypto-->>Service: True or False
    Service->>Auth: create_access_token(user_id, role)
    Auth-->>Service: JWT
    Service-->>Controller: access_token
    Controller-->>Client: bearer token 응답
```

## 2. 실제 코드 호출 순서

```text
POST /user/login
-> user_controller.login()
-> request content-type 확인
-> email/password 추출
-> user_service.login()
-> user_repo.find_by_email()
-> crypto.verify()
-> create_access_token()
-> { access_token, token_type }
```

## 3. Controller가 하는 일

`user_controller.py`

```python
if "application/json" in content_type:
    body = await request.json()
    email = body.get("email") or body.get("username")
    password = body.get("password")
else:
    form = parse_qs((await request.body()).decode("utf-8"))
    email = form.get("email", form.get("username", [None]))[0]
    password = form.get("password", [None])[0]
```

원본 GitHub 코드는 `OAuth2PasswordRequestForm`을 사용합니다. 로컬에서는 `python-multipart` 미설치 상태에서도 앱이 죽지 않게 JSON과 form body를 직접 파싱하도록 했습니다.

## 4. Service가 하는 일

`user_service.py`

```python
user = self.user_repo.find_by_email(email)

if not self.crypto.verify(password, user.password):
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
```

DB에 저장된 비밀번호는 bcrypt hash입니다. 로그인 때는 입력한 평문 비밀번호를 hash와 비교합니다.

```python
access_token = create_access_token(
    payload={"user_id": user.id},
    role=Role.USER,
)
```

비밀번호가 맞으면 JWT를 발급합니다. payload에는 `user_id`가 들어가고 role은 `USER`로 들어갑니다.

## 5. JWT 생성 흐름

```mermaid
flowchart TD
    A[create_access_token] --> B[header 생성]
    B --> C[payload 생성: user_id role exp]
    C --> D[base64url encode]
    D --> E[JWT_SECRET으로 HMAC SHA256 서명]
    E --> F[header.payload.signature 반환]
```

## 6. 인증 API에서 JWT 검증 흐름

```mermaid
flowchart TD
    A[Authorization: Bearer token] --> B[get_current_user]
    B --> C[decode_access_token]
    C --> D[서명 검증]
    D --> E[exp 만료 확인]
    E --> F[user_id, role 확인]
    F --> G[CurrentUser 반환]
```

`common/auth.py`

```python
def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    payload = decode_access_token(token)

    user_id = payload.get("user_id")
    role = payload.get("role")
    if not user_id or role != Role.USER:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

    return CurrentUser(id=user_id, role=Role(role))
```

## 7. 실패 케이스

- body에 email/password가 없으면 `400`
- 이메일이 DB에 없으면 repository에서 `422`
- 비밀번호가 틀리면 `401`
- 토큰이 잘못되었거나 만료되면 `401`
- role이 USER가 아니면 `403`