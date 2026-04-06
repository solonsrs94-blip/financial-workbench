# Financial Workbench

Personal financial analysis workbench with multi-method valuation tools.

## Setup

### 1. Clone and install

```bash
git clone <repo-url>
cd Vision
pip install -r requirements.txt
```

### 2. Configure secrets

```bash
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
```

Edit `.streamlit/secrets.toml` and fill in your API keys and Firebase credentials.

### 3. Firebase project

The app uses Firebase for authentication and cloud storage:
- **Firebase Auth** (Email/Password) for user login
- **Firestore** for saving valuations

You need a Firebase project with Auth and Firestore enabled. Add the service account credentials to your `secrets.toml` under `[firebase_service_account]`.

### 4. Run locally

```bash
streamlit run app.py
```

## Deployment (Streamlit Community Cloud)

1. Push code to GitHub (secrets are gitignored)
2. Connect repo on [share.streamlit.io](https://share.streamlit.io)
3. Add secrets via the app settings UI (paste contents of `secrets.toml`)
