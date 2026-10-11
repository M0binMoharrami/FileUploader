# Local File Uploader

A small Flask app for sending files from a browser to the computer running the server. Multiple files can be selected at once, but they are uploaded **sequentially**: file 2 starts only after file 1 finishes. Each queued file has its own progress bar.

## Features

- Multi-file selection and drag-and-drop
- Sequential upload queue (one active upload at a time)
- Per-file progress indicators and failure reporting
- Uploaded file list with size and modified date
- Download and delete actions
- Files stored in the local `uploads/` directory
- Responsive dark interface
- Login required for the web interface and all file APIs
- Session-based authentication and logout

## Requirements

Python 3.10 or newer is recommended.

## Run

```bash
python -m venv .venv
```

Linux/macOS:

```bash
source .venv/bin/activate
```

Windows:

```powershell
.venv\Scripts\activate
```

Install dependencies and configure your login before starting. The defaults are `admin` / `ChangeMe-Please-123!`; change them before using this on a network.

Linux/macOS (same terminal):

```bash
pip install -r requirements.txt
export UPLOADER_USERNAME='your-username'
export UPLOADER_PASSWORD='use-a-long-unique-password'
export FLASK_SECRET_KEY="$(python -c 'import secrets; print(secrets.token_hex(32))')"
python app.py
```

Windows PowerShell:

```powershell
pip install -r requirements.txt
$env:UPLOADER_USERNAME = 'your-username'
$env:UPLOADER_PASSWORD = 'use-a-long-unique-password'
$env:FLASK_SECRET_KEY = python -c "import secrets; print(secrets.token_hex(32))"
python app.py
```

Open `http://127.0.0.1:5000` on the same computer. To use it from another device on the same Wi-Fi/LAN, open `http://COMPUTER_LAN_IP:5000` on that device. Allow port 5000 through the computer's firewall only on trusted private networks.

## Project layout

```text
LocalFileUploader/
├── app.py
├── requirements.txt
├── README.md
├── templates/
│   ├── index.html
│   └── login.html
└── uploads/
```

Files you upload are saved in `uploads/`. Back up this folder if you need to preserve uploaded files.

## Notes

- The server accepts uploads up to 2 GB per request by default. Change `MAX_CONTENT_LENGTH` in `app.py` to adjust this limit.
- The web interface, upload/list/download/delete APIs require a valid login session.
- Credentials are configured with `UPLOADER_USERNAME` and `UPLOADER_PASSWORD`. If these are not set, the app uses the setup defaults shown above; replace them before use.
- Set `FLASK_SECRET_KEY` to a long random value for stable session signing. If omitted, a random key is generated at startup and existing sessions are invalidated on restart.
- This app is intended for local/trusted network use. For public internet access, put it behind HTTPS and a production WSGI server, and add rate limiting/monitoring. Do not use the built-in development server as a public production server.
- If a file with the same name already exists, the app saves the new file with a numeric suffix rather than overwriting the old one.
