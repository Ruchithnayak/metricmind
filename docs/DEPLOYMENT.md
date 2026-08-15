# Deployment

## Offline demo

```powershell
python run_offline.py
```

Open `http://127.0.0.1:8080`.

## Production direction

Serve the web client from a controlled host and move authentication, data access, secrets and authorization to a production backend. Keep the governed metric definitions shared between analytical services and the UI.
