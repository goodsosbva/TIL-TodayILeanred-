# TIL CRUD 구현 흐름

## 왜 구현했는가

프로젝트 이름이 TIL App이므로 핵심 기능은 사용자가 오늘 배운 내용을 기록하는 것입니다. 유저와 로그인 기능이 준비된 뒤, 로그인한 사용자 기준으로 TIL 노트를 CRUD할 수 있게 구현했습니다.

## 구현한 파일 순서

```text
note/domain/note.py
-> note/domain/repository/note_repo.py
-> note/infra/db_models/note.py
-> note/infra/repository/note_repo.py
-> note/application/note_service.py
-> note/interface/controllers/note_controller.py
-> containers.py에 note_repo/note_service 등록
-> main.py에 note router 등록
```

## 구현 흐름 그림

```mermaid
flowchart TD
    A[Note/Tag 도메인 생성] --> B[INoteRepository 생성]
    B --> C[Note/Tag/note_tag DB 모델 생성]
    C --> D[NoteRepository 구현]
    D --> E[NoteService 구현]
    E --> F[note_controller API 구현]
    F --> G[Container와 main.py에 연결]
```

## 작성 구현 흐름

```mermaid
sequenceDiagram
    participant Client
    participant Auth
    participant Controller
    participant Service
    participant Repo
    participant DB

    Client->>Auth: Authorization token
    Auth-->>Controller: CurrentUser
    Client->>Controller: POST /notes
    Controller->>Service: create_note(user_id, body)
    Service->>Service: ULID 생성
    Service->>Service: Tag 객체 생성
    Service->>Repo: save(user_id,note)
    Repo->>DB: tag 조회/생성
    Repo->>DB: note 저장
    Repo->>DB: note_tag 연결
    Controller-->>Client: NoteResponse
```

## 조회 구현 흐름

```mermaid
flowchart TD
    A[GET /notes] --> B[get_current_user]
    B --> C[NoteService.get_notes]
    C --> D[NoteRepository.get_notes]
    D --> E[user_id 조건]
    E --> F[tags joinedload]
    F --> G[pagination]
    G --> H[response]
```

## 수정 구현 흐름

```mermaid
flowchart TD
    A[PUT /notes/id] --> B[get_current_user]
    B --> C[기존 note 조회]
    C --> D[입력된 필드만 변경]
    D --> E[tag_names 있으면 태그 재구성]
    E --> F[NoteRepository.update]
    F --> G[note와 note_tag 갱신]
```

## 삭제 구현 흐름

```mermaid
flowchart TD
    A[DELETE /notes/id] --> B[get_current_user]
    B --> C[NoteRepository.delete]
    C --> D[user_id + id 조건 조회]
    D --> E[note 삭제]
    E --> F[안 쓰는 tag 삭제]
    F --> G[204 응답]
```

## 핵심 구현 이유

### 1. 모든 Repository 쿼리에 user_id를 넣은 이유

```python
.filter(NoteModel.user_id == user_id, NoteModel.id == id)
```

노트 ID를 알아도 남의 노트를 조회, 수정, 삭제하지 못하게 하기 위해서입니다.

### 2. tag를 별도 테이블로 만든 이유

한 노트에 여러 태그가 붙고, 같은 태그가 여러 노트에 붙을 수 있습니다. 그래서 `note`, `tag`, `note_tag` 세 테이블로 나눴습니다.

```mermaid
erDiagram
    note ||--o{ note_tag : has
    tag ||--o{ note_tag : has
```

### 3. Service에서 도메인 객체를 만드는 이유

```python
note = Note(
    id=self.ulid.generate(),
    user_id=user_id,
    title=title,
    content=content,
    memo_date=memo_date,
    tags=tags,
)
```

ID 생성과 생성 시간, 태그 객체 구성은 비즈니스 로직입니다. DB 저장소가 아니라 Service에서 처리합니다.

## 최종 API

```text
POST   /notes
GET    /notes
GET    /notes/{id}
PUT    /notes/{id}
DELETE /notes/{id}
GET    /notes/tags/{tag_name}/notes
```