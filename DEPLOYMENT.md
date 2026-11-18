# Public deployment on Render

## Free demo

In Render, create a Blueprint from the Campus SkillSwap repository. Set **Branch** to `main` and **Blueprint Path** to `render-free.yaml`. Check that the preview shows a Free web service, then click **Deploy Blueprint**. Share the HTTPS URL from the service page.

The free service uses temporary SQLite storage. Accounts, posts, sessions, and reviews are reset on restarts, redeploys, and spin-downs. Startup recreates the sample listings.

## Deployment with a persistent disk

The `render.yaml` Blueprint uses a paid web service and persistent disk. Review the charges in Render before deploying.

1. Put the contents of this folder in a dedicated Git repository. Do not upload the parent workspace, `.venv`, secrets, or your local database.
2. In Render, create a Blueprint from that repository. The included `render.yaml` configures Python, Gunicorn, static files, HTTPS settings and SQLite on a persistent disk.
3. Review the service and disk costs before applying the Blueprint.
4. Once deployment succeeds, use the HTTPS URL returned by Render. Test registration, posting, search, session completion and reviews there.
5. In the Render service shell run `python manage.py createsuperuser` for an administrator account. Do not put an admin password in the repository.

The first deployment starts a new database and adds the 12 sample skills with their named inactive accounts. Your local accounts, reviews and posts are not uploaded. Subsequent starts retain the database and do not duplicate sample posts. Sample posts remain labeled in their descriptions.

Only run one service instance with this SQLite setup. Plan regular SQLite-consistent backups and test restoration; persistent storage alone is not a backup. Use managed PostgreSQL if the service later needs multiple instances.

Production reads `DJANGO_SECRET_KEY`, `DJANGO_DEBUG=0`, `RENDER_EXTERNAL_HOSTNAME` and `SQLITE_PATH`. For a custom domain, add it to `DJANGO_ALLOWED_HOSTS`. The proxy header setting assumes Render terminates HTTPS and sets the forwarded protocol header.

Verify production configuration after installing `requirements-production.txt`:

```powershell
$env:DJANGO_DEBUG = '0'
$env:DJANGO_SECRET_KEY = 'use-a-long-random-secret-here-at-least-50-characters'
..\.venv\Scripts\python.exe manage.py check --deploy
Remove-Item Env:DJANGO_DEBUG
Remove-Item Env:DJANGO_SECRET_KEY
```

Gunicorn runs on the Linux hosting server, not Windows. Local development still uses `manage.py runserver`. Bootstrap currently requires its CDN connection.
