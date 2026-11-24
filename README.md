# Kanban Expense & Bill Tracker

A modern, decoupled Single Page Application (SPA) for managing personal expenses, bills, and monthly budgets using an interactive Kanban board with atomic transaction safety and real-time financial tracking.

---

## 🛠️ Tech Stack

### Backend
- **Django 6.1** & **Django REST Framework (DRF)**
- **PostgreSQL** with ACID `transaction.atomic()` & `select_for_update()`
- **Python Dotenv** & **Django CORS Headers**

### Frontend
- **Vue 3** (Composition API, `<script setup>`)
- **Vite** & **Pinia** (State Management with Optimistic UI & Auto-Rollback)
- **Tailwind CSS v4** (`@tailwindcss/vite`)
- **vuedraggable** (Drag-and-drop fractional indexing)
- **Axios** & **Lucide Vue Next** icons
- **Plus Jakarta Sans** typography

---

## ✨ Features

1. **Interactive Kanban Board**
   - 3 Default Columns: *Wishlist / Rencana*, *Tagihan / Belum Bayar*, *Lunas / Paid*.
   - Drag-and-drop cards between columns with fractional indexing (`position`).
   - **Auto-Deduct Balance:** Moving to *Lunas* automatically deducts wallet balance. Rejects (HTTP 400) if balance is insufficient.
   - **Auto-Refund Balance:** Pulling back from *Lunas* to unpaid automatically refunds wallet balance.
   - **Optimistic UI:** Instant visual feedback with automatic rollback on error.
   - Real-time search by title/notes and filtering by category or wallet.

2. **Digital Wallet Management**
   - Create, edit balances/names, and delete digital wallets.
   - Total balance aggregation across all active wallets.
   - Safe deletion prevention if wallet is currently linked to existing expense cards (`models.PROTECT`).

3. **📅 Bill Schedule Calendar View**
   - Interactive monthly calendar showing bills and expenses on their respective due dates.
   - Status indicators (Paid vs Pending) and monthly due totals.
   - Click cards directly in the calendar to view/edit details.

4. **📊 Analytics & Budget Tracking**
   - Category monthly budget progress bars with visual overbudget warnings.
   - Wallet spending and liquidity distribution.
   - Smart insights: largest expense item, most expensive category, and total monthly spent.

5. **Reusable Modern UI Components**
   - Custom Dropdown (`CustomSelect.vue`) with category color dots and subtitle badges.
   - Interactive Popover Calendar (`DatePicker.vue`) with quick shortcuts (Today, Tomorrow, End of Month).
   - Reusable Confirmation Dialog (`ConfirmModal.vue`) for safe card and wallet deletions.
   - Toast notifications with automatic dismiss.

---

## 🚀 Quick Start Guide

### 1. Prerequisites
- Python 3.10+
- Node.js 18+
- PostgreSQL database server running on `localhost:5432`

### 2. Backend Setup
```bash
cd backend

# Create & activate virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1   # Windows PowerShell
# source venv/bin/activate    # Linux / macOS

# Install dependencies
pip install django djangorestframework django-cors-headers psycopg2-binary python-dotenv

# Setup environment variables
cp .env.example .env
# Adjust DB_PASSWORD and DB_NAME in .env according to your PostgreSQL setup

# Run database migrations
python manage.py migrate

# Seed default columns, wallets, categories, and sample cards
python manage.py seed_data

# Start backend server
python manage.py runserver
```
*Backend runs on `http://127.0.0.1:8000`*

### 3. Frontend Setup
```bash
cd frontend

# Install dependencies
npm install

# Setup environment variables
cp .env.example .env

# Run Vite development server
npm run dev
```
*Frontend runs on `http://localhost:5173` or `http://localhost:5174`*

---

## 🧪 Testing
Run backend unit & integration tests:
```bash
cd backend
python manage.py test expenses
```
