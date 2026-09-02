import os

os.environ.setdefault("DATABASE_URL", "")
from eventsphere_common.db import Base, get_db_dependency, make_engine, make_session_factory  # noqa: E402

from .config import settings  # noqa: E402

os.environ["DATABASE_URL"] = settings.database_url

engine = make_engine()
SessionLocal = make_session_factory(engine)
get_db = get_db_dependency(SessionLocal)
