# CHIS Device Manager

A device tracking system for Kenya's Community Health Information System (eCHIS).

## Roles & Hierarchy

```
Country Admin → County Focal → Sub-County Focal → CHA → CHP
```

| Role | Device | Scope |
|------|--------|-------|
| CHP  | Phone  | Own device only |
| CHA  | Tablet | CHU(s) they supervise |
| Sub-County Focal | Tablet | All CHUs in sub-county |
| County Focal | Tablet/Laptop | All sub-counties in county |
| Country Admin | — | Everything |

---

## Local Setup

### 1. Install Python dependencies
```bash
pip install -r requirements.txt
```

### 2. Run migrations
```bash
python manage.py migrate
```

### 3. Create a superuser (for Django admin)
```bash
python manage.py createsuperuser
```

### 4. Seed sample data (optional, for testing)
```bash
python manage.py seed_data
```
This creates sample counties, CHUs, and test users. All passwords: `chis1234`

### 5. Run the server
```bash
python manage.py runserver
```

Visit: http://127.0.0.1:8000

---

## Deploy to Railway

1. Push this folder to a GitHub repo
2. Go to [railway.app](https://railway.app) → New Project → Deploy from GitHub
3. Add environment variables:
   ```
   SECRET_KEY=<generate a strong random key>
   DEBUG=False
   ```
4. Railway auto-detects the `Procfile` and runs migrations on deploy

## Deploy to Render

1. Push to GitHub
2. Go to [render.com](https://render.com) → New Web Service → Connect repo
3. Build command: `pip install -r requirements.txt`
4. Start command: `gunicorn chis_devices.wsgi --bind 0.0.0.0:$PORT`
5. Add env vars: `SECRET_KEY`, `DEBUG=False`

---

## Adding Real Data

After deploying, use the Django Admin (`/admin/`) to:
1. Add Counties, Sub-Counties, CHUs
2. Create user accounts and assign roles + locations
3. Devices can then be added from the main interface

---

## Generating a Secret Key
```python
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```
