# HR Analytics & Attrition Prediction

Quick deploy to Streamlit Community Cloud

1. Push this repository to GitHub (already done).
2. Go to https://share.streamlit.io and sign in with your GitHub account.
3. Click "New app" → select this repository, branch `main`, and the file `app.py` as the entrypoint.
4. Streamlit will build using `requirements.txt` and deploy the app.

Notes
- `users.json`, `*.pkl`, and `*.xlsx` were previously ignored by `.gitignore`, which can cause deployment failures because the app needs `HR Data.xlsx`, `rf_pipeline.pkl`/`rf_pipeline_fixed.pkl`, and `users.json` at runtime.
- These files are now explicitly un-ignored in `.gitignore` so they can be committed and included in deploys.
- When deploying to Streamlit Community Cloud, choose branch `main` and `app.py` as the entrypoint.
- If `users.json` is missing, the app will still fall back to default accounts (`admin`/`admin123`), but commit `users.json` when you want persistent user account data.
- To persist logins or production secrets safely, consider moving authentication storage to Streamlit Secrets or a database.

If you want, I can also add a `Procfile`/`Dockerfile`, modify the app to store users in `st.secrets`, or add a GitHub Actions workflow to auto-deploy.