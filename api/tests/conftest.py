import pytest
from fastapi.testclient import TestClient

from app import models  # noqa: F401
from app.db import Base, engine
from app.main import app


@pytest.fixture()
def client():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)  # uniquement pour les tests ; la prod utilise Alembic
    with TestClient(app) as c:
        yield c
    Base.metadata.drop_all(engine)
