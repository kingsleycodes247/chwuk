# CHW UK — Community of Hashem Worldwide, United Kingdom branch

Django website for **CHW London Synagogue, Selby Centre, Selby Road, London N17 8JL**.
Shabbat worship is held every Saturday. Staff upload the weekly programme in the admin panel and it appears on the landing page.

## Run it locally

```bash
cp .env.example .env                                   # local dev settings (DJANGO_DEBUG=1)
npm install && npm run build                           # builds Tailwind CSS (use `npm run dev` while editing templates)
python -m venv .venv && source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python manage.py makemigrations core
python manage.py migrate
python manage.py createsuperuser                       # your admin login
python manage.py seed_demo                             # optional: placeholder programme for testing
python manage.py runserver
```

Open http://127.0.0.1:8000/ — admin login is at http://127.0.0.1:8000/admin/ (also linked in the nav and footer).

## Uploading the weekly programme (admin)

1. Log in at `/admin/` → **Weekly programmes → Add**.
2. The date defaults to the coming Saturday (only Saturdays are accepted).
3. Either or both:
   * tick **Fill in the standard order of service**, then edit ministers / durations in the rows below; and/or
   * upload the finished programme as an image or PDF (max 8 MB).
4. Keep **Published** ticked. The landing page shows the next upcoming published programme; once its date passes, the latest one stays up until the next is published. Past programmes are listed at `/programmes/`.

Tip: in the list view, select last week's programme → action **Copy to the following Saturday (as a draft)**, update the names, then publish.

Other admin sections: **Site settings** (service time, phone, email, WhatsApp, social links — the service time is blank by default, so set it), **Announcements**, **Events**, **Contact messages**.
Give other staff their own accounts (Users → tick *Staff status* and grant only the permissions they need).

## Images (design them in Canva)

Upload under **Site settings** and **Gallery** in the admin — no code changes needed. Until you upload them, the site shows a navy placeholder.

| Where | Canva size | Notes |
|---|---|---|
| Hero background | 2400 × 1200 px (landscape) | Shown softened (about 35% opacity) behind the heading; the logo sits in a small card on top of it |
| About us picture | 1200 × 1400 px (portrait) | Beside the About text |
| Gallery | 1200 × 800 px each | Appears as a grid once at least one is published; set the order and captions in the list |

JPG, PNG or WEBP, under 8 MB each. The logo itself is `core/static/core/img/logo.jpg` — replace that file to change it (it is also the browser-tab icon and the admin logo).

## Admin look

The admin is restyled (navy and gold, branded login, a dashboard showing whether next Saturday's programme is published) using template and CSS overrides in `templates/admin/` and `core/static/core/admin.css`. It needs no extra packages. Colours are variables at the top of the CSS file.

## Configuration (environment variables)

| Variable | Purpose |
|---|---|
| `DJANGO_SECRET_KEY` | **Required in production** |
| `DJANGO_DEBUG` | `1` for local development only; unset/`0` in production (the default) |
| `DJANGO_ALLOWED_HOSTS` | comma-separated, e.g. `chwuk.org,www.chwuk.org` |
| `DJANGO_CSRF_TRUSTED_ORIGINS` | e.g. `https://chwuk.org` |
| `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_HOST`, `POSTGRES_PORT` | use PostgreSQL instead of SQLite |

Settings are read from the environment or a `.env` file in the project root. Uploaded programmes live in `media/` — back that folder up (see `DEPLOY.md`).

## Notes
* **Going live:** see `DEPLOY.md` (VPS setup, nginx, HTTPS, several sites on one server).
* Tailwind is compiled locally (`npm run build`) into `core/static/core/tailwind.css`, which is committed so the server needs no Node. Rebuild and commit whenever you change classes in the templates.
* Admin login has no lockout. Before launch, consider adding `django-axes` and enabling HTTPS.
