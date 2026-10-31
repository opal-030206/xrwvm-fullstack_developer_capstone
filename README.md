# Cars Dealership

**Project name:** Cars Dealership - National Car Retailer Web Application
**Programme:** IBM Full-Stack Developer Professional Certificate - Capstone Project
**Author:** Nishtha Sharma

Cars Dealership is a full-stack web application for a fictional national car
retailer with dealership branches across the United States. Visitors can browse
every branch, filter by state, read customer reviews, sign up, sign in, and post
reviews that are scored by a separate sentiment analysis microservice.

---

## 1. Architecture

```
                    +-------------------------------------+
   Browser  ──────> |  Django 5.2  (server/)              |
                    |  - React single-page app (Vite)     |
                    |  - REST/JSON API under /djangoapp/  |
                    |  - Session auth + Django admin      |
                    |  - Static pages: About / Contact    |
                    +------------------+------------------+
                                       | HTTP POST /analyze
                                       v
                    +-------------------------------------+
                    |  Flask 3  (server/sentiment/)       |
                    |  Sentiment analysis microservice    |
                    |  Lexicon + negation aware scoring   |
                    +-------------------------------------+
                                       |
                                       v
                              SQLite database
                          (dealers, cars, users, reviews)
```

* **Django** owns authentication, the dealer/car/review APIs, the admin site and
  the page routes. It serves the compiled React bundle through WhiteNoise.
* **React 18 + Vite** renders the UI (dealer grid, dealer detail, login,
  sign-up, post review) and talks to the Django API with `fetch`.
* **Flask** exposes `POST /analyze`. Django proxies to it from
  `/djangoapp/analyze_review` and from `add_review`, and falls back to the same
  in-process analyser if the microservice is unavailable.
* **SQLite** keeps the project portable; the schema is a small relational model
  (`CarMake`, `CarModel`, `Dealer`, `Review`).

---

## 2. Repository layout

```
cars-dealership/
├── manage.py                     Django entry point
├── requirements.txt
├── Dockerfile                    Multi-stage image: React build + Django/gunicorn
├── Dockerfile.sentiment          Flask sentiment image
├── docker-compose.yml            Both services wired together
├── .github/workflows/ci.yml      GitHub Actions: tests, React build, Docker build
├── server/
│   ├── settings.py               Django settings (SQLite, WhiteNoise, CORS)
│   ├── urls.py
│   ├── djangoapp/
│   │   ├── models.py             CarMake, CarModel, Dealer, Review
│   │   ├── views.py              JSON API (login, dealers, reviews, cars, sentiment)
│   │   ├── urls.py               /djangoapp/... routes
│   │   ├── page_urls.py          /, /about, /contact and React routes
│   │   ├── services.py           serialisers + Flask client with local fallback
│   │   ├── tests.py              22 Django tests
│   │   ├── admin.py
│   │   └── management/commands/seed_data.py
│   ├── sentiment/
│   │   ├── analyzer.py           Lexicon sentiment analyser
│   │   └── app.py                Flask app (POST /analyze, GET /healthz)
│   └── frontend/
│       ├── src/                  React sources
│       │   └── components/Register/Register.jsx   five fields + Register button
│       ├── static/About.html     About Us page
│       ├── static/Contact.html   Contact Us page
│       ├── static/css/pages.css
│       ├── static/images/        Dealer photos, team portraits, map
│       └── dist/                 Vite production build (generated)
├── screenshots/                  Graded screenshots (Tasks 12-13, 17-22, 25-28)
└── submission/                   cURL transcripts and terminal output (Tasks 2, 5-11, 14-16)
```

---

## 3. Running the project locally

Prerequisites: Python 3.12+, Node.js 20+.

```bash
# 1. Python environment
python -m venv .venv
.venv\Scripts\activate            # Windows
# source .venv/bin/activate       # macOS / Linux
pip install -r requirements.txt

# 2. Database + demo data
python manage.py migrate
python manage.py seed_data

# 3. Sentiment microservice (terminal 1)
python -m flask --app server.sentiment.app run --host 127.0.0.1 --port 5050

# 4. React build + Django (terminal 2)
cd server/frontend && npm install && npm run build && cd ../..
python manage.py runserver 127.0.0.1:8000
```

