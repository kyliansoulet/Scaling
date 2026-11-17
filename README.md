# Coco Notes

Application de notes : client React + TypeScript, API FastAPI et base PostgreSQL, déployée sur Scalingo.

- Site : https://coco-notes-client-ks.osc-fr1.scalingo.io
- API : https://coco-notes-api-ks.osc-fr1.scalingo.io (`/health`, `/docs`)

## Architecture

Deux apps Scalingo dans un monorepo : `client/` (Node.js, build Vite servi par `serve`) et `api/` (Python, uvicorn). Seule l'API parle à la base PostgreSQL Starter 512. Chaque app pointe vers son dossier avec `PROJECT_DIR`.

## Déploiement

Chaque push sur `main` lance la CI GitHub Actions (tests API et build client). Si elle est verte, Scalingo redéploie automatiquement. Les migrations Alembic sont jouées après chaque déploiement (`postdeploy` du Procfile).

## Variables d'environnement

- API : `PROJECT_DIR`, `JWT_SECRET`, `JWT_EXPIRE_MINUTES`, `CORS_ORIGINS`, `SCALINGO_POSTGRESQL_URL` (ajoutée par l'addon)
- Client : `PROJECT_DIR`, `VITE_API_URL` (figée au build)

## Lancer en local

`docker compose up -d`, puis copier les `.env.example` en `.env`. Ensuite, côté API : `pip install -r requirements-dev.txt`, `alembic upgrade head`, `uvicorn app.main:app --reload`. Côté client : `npm install`, `npm run dev`.

## Coût

Estimé : 3 × 7,20 € = 21,60 €/mois (2 conteneurs S + PostgreSQL Starter 512), couvert par le voucher Ynov (50 €/mois). Réel : à relever dans Billing.

## En cas de panne

- Logs : `scalingo --app coco-notes-api-ks logs --lines 200`
- Rollback : `git revert <commit>` puis push sur `main` (redéploiement automatique)
- Sauvegarde : backups automatiques dans l'addon PostgreSQL (onglet Backups), téléchargeables avec `scalingo --app coco-notes-api-ks backups-download`
- Restauration : `pg_restore` via `scalingo --app coco-notes-api-ks db-tunnel SCALINGO_POSTGRESQL_URL`
