"""Données initiales : à lancer une seule fois.

    scalingo --app <app-api> run python -m app.seed
"""
import os

from sqlalchemy import select

from .db import SessionLocal
from .models import Note, User
from .security import hash_password


def main() -> None:
    email = os.environ.get("SEED_EMAIL", "demo@coco-notes.fr")
    password = os.environ.get("SEED_PASSWORD", "demo1234")
    with SessionLocal() as db:
        if db.scalar(select(User).where(User.email == email)):
            print(f"Seed déjà présent ({email})")
            return
        user = User(email=email, password_hash=hash_password(password))
        user.notes = [
            Note(title="Bienvenue", content="Première note créée par le seed."),
            Note(title="Déployé sur Scalingo", content="Client React + API FastAPI + PostgreSQL."),
        ]
        db.add(user)
        db.commit()
        print(f"Utilisateur de démo créé : {email}")


if __name__ == "__main__":
    main()
