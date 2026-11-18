# Campus SkillSwap

A beginner-friendly Django and SQLite app. All application views are functions. Includes registration, login, POST logout, public browsing, title/category search, owner-only post management, a dashboard, session requests, and ratings with written reviews.

## 1. Run the project

Open PowerShell in this folder. Python 3.12–3.14 is recommended for Django 5.2. The workspace interpreter also passed the included checks on Python 3.15, outside that release's officially supported range.

```powershell
py -3.14 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe manage.py migrate
.\.venv\Scripts\python.exe manage.py createsuperuser
.\.venv\Scripts\python.exe manage.py runserver
```

Open http://127.0.0.1:8000/. Administration is at `/admin/`. No accounts or example posts are preloaded. If using the existing workspace environment instead, run `..\.venv\Scripts\python.exe manage.py runserver` from this folder.

## 2. Understand the project setup

`manage.py` runs Django commands. `config/settings.py` enables authentication, sessions, messages, templates, SQLite and CSRF protection. `config/urls.py` connects Django's login/logout pages, administration and the skills app. `skills/urls.py` maps each application URL to a function in `views.py`.

The templates in the supplied ZIP were Learning Log examples. This project has new SkillSwap templates; it does not depend on the old `MainApp`, `users`, or `bootstrap4` template package.

## 3. Store the data

`skills/models.py` defines three tables:

- `Skill`: title, category, description, owner and posting time. Category is simple free text.
- `Session`: a learner's request for a skill, with a completed flag. One request per learner per skill keeps this starter simple.
- `Review`: a 1–5 rating and written comment linked to a skill and author. Database constraints enforce the rating range and one review per learner per skill.

Foreign keys connect records. Deleting a skill also removes its sessions and reviews. The initial migration records this schema; `migrate` creates the tables. If you later change models, run `makemigrations` and then `migrate`.

## 4. Create accounts and skill posts

`register` uses Django's `UserCreationForm`, which checks matching passwords and configured password rules. Django handles password hashing. Login and logout use Django's built-in authentication views; every custom application view is function-based.

`SkillForm` exposes only title, category and description. The create view sets the owner from the logged-in user, rather than trusting a submitted owner ID. Edit and delete look up the skill with both its ID and `owner=request.user`, so other students cannot change it. Delete first displays a confirmation and only removes data on POST.

## 5. Search by title or category

The search form in `templates/skills/list.html` uses GET, so a search can be bookmarked, for example `/?q=music`. The input is named `q`.

The `skill_list` function reads and trims `request.GET.get('q', '')`. An empty query shows all skills. Otherwise it filters using:

```python
Q(title__icontains=query) | Q(category__icontains=query)
```

`icontains` means case-insensitive partial matching. `|` means either field may match. Django sends the values as query parameters rather than constructing SQL from user input. The template retains the search text, provides a Clear link, and shows an empty-state message when there are no matches. SQLite's built-in case-insensitive matching is primarily ASCII; broader language search would need additional work.

## 6. Understand the Bootstrap styling

`templates/base.html` provides the shared navigation, messages, footer and Bootstrap stylesheet. Other templates use `{% extends 'base.html' %}` and fill its content block, avoiding repeated page layouts.

The skill list uses Bootstrap's `row`, `col-md-6`, and `col-lg-4` classes for one, two or three columns according to screen size. Cards have category badges, concise descriptions and clear action buttons. A small shared style block supplies the navy, indigo and mint palette, rounded corners, readable form fields and keyboard focus outlines. The navigation wraps on small screens without requiring JavaScript.

Bootstrap loads from a CDN, so an internet connection is needed for its styling. The HTML remains functional without Bootstrap, but the layout is plainer. For offline use, download Bootstrap and serve it using Django static files.

## 7. Request and complete a session

1. A learner opens a skill and selects Request a session.
2. A POST view creates one session request; repeated submissions reuse it.
3. The provider sees the request on their dashboard. Students arrange the session outside this app; there is no messaging or scheduling service.
4. After teaching, the provider selects Mark session complete. The view checks that the logged-in user owns that session's skill.
5. The learner can now review the skill.

This is provider-attested completion. It does not independently verify an in-person meeting. Providers cannot request their own skills. Requesting and completing sessions require POST and CSRF tokens.

## 8. Rate and review a skill

The detail view checks eligibility on the server: the learner needs a completed session and cannot be the skill owner. Hiding the form alone would not protect the endpoint, so the same check runs for POST submissions.

`ReviewForm` validates a rating choice from 1 to 5 and a required comment of at most 1,500 characters. The view supplies the author and skill. If a review already exists, it is passed as the form's `instance`, so saving updates it instead of adding another. After a successful save, redirecting avoids accidental resubmission on refresh.

`Avg` calculates the average rating, and `Count` supplies the number of reviews on each browse card. Unrated skills show a friendly placeholder. Django escapes user content by default; comments are displayed with `linebreaks` rather than marked safe.

## 9. Try the complete workflow

Register a provider account, post a skill, then log out. Register a learner account, search for the skill and request a session. Log back in as the provider, open My dashboard and mark the session complete. Return as the learner, open the skill, and save a rating and comment. Update the review and check the browse card's average.

## 10. Run verification

```powershell
.\.venv\Scripts\python.exe manage.py check
.\.venv\Scripts\python.exe manage.py test
```

The tests cover search, rendered pages, post ownership, login requirements, POST-only actions, CSRF protection, session completion permissions, review eligibility, invalid ratings, review updates, averages, creation and deletion. They use a temporary database.

This is a local development starter. Before public deployment, set a private `DJANGO_SECRET_KEY`, disable debug, configure allowed hosts and HTTPS, serve static assets, and arrange backups. Account email verification, password-reset email delivery, messaging, pagination and moderation workflows are not configured. Django's included password-reset URLs need templates and email configuration before use; login, registration and logout are ready.

## Interface and meeting updates
Search now includes category filter buttons that work together with the search text. Registration, posting, and editing have specific button labels and field help. The mobile menu collapses using the Bootstrap bundle, and navigation shows the signed-in username. Skill cards show consistent View skill buttons and result counts.

Session requests optionally include a preferred time and public meeting place. The provider can confirm those details from their dashboard, and the learner sees confirmation on theirs. Completion still requires the provider's separate confirmation after teaching; completed sessions link directly to the review form. There is no chat or automated calendar booking. Meeting details appear only on participant dashboards. Run manage.py migrate after updating an existing installation.

