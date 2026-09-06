

#Payment Transaction Engine

The Payment Transaction Engine is a highly concurrent payment processing engine built using Python‚ FastAPI‚ SQLAlchemy‚ and Cloud-based PostgreSQL from Neon․

Key Features:

1․ User Wallet Management - Users that have signed up with the payment engine are credited an initial balance․
2․ ACID Compliant Transfers- Balance transfers are done without any race condition by using the 'with for update' clause for row level locking․
3․ Transaction History - The transactions which were successful and which were failed shall be recorded in real time․
4․ Cloud Database Integration - Neon provides a cloud-based data store for data storage․
Tech Stack․ In terms of server-side technology stack‚ the payment engine has been built using Python‚ FastAPI and Uvicorn․ It uses SQLAlchemy and Pydantic for ORM and validation‚ and is based on a PostgreSQL database (Neon Cloud)․
  
## Live Demo & Testing

https://payment-engine-4dju.onrender.com/docs



# payment-engine
>>>>>>> 89db6692f181feff0137516f9e564f798f63e081
