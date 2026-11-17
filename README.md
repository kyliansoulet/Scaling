# Coco Notes — déploiement Scalingo

Application de prise de notes : client **React + TypeScript (Vite)**, API **FastAPI**, base **PostgreSQL**, déployée sur **Scalingo** en HTTPS.

- Client en ligne : `https://<app-client>.osc-fr1.scalingo.io`
- API en ligne : `https://<app-api>.osc-fr1.scalingo.io` (`/health`, `/docs`)

## Architecture

```
Navigateur ──pages──▶ App 1 « client » (Node.js, build Vite, serve -s dist sur $PORT)
     │
     └──fetch JSON──▶ App 2 « api » (Python, uvicorn sur $PORT, CORS limité au client, /health)
                              │ SQL
                              ▼
                      Addon PostgreSQL Starter 512 (SCALINGO_POSTGRESQL_URL)
```

Monorepo : `api/` et `client/`. Chaque app Scalingo pointe vers son dossier via `PROJECT_DIR`.
Aucune donnée sur le disque du conteneur (éphémère) : tout est dans PostgreSQL. Aucun secret dans Git.

## Lancer en local

```bash
docker compose up -d                      # PostgreSQL 16

cd api
python -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
cp .env.example .env
alembic upgrade head
python -m app.seed                        # demo@coco-notes.fr / demo1234
uvicorn app.main:app --reload             # http://localhost:8000/docs

cd ../client
cp .env.example .env
npm install
npm run dev                               # http://localhost:5173
```

Tests : `cd api && pytest` (PostgreSQL requis) — `cd client && npm test`.

## Variables d'environnement

| App | Variable | Rôle |
|---|---|---|
| api | `SCALINGO_POSTGRESQL_URL` | Injectée par l'addon ; `postgres://` est converti en `postgresql+psycopg://` |
| api | `DATABASE_URL` | Base en local uniquement |
| api | `JWT_SECRET` | Clé de signature des jetons (longue valeur aléatoire) |
| api | `JWT_EXPIRE_MINUTES` | Durée de validité d'un jeton |
| api | `CORS_ORIGINS` | Origines autorisées, séparées par des virgules (URL publique du client) |
| api | `PROJECT_DIR` | `api` |
| client | `VITE_API_URL` | URL publique de l'API, **figée au build** (tout changement impose un redéploiement) |
| client | `PROJECT_DIR` | `client` |

## Procédure de déploiement reproductible

```bash
# API + base
scalingo create <app-api> --region osc-fr1
scalingo --app <app-api> env-set PROJECT_DIR=api JWT_SECRET=$(openssl rand -hex 32) \
  JWT_EXPIRE_MINUTES=60 CORS_ORIGINS=https://<app-client>.osc-fr1.scalingo.io
scalingo --app <app-api> addons-add postgresql postgresql-starter-512
scalingo --app <app-api> scale web:1:S

# Client
scalingo create <app-client> --region osc-fr1
scalingo --app <app-client> env-set PROJECT_DIR=client VITE_API_URL=https://<app-api>.osc-fr1.scalingo.io
scalingo --app <app-client> scale web:1:S

# Lier les deux apps au dépôt GitHub (branche main, déploiement auto après CI verte)
scalingo --app <app-api> integration-link-create https://github.com/<user>/<repo> --branch main --auto-deploy
scalingo --app <app-client> integration-link-create https://github.com/<user>/<repo> --branch main --auto-deploy

# Données initiales (une seule fois)
scalingo --app <app-api> run python -m app.seed
```

`api/Procfile` :

```
web: uvicorn app.main:app --host 0.0.0.0 --port $PORT ...
postdeploy: alembic upgrade head      # migrations jouées après chaque déploiement
```

Le client est construit par le buildpack Node.js (`npm run build`) puis servi par `npm start` (`serve -s dist`), ce qui renvoie `index.html` pour toute URL interne : rafraîchir `/about` ne renvoie pas 404.

## Intégration et déploiement continus

- `.github/workflows/api.yml` : ruff, migrations up/down, pytest sur un PostgreSQL de service — uniquement si `api/**` change.
- `.github/workflows/client.yml` : typecheck, vitest, build — uniquement si `client/**` change.
- Scalingo attend que les checks GitHub soient verts avant le déploiement automatique de `main` : une PR qui casse un test n'atteint pas la production.

## Coûts

| Ressource | Quantité | Estimation mensuelle |
|---|---|---|
| Conteneur S (api) | 1 | ~7,20 € |
| Conteneur S (client) | 1 | ~7,20 € |
| PostgreSQL Starter 512 | 1 | ~7,20 € |
| **Total estimé** | | **~21,60 € HT/mois** (sous le plafond de 50 €/mois du voucher) |

Estimation à vérifier avec le simulateur de prix Scalingo. Consommation réelle : _à relever dans Billing après une semaine_.

## En cas de panne

```bash
# Logs
scalingo --app <app-api> logs --lines 200
scalingo --app <app-api> addons                         # récupérer l'ID de l'addon
scalingo --app <app-api> logs --addon <addon-id> --lines 200

# Diagnostic
curl -i https://<app-api>.osc-fr1.scalingo.io/health  # 500 si la base est injoignable
scalingo --app <app-api> ps
scalingo --app <app-api> deployments

# Rollback : redéployer un commit/déploiement précédent
scalingo --app <app-api> deploy <url-archive-du-commit-precedent>
#   ou dans le dashboard : Deployments > choisir un déploiement > Redeploy

# Sauvegarde / restauration PostgreSQL
scalingo --app <app-api> backups                        # sauvegardes automatiques quotidiennes
scalingo --app <app-api> backups-download --backup <id>
scalingo --app <app-api> db-tunnel SCALINGO_POSTGRESQL_URL   # tunnel local sur 127.0.0.1:10000
pg_restore --clean --if-exists --no-owner --no-privileges -d "postgresql://<user>:<pwd>@127.0.0.1:10000/<db>" backup.pgsql

# Redémarrer / mettre en pause
scalingo --app <app-api> restart
scalingo --app <app-api> scale web:0                    # arrêt (fin de module)
```

Erreur provoquée pour l'exercice : `JWT_SECRET` modifié → tous les jetons existants deviennent invalides (401), visible dans les logs ; ou base volontairement inaccessible → `/health` renvoie 500.
