# CartPilot — Full-stack e-commerce starter

CartPilot is a Django REST Framework + React + Axios e-commerce application with product/category CRUD, JWT authentication, cart, wishlist, checkout, order history, reviews, recommendations, budgets/spending insights, price alerts, and admin analytics.

## Requirements
- Python 3.11+
- Node.js 20+
- PostgreSQL 16+ (or SQLite for a quick smoke test)

## 1. Backend setup (Windows PowerShell)
```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

Edit `backend/.env` and set `DATABASE_URL` to your local PostgreSQL database, for example:
`DATABASE_URL=postgresql://cartpilot_user:YOUR_PASSWORD@127.0.0.1:5432/cartpilot`

Create the database and user in PostgreSQL/pgAdmin first. Then run:
```powershell
python manage.py makemigrations store
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

If PowerShell blocks activation, use Command Prompt:
```bat
.venv\Scripts\activate.bat
```

Backend:
- API root: `http://127.0.0.1:8000/api/v1/`
- Django admin: `http://127.0.0.1:8000/admin/`
- Health: `http://127.0.0.1:8000/api/v1/health/`

## 2. Frontend setup
Open a second terminal:
```powershell
cd frontend
npm install
Copy-Item .env.example .env
npm run dev
```
Open the Vite URL shown in the terminal (normally `http://localhost:5173`).

## 3. Seed demo catalog
With the backend virtual environment active:
```powershell
python manage.py seed_demo
```
This creates demo categories and products. It does not create a demo user or password.

## Features included
- JWT register/login and authenticated profile endpoint
- Product/category read APIs and admin-only product/category write APIs
- Search, category filter, price range, sort, pagination
- User-owned cart and wishlist
- Transactional checkout with server-side price/stock validation
- Order history/detail and cancellation when eligible
- Product reviews (create/update/delete own review)
- Rule-based recommendations
- Monthly budgets and spending insights
- Price alerts and recorded price snapshots
- Admin analytics and low-stock endpoints
- React UI for catalog, product details, cart, wishlist, orders, insights, price watch, login/register, and admin dashboard

## Important notes
- Checkout uses a simulated payment method; no real payment provider is connected.
- Price tracking records CartPilot's own product price snapshots; it does not scrape external shops.
- Product/category create/update/delete are staff-only through API. Use Django admin or a staff JWT session.
- JWT access tokens are stored in localStorage in this learning starter. For production, consider secure HttpOnly cookie-based auth, rate limiting, HTTPS, email verification, and a professional security review.
- Set a strong `DJANGO_SECRET_KEY` and `DJANGO_DEBUG=False` before deployment.
