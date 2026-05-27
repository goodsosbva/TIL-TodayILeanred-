from dataclasses import asdict
from datetime import datetime
from typing import Annotated

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from common.auth import CurrentUser, get_current_user
from containers import Container
from note.application.note_service import NoteService


router = APIRouter(prefix="/notes")


class NoteResponse(BaseModel):
    id: str
    user_id: str
    title: str
    content: str
    memo_date: str
    tags: list[str]
    created_at: datetime
    updated_at: datetime


class CreateNoteBody(BaseModel):
    title: str = Field(min_length=1, max_length=64)
    content: str = Field(min_length=1)
    memo_date: str = Field(min_length=8, max_length=8)
    tags: list[str] | None = Field(default=None, min_length=1, max_length=32)


@router.post("", status_code=201, response_model=NoteResponse)
@inject
def create_note(
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    body: CreateNoteBody,
    note_service: NoteService = Depends(Provide[Container.note_service]),
):
    note = note_service.create_note(
        user_id=current_user.id,
        title=body.title,
        content=body.content,
        memo_date=body.memo_date,
        tag_names=body.tags,
    )

    return _to_response(note)


class GetNotesResponse(BaseModel):
    total_count: int
    page: int
    notes: list[NoteResponse]


@router.get("", response_model=GetNotesResponse)
@inject
def get_notes(
    page: int = 1,
    items_per_page: int = 10,
    current_user: CurrentUser = Depends(get_current_user),
    note_service: NoteService = Depends(Provide[Container.note_service]),
):
    total_count, notes = note_service.get_notes(
        user_id=current_user.id,
        page=page,
        items_per_page=items_per_page,
    )

    return {
        "total_count": total_count,
        "page": page,
        "notes": [_to_response(note) for note in notes],
    }


@router.get("/tags/{tag_name}/notes", response_model=GetNotesResponse)
@inject
def get_notes_by_tag(
    tag_name: str,
    page: int = 1,
    items_per_page: int = 10,
    current_user: CurrentUser = Depends(get_current_user),
    note_service: NoteService = Depends(Provide[Container.note_service]),
):
    total_count, notes = note_service.get_notes_by_tag(
        user_id=current_user.id,
        tag_name=tag_name,
        page=page,
        items_per_page=items_per_page,
    )

    return {
        "total_count": total_count,
        "page": page,
        "notes": [_to_response(note) for note in notes],
    }


@router.get("/{id}", response_model=NoteResponse)
@inject
def get_note(
    id: str,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    note_service: NoteService = Depends(Provide[Container.note_service]),
):
    note = note_service.get_note(
        user_id=current_user.id,
        id=id,
    )

    return _to_response(note)


class UpdateNoteBody(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=64)
    content: str | None = Field(default=None, min_length=1)
    memo_date: str | None = Field(default=None, min_length=8, max_length=8)
    tags: list[str] | None = Field(default=None)


@router.put("/{id}", response_model=NoteResponse)
@inject
def update_note(
    id: str,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    body: UpdateNoteBody,
    note_service: NoteService = Depends(Provide[Container.note_service]),
):
    note = note_service.update_note(
        user_id=current_user.id,
        id=id,
        title=body.title,
        content=body.content,
        memo_date=body.memo_date,
        tag_names=body.tags,
    )

    return _to_response(note)


@router.delete("/{id}", status_code=204)
@inject
def delete_note(
    id: str,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    note_service: NoteService = Depends(Provide[Container.note_service]),
):
    note_service.delete_note(
        user_id=current_user.id,
        id=id,
    )


def _to_response(note):
    response = asdict(note)
    response.update({"tags": [tag.name for tag in note.tags]})
    return response
