import logging

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select, text
from sqlalchemy.orm import Session

from .config import get_settings
from .db import get_db
from .models import Note, User
from .schemas import Credentials, NoteIn, NoteOut, Token, UserOut
from .security import create_token, current_user, hash_password, verify_password

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("coco-notes")

app = FastAPI(title="Coco Notes API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=get_settings().cors_origin_list,
    allow_credentials=False,
    allow_methods=["GET", "POST", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)


@app.get("/health", tags=["ops"])
def health(db: Session = Depends(get_db)) -> dict:
    db.execute(text("SELECT 1"))
    return {"status": "ok", "database": "ok"}


@app.post("/auth/register", response_model=Token, status_code=status.HTTP_201_CREATED, tags=["auth"])
def register(body: Credentials, db: Session = Depends(get_db)) -> Token:
    email = body.email.lower()
    if db.scalar(select(User).where(User.email == email)):
        raise HTTPException(status.HTTP_409_CONFLICT, "Email déjà utilisé")
    user = User(email=email, password_hash=hash_password(body.password))
    db.add(user)
    db.commit()
    log.info("Nouvel utilisateur id=%s", user.id)
    return Token(access_token=create_token(user.id))


@app.post("/auth/login", response_model=Token, tags=["auth"])
def login(body: Credentials, db: Session = Depends(get_db)) -> Token:
    user = db.scalar(select(User).where(User.email == body.email.lower()))
    if user is None or not verify_password(body.password, user.password_hash):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Identifiants invalides")
    return Token(access_token=create_token(user.id))


@app.get("/me", response_model=UserOut, tags=["auth"])
def me(user: User = Depends(current_user)) -> User:
    return user


@app.get("/notes", response_model=list[NoteOut], tags=["notes"])
def list_notes(user: User = Depends(current_user), db: Session = Depends(get_db)) -> list[Note]:
    return list(db.scalars(select(Note).where(Note.owner_id == user.id).order_by(Note.id.desc())))


@app.post("/notes", response_model=NoteOut, status_code=status.HTTP_201_CREATED, tags=["notes"])
def create_note(body: NoteIn, user: User = Depends(current_user), db: Session = Depends(get_db)) -> Note:
    note = Note(title=body.title, content=body.content, owner_id=user.id)
    db.add(note)
    db.commit()
    db.refresh(note)
    return note


@app.delete("/notes/{note_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["notes"])
def delete_note(note_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)) -> None:
    note = db.get(Note, note_id)
    if note is None or note.owner_id != user.id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Note introuvable")
    db.delete(note)
    db.commit()
