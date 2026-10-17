from sqlalchemy import JSON, MetaData
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase

from echovault.config import get_settings

# Schema-isolated metadata for multi-tenant database sharing
settings = get_settings()
metadata = MetaData(schema=settings.db_schema)


class Base(DeclarativeBase):
    metadata = metadata


# JSON variant: native JSONB on PostgreSQL, standard JSON elsewhere (e.g. SQLite tests)
JSONType = JSON().with_variant(JSONB(), "postgresql")
