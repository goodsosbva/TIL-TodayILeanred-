from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, String, Table, Text
from sqlalchemy.orm import relationship

from database import Base


note_tag_association = Table(
    "note_tag",
    Base.metadata,
    Column("note_id", String(36), ForeignKey("note.id"), primary_key=True),
    Column("tag_id", String(36), ForeignKey("tag.id"), primary_key=True),
)


class Note(Base):
    __tablename__ = "note"

    id = Column(String(36), primary_key=True)
    user_id = Column(String(36), nullable=False, index=True)
    title = Column(String(64), nullable=False)
    content = Column(Text, nullable=False)
    memo_date = Column(String(8), nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    tags = relationship(
        "Tag",
        secondary=note_tag_association,
        back_populates="notes",
        lazy="joined",
    )


class Tag(Base):
    __tablename__ = "tag"

    id = Column(String(36), primary_key=True)
    name = Column(String(64), nullable=False, unique=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    notes = relationship(
        "Note",
        secondary=note_tag_association,
        back_populates="tags",
        lazy="joined",
    )
