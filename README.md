# HR Analytics & Attrition Prediction

Quick deploy to Streamlit Community Cloud

1. Push this repository to GitHub (already done).
2. Go to https://share.streamlit.io and sign in with your GitHub account.
3. Click "New app" → select this repository, branch `main`, and the file `app.py` as the entrypoint.
4. Streamlit will build using `requirements.txt` and deploy the app.

Notes
- `users.json`, `*.pkl`, and `*.xlsx` are ignored by `.gitignore`. The app ships with default accounts (`admin`/`admin123`) if `users.json` is absent.
- To persist user accounts on Streamlit Cloud, use external storage or update the app to use Streamlit Secrets / a database.

If you want, I can: add a `Procfile`/`Dockerfile`, modify the app to store users in `st.secrets`, or add a GitHub Actions workflow to auto-deploy.