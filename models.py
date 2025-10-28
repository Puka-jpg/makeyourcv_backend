from sqlalchemy import Integer, String
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(AsyncAttrs, DeclarativeBase):
    """Base class for all models."""

    pass


class Skills(Base):
    """Skills Model = Stores users skills with description"""

    __tablename__ = "skills"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    skill_name: Mapped[str] = mapped_column(String, nullable=False)
    skill_description: Mapped[str] = mapped_column(String, nullable=False)

    def __repr__(self):
        return f"Skills: {self.skill_name}"
