# 💳 Payment Transaction Engine

A high-concurrency payment processing engine built with Python, FastAPI, SQLAlchemy, and Cloud PostgreSQL (Neon).

## 🚀 Features
- **User Wallet Management:** Create user accounts with initial balances.
- **ACID-Compliant Transfers:** Safe balance transfers with row-level locking (`with_for_update`) to prevent race conditions.
- **Transaction History:** Real-time logging of succeeded and failed transfers.
- **Cloud Database Integration:** Connected to serverless PostgreSQL on Neon.tech.

## 🛠️ Tech Stack
- **Backend:** Python, FastAPI, Uvicorn
- **ORM & Validation:** SQLAlchemy, Pydantic
- **Database:** PostgreSQL (Neon Cloud)

## 🏃 Local Setup
1. **Clone repository:**
   ```bash
   git clone [https://github.com/YOUR_GITHUB_USERNAME/payment-transaction-engine.git](https://github.com/YOUR_GITHUB_USERNAME/payment-transaction-engine.git)
   cd payment-transaction-engine