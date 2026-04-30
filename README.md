# Sentiment Analysis Web App (FastAPI + TypeScript)

A simple one-page web app that lets you upload multiple files and get sentiment predictions for each file.

- **Backend:** FastAPI + Hugging Face Transformers
- **Model:** `cardiffnlp/twitter-roberta-base-sentiment-latest` (widely used open-source sentiment model)
- **Frontend:** One-page TypeScript UI (bundled with esbuild)

---

## 1) Project structure

```text
backend/
  main.py
  requirements.txt
frontend/
  package.json
  src/app.ts
  public/
    index.html
    styles.css
    app.js (generated)
```

---

## 2) Local run (quick test)

### Backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000
```

### Frontend build + serve

Open a second terminal:

```bash
cd frontend
npm install
npm run build
python3 -m http.server 8080 --directory public
```

Now open: `http://localhost:8080`

Set **Backend API URL** to: `http://localhost:8000`

---

## 3) Deploy on Ubuntu cloud server (production-ish setup)

### Step A — Install system dependencies

```bash
sudo apt update
sudo apt install -y python3 python3-venv python3-pip nodejs npm nginx
```

### Step B — Copy project to server

```bash
git clone https://github.com/omosaiye/sentimentAnn.git sentiment-app
cd sentiment-app
```

### Step C — Build backend environment

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### Step D — Build frontend

```bash
cd ../frontend
npm install
npm run build
```

### Step E — Create a systemd service for FastAPI

Create `/etc/systemd/system/sentiment-api.service`:

```ini
[Unit]
Description=Sentiment FastAPI Service
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/sentiment-app/backend
Environment="PATH=/home/ubuntu/sentiment-app/backend/.venv/bin"
ExecStart=/home/ubuntu/sentiment-app/backend/.venv/bin/uvicorn main:app --host 127.0.0.1 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl daemon-reload
sudo systemctl enable sentiment-api
sudo systemctl start sentiment-api
sudo systemctl status sentiment-api
```

### Step F — Configure Nginx for frontend + API proxy

Create `/etc/nginx/sites-available/sentiment-app`:

```nginx
server {
    listen 80;
    server_name _;

    root /home/ubuntu/sentiment-app/frontend/public;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /analyze {
        proxy_pass http://127.0.0.1:8000/analyze;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /health {
        proxy_pass http://127.0.0.1:8000/health;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

Enable and reload Nginx:

```bash
sudo ln -s /etc/nginx/sites-available/sentiment-app /etc/nginx/sites-enabled/sentiment-app
sudo nginx -t
sudo systemctl reload nginx
```

Visit your server IP in a browser.

---

## 4) About your Ollama Cloud account

This implementation uses a high-quality open-source Hugging Face sentiment model directly in Python, so **Ollama Cloud is optional**.

If you want, a next step is replacing the classifier with an Ollama-hosted model and calling it from FastAPI. The UI and API contract can stay the same.

---

## 5) API contract

### `POST /analyze`

- **Form field:** `files` (one or many uploads)
- **Returns:** per-file sentiment label and confidence score

Example response:

```json
{
  "model": "cardiffnlp/twitter-roberta-base-sentiment-latest",
  "total_files": 2,
  "results": [
    {
      "filename": "note1.txt",
      "label": "positive",
      "score": 0.9921,
      "chars_analyzed": 847
    }
  ]
}
```
