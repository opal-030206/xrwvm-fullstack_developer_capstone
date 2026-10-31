# Submission guide - 28 tasks

Everything marked **READY** was produced by actually running the application in
this folder. Items marked **YOU MUST DO** need your GitHub account and your IBM
Cloud account - they cannot be produced from this machine alone.

## Status at a glance

| # | Points | What to submit | File / artefact | Status |
|---|--------|----------------|-----------------|--------|
| 1 | 1 | Public GitHub URL of `README.md` | `README.md` | **YOU MUST DO** (push repo, copy URL) |
| 2 | 1 | Terminal output of the running Django server | `submission/django_server` | READY |
| 3 | 3 | GitHub URL of `server/frontend/static/About.html` | `server/frontend/static/About.html` | **YOU MUST DO** (push repo, copy URL) |
| 4 | 2 | GitHub URL of `server/frontend/static/Contact.html` | `server/frontend/static/Contact.html` | **YOU MUST DO** (push repo, copy URL) |
| 5 | 2 | cURL login command + output | `submission/loginuser` | READY |
| 6 | 2 | cURL logout command + output | `submission/logoutuser` | READY |
| 7 | 1 | GitHub URL of `Register.jsx` | `server/frontend/src/components/Register/Register.jsx` | **YOU MUST DO** (push repo, copy URL) |
| 8 | 2 | cURL reviews for a dealer | `submission/getdealerreviews` | READY |
| 9 | 2 | cURL all dealers | `submission/getalldealers` | READY |
| 10 | 2 | cURL one dealer by id | `submission/getdealerbyid` | READY |
| 11 | 2 | cURL dealers in Kansas | `submission/getdealersbyState` | READY |
| 12 | 2 | Screenshot, root logged in to admin | `screenshots/admin_login.png` | READY |
| 13 | 1 | Screenshot, root logged out of admin | `screenshots/admin_logout.png` | READY |
| 14 | 2 | cURL car makes + models | `submission/getallcarmakes` | READY |
| 15 | 2 | Same file covers task 15 | `submission/getallcarmakes` | READY |
| 16 | 2 | Sentiment for "Fantastic services" | `submission/analyzereview` | READY |
| 17 | 1 | Screenshot, home page signed out | `screenshots/get_dealers.png` | READY |
| 18 | 2 | Screenshot, home page signed in + address bar | `screenshots/get_dealers_loggedin.png` | READY |
| 19 | 2 | Screenshot, dealers filtered by Kansas + address bar | `screenshots/dealersbystate.png` | READY |
| 20 | 1 | Screenshot, dealer details + reviews + address bar | `screenshots/dealer_id_reviews.png` | READY |
| 21 | 1 | Screenshot, review form filled in | `screenshots/dealership_review_submission.png` | READY |
| 22 | 2 | Screenshot, posted review | `screenshots/added_review.png` | READY |
| 23 | 3 | GitHub Actions run log | `submission/CICD` | **YOU MUST DO** (push repo, run workflow, paste log) |
| 24 | 1 | Deployment URL | `submission/deploymentURL` | **YOU MUST DO** (deploy to Code Engine) |
| 25 | 2 | Screenshot, deployed landing page | `screenshots/deployed_landingpage.png` | **REPLACE** (currently local production-mode) |
| 26 | 2 | Screenshot, deployed logged-in page | `screenshots/deployed_loggedin.png` | **REPLACE** (currently local production-mode) |
| 27 | 2 | Screenshot, deployed dealer details | `screenshots/deployed_dealer_detail.png` | **REPLACE** (currently local production-mode) |
| 28 | 2 | Screenshot, review in deployed app | `screenshots/deployed_add_review.png` | **REPLACE** (currently local production-mode) |

## Important about Tasks 25-28

The four `deployed_*.png` files in `screenshots/` were captured from the app
running in **production mode on this laptop** (`waitress` + WhiteNoise +
`CAR_DEALERSHIP_DEBUG=0` on `http://127.0.0.1:8002`). You can see that address
in each screenshot's address bar. They prove the production build works, but
they are **not** IBM Cloud deployment evidence and should not be submitted for
Tasks 25-28 as they are.

After you deploy (see `deploy/code-engine.md`), regenerate them with the real
URL:

```bash
node tools/shoot-deployed.mjs https://<your-app>.<region>.codeengine.appdomain.cloud
```

## Steps to finish the remaining tasks

1. **GitHub repository** - done. Pushed to
   <https://github.com/opal-030206/Capstone_carDealership> (public, branch `main`,
   commits `05570aa` and `02f4baa`).

2. **Tasks 1, 3, 4, 7** - use these exact URLs:

   ```
   https://github.com/opal-030206/Capstone_carDealership/blob/main/README.md
   https://github.com/opal-030206/Capstone_carDealership/blob/main/server/frontend/static/About.html
   https://github.com/opal-030206/Capstone_carDealership/blob/main/server/frontend/static/Contact.html
   https://github.com/opal-030206/Capstone_carDealership/blob/main/server/frontend/src/components/Register/Register.jsx
   ```

   The repository is **public**, so the links work for the grader.

3. **Task 23** - the push triggers `.github/workflows/ci.yml`. Open the
   **Actions** tab, wait for the green run, open the latest job, and copy the
   step log into `submission/CICD`. The file currently in `submission/CICD` is a
   placeholder and must be replaced.

4. **Tasks 24-28** - follow `deploy/code-engine.md`, then write the public URL
   into `submission/deploymentURL` (overwriting the placeholder) and rerun
   `node tools/shoot-deployed.mjs <deployment-url>`.

## Notes for the grader's environment

* The app is a single Django project; the React bundle in
  `server/frontend/dist/` is what Django serves.
* `submission/*` transcripts were produced with the real commands shown at the
  top of each file, against `http://localhost:8000`.
* Screenshots were taken in Chrome at 1280x720 with the browser address bar
  visible, as Tasks 18-20 require.
