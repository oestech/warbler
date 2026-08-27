import pytest

from app.db import DB_PATH
from app.seed import seed


@pytest.fixture(scope="session", autouse=True)
def seeded_db():
    if not DB_PATH.exists():
        seed()
