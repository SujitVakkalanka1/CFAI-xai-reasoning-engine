# CFAI Finance Reasoning Model

A simple academic finance project with a login page.

## Login

Default login:

```text
Username: admin
Password: finance123
```

You can change these during deployment by setting:

```text
APP_USERNAME
APP_PASSWORD
SECRET_KEY
```

## What the app does

The app asks for basic financial details and gives:

- A clear result
- Simple reasons
- Suggested improvements

It is made for academic use only. It is not financial advice.

## Run locally

### Windows

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

### macOS or Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Open this in your browser:

```text
http://127.0.0.1:5000
```

## Deploy without Docker

Use these commands on a Python hosting service:

```text
Build command:
pip install -r requirements.txt

Start command:
gunicorn wsgi:app
```

For Render, create a Web Service, connect your GitHub repository, then use the build and start commands above.

For PythonAnywhere, create a Flask web app and point the WSGI file to `app.py`.
