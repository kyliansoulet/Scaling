from app.config import Settings


def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_register_login_and_notes(client):
    creds = {"email": "alice@example.com", "password": "secret123"}
    assert client.post("/auth/register", json=creds).status_code == 201
    assert client.post("/auth/register", json=creds).status_code == 409

    token = client.post("/auth/login", json=creds).json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    assert client.get("/notes").status_code == 401
    r = client.post("/notes", json={"title": "Hello", "content": "world"}, headers=headers)
    assert r.status_code == 201
    note_id = r.json()["id"]
    assert [n["title"] for n in client.get("/notes", headers=headers).json()] == ["Hello"]
    assert client.delete(f"/notes/{note_id}", headers=headers).status_code == 204
    assert client.get("/notes", headers=headers).json() == []


def test_bad_login(client):
    r = client.post("/auth/login", json={"email": "nobody@example.com", "password": "nopass1"})
    assert r.status_code == 401


def test_postgres_url_is_normalized():
    s = Settings(scalingo_postgresql_url="postgres://u:p@h:5432/db?sslmode=prefer", database_url="")
    assert s.sqlalchemy_url == "postgresql+psycopg://u:p@h:5432/db?sslmode=prefer"