Open <http://127.0.0.1:8000/>.

### Demo accounts

| Username | Password   | Role                          |
|----------|------------|-------------------------------|
| `root`   | `root123`  | superuser - Django admin, /admin/ |
| `jdoe`   | `jdoe123`  | customer                      |
| `msmith` | `msmith123` | customer                     |
| `apatel` | `apatel123` | customer                     |

The seed data contains **18 dealerships** in 14 states (4 in Kansas), **8 car
makes** with 21 models, and 12 published reviews.

---

## 4. API reference

All endpoints are JSON. POST bodies are accepted as `application/json`.

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/djangoapp/login` | Sign in, returns the authenticated user |
| POST | `/djangoapp/logout` | End the session |
| POST | `/djangoapp/register` | Create an account (username, first name, last name, email, password) |
| GET  | `/djangoapp/session` | Current session state |
| GET  | `/djangoapp/get_dealers` | Every dealership |
| GET  | `/djangoapp/get_dealer/<id>` | One dealership |
| GET  | `/djangoapp/get_dealers/<state>` | Dealerships in a state, e.g. `Kansas` |
| GET  | `/djangoapp/reviews/dealer/<id>` | Reviews for a dealership |
| POST | `/djangoapp/add_review` | Add a review (login required), stores sentiment |
| GET  | `/djangoapp/get_cars` | All car makes with their models |
| POST | `/djangoapp/analyze_review` | Sentiment for arbitrary text (proxies Flask) |

Examples:

```bash
curl -s -X POST http://localhost:8000/djangoapp/login \
  -H 'Content-Type: application/json' \
  -d '{"userName":"root","password":"root123"}' \
  -c cookies.txt -b cookies.txt

curl -s http://localhost:8000/djangoapp/get_dealers/Kansas
curl -s http://localhost:8000/djangoapp/reviews/dealer/1
curl -s -X POST http://localhost:8000/djangoapp/analyze_review \
  -H 'Content-Type: application/json' -d '{"text":"Fantastic services"}'
# -> {"confidence": 1.0, "score": 3.4, "sentiment": "positive", ...}
```

Full transcripts are in [`submission/`](submission), regenerated with
`bash scripts/capture-curl.sh` while both services are running.

---

## 5. Tests and CI

```bash
python manage.py test server.djangoapp      # 22 tests
cd server/frontend && npm run build         # production bundle
```

`.github/workflows/ci.yml` runs three jobs on every push and pull request:

1. **Django tests** - `manage.py check --deploy`, the 22-test suite, `collectstatic`.
2. **React build** - `npm ci` and `npm run build`, bundle uploaded as an artefact.
3. **Docker images** - builds both images, starts them, and smoke-tests the
   dealers API and the sentiment endpoint.

---

## 6. Container images and deployment

```bash
docker compose up --build          # Django on :8000, Flask on :5050
```

`Dockerfile` is a multi-stage build: Node compiles the React bundle, then a
slim Python image runs `gunicorn server.wsgi:application` with WhiteNoise
serving the static build. Step-by-step IBM Cloud Code Engine instructions are in
[`deploy/code-engine.md`](deploy/code-engine.md).

---

## 7. Graded artefacts

| Tasks | Artefact |
|-------|----------|
| 1, 3, 4, 7 | `README.md`, `server/frontend/static/About.html`, `server/frontend/static/Contact.html`, `server/frontend/src/components/Register/Register.jsx` |
| 2 | `submission/django_server` |
| 5, 6, 8-11, 14-16 | `submission/loginuser`, `logoutuser`, `getdealerreviews`, `getalldealers`, `getdealerbyid`, `getdealersbyState`, `getallcarmakes`, `analyzereview` |
| 12, 13, 17-22 | `screenshots/admin_login.png` ... `screenshots/added_review.png` |
| 23 | `submission/CICD` (GitHub Actions run log) |
| 24-28 | `submission/deploymentURL` and `screenshots/deployed_*.png` |

See [`SUBMISSION-GUIDE.md`](SUBMISSION-GUIDE.md) for what each task needs and
which artefacts still require your own GitHub repository and IBM Cloud account.
