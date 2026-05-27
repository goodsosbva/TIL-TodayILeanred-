from fastapi import HTTPException
from sqlalchemy.orm import Session, joinedload

from database import SessionLocal
from note.domain.note import Note as NoteVO
from note.domain.note import Tag as TagVO
from note.domain.repository.note_repo import INoteRepository
from note.infra.db_models.note import Note as NoteModel
from note.infra.db_models.note import Tag as TagModel


class NoteRepository(INoteRepository):
    def get_notes(
        self,
        user_id: str,
        page: int,
        items_per_page: int,
    ) -> tuple[int, list[NoteVO]]:
        with SessionLocal() as db:
            query = (
                db.query(NoteModel)
                .options(joinedload(NoteModel.tags))
                .filter(NoteModel.user_id == user_id)
                .order_by(NoteModel.memo_date.desc(), NoteModel.created_at.desc())
            )
            total_count = query.count()
            notes = query.offset((page - 1) * items_per_page).limit(items_per_page).all()

            return total_count, [self._to_note_vo(note) for note in notes]

    def get_notes_by_tag_name(
        self,
        user_id: str,
        tag_name: str,
        page: int,
        items_per_page: int,
    ) -> tuple[int, list[NoteVO]]:
        with SessionLocal() as db:
            query = (
                db.query(NoteModel)
                .options(joinedload(NoteModel.tags))
                .filter(
                    NoteModel.user_id == user_id,
                    NoteModel.tags.any(TagModel.name == tag_name),
                )
                .order_by(NoteModel.memo_date.desc(), NoteModel.created_at.desc())
            )
            total_count = query.count()
            notes = query.offset((page - 1) * items_per_page).limit(items_per_page).all()

            return total_count, [self._to_note_vo(note) for note in notes]

    def find_by_id(self, user_id: str, id: str) -> NoteVO:
        with SessionLocal() as db:
            note = (
                db.query(NoteModel)
                .options(joinedload(NoteModel.tags))
                .filter(NoteModel.user_id == user_id, NoteModel.id == id)
                .first()
            )

            if not note:
                raise HTTPException(status_code=422)

            return self._to_note_vo(note)

    def save(self, user_id: str, note: NoteVO):
        with SessionLocal() as db:
            new_note = NoteModel(
                id=note.id,
                user_id=user_id,
                title=note.title,
                content=note.content,
                memo_date=note.memo_date,
                tags=self._get_or_create_tag_models(db, note.tags),
                created_at=note.created_at,
                updated_at=note.updated_at,
            )

            db.add(new_note)
            db.commit()

    def update(self, user_id: str, note: NoteVO) -> NoteVO:
        with SessionLocal() as db:
            note_model = (
                db.query(NoteModel)
                .options(joinedload(NoteModel.tags))
                .filter(NoteModel.user_id == user_id, NoteModel.id == note.id)
                .first()
            )

            if not note_model:
                raise HTTPException(status_code=422)

            note_model.title = note.title
            note_model.content = note.content
            note_model.memo_date = note.memo_date
            note_model.updated_at = note.updated_at
            note_model.tags = self._get_or_create_tag_models(db, note.tags)

            db.add(note_model)
            db.flush()
            self._delete_unused_tags(db)
            db.commit()

            return self._to_note_vo(note_model)

    def delete(self, user_id: str, id: str):
        with SessionLocal() as db:
            note = (
                db.query(NoteModel)
                .options(joinedload(NoteModel.tags))
                .filter(NoteModel.user_id == user_id, NoteModel.id == id)
                .first()
            )

            if not note:
                raise HTTPException(status_code=422)

            db.delete(note)
            db.flush()
            self._delete_unused_tags(db)
            db.commit()

    def _get_or_create_tag_models(
        self,
        db: Session,
        tags: list[TagVO],
    ) -> list[TagModel]:
        tag_models: list[TagModel] = []

        for tag in tags:
            existing_tag = db.query(TagModel).filter(TagModel.name == tag.name).first()
            if existing_tag:
                tag_models.append(existing_tag)
                continue

            tag_models.append(
                TagModel(
                    id=tag.id,
                    name=tag.name,
                    created_at=tag.created_at,
                    updated_at=tag.updated_at,
                )
            )

        return tag_models

    def _delete_unused_tags(self, db: Session) -> None:
        unused_tags = db.query(TagModel).filter(~TagModel.notes.any()).all()
        for tag in unused_tags:
            db.delete(tag)

    def _to_note_vo(self, note: NoteModel) -> NoteVO:
        return NoteVO(
            id=note.id,
            user_id=note.user_id,
            title=note.title,
            content=note.content,
            memo_date=note.memo_date,
            tags=[self._to_tag_vo(tag) for tag in note.tags],
            created_at=note.created_at,
            updated_at=note.updated_at,
        )

    def _to_tag_vo(self, tag: TagModel) -> TagVO:
        return TagVO(
            id=tag.id,
            name=tag.name,
            created_at=tag.created_at,
            updated_at=tag.updated_at,
        )
