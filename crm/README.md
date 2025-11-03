# 🧾 CRM Celery Report System

This document explains how to set up and run the Celery-based automated reporting system for the **alx-backend-graphql_crm** project.  
The Celery task generates a **weekly CRM report** that summarizes:
- Total customers  
- Total orders  
- Total revenue  

The report data is fetched via the **GraphQL schema** and logged automatically.

---

## ⚙️ 1. Prerequisites

Before starting, ensure the following services are installed and running:
- **Python 3.10+**
- **Redis Server**
- **Django**
- **Celery**
- **django-celery-beat**

---

## 📦 2. Installation

### Step 1 — Install Dependencies

Install all required dependencies from `requirements.txt`:

```bash
pip install -r requirements.txt
Ensure the following packages are present:

css
Copy code
celery
django-celery-beat
redis
graphene-django
django-filter
Step 2 — Install and Start Redis
Install Redis (if not already installed):

bash
Copy code
sudo apt update
sudo apt install redis-server
Start Redis:

bash
Copy code
sudo service redis-server start
Verify Redis is running:

bash
Copy code
redis-cli ping
# Should return: PONG
🧩 3. Django Setup
Run database migrations:

bash
Copy code
python manage.py migrate
Confirm django_celery_beat is listed in your INSTALLED_APPS in crm/settings.py.

🚀 4. Running the CRM Application
Start the Django development server:

bash
Copy code
python manage.py runserver
Verify that the GraphQL endpoint works by visiting:

bash
Copy code
http://localhost:8000/graphql
Then run this query to confirm the report fields are accessible:

graphql
Copy code
query {
  totalCustomers
  totalOrders
  totalRevenue