from sqlalchemy import Integer
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, declared_attr


class BaseModel(DeclarativeBase):
    """Base class for all SQLAlchemy models"""
    __abstract__ = True

    @declared_attr.directive
    def __tablename__(cls) -> str:
        if cls.__name__.endswith('y'):
            return cls.__name__[:-1].lower() + "ies"
        if cls.__name__.endswith('s'):
            return cls.__name__.lower()
        return cls.__name__.lower() + "s"


class IdMixinBase(BaseModel):
    """
    Base class for SQLAlchemy models which provides a single 'id' integer primary key
    """
    __abstract__ = True
    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, index=True, autoincrement=True)
