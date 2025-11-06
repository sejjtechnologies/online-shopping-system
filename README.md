# 🛒 Online Shopping & Marketing System

## Overview

This is a full-stack web application designed to streamline online shopping, product management, and sales tracking. It supports multiple user roles — **Customers**, **Staff**, and **Admins** — each with tailored dashboards and workflows.

Built with **Flask**, **PostgreSQL**, and **Bootstrap**, the system includes:

- Customer registration and login
- Product browsing and purchasing
- Staff sales tracking and dashboard
- Admin management of users, products, roles, and account balances
- Supabase integration for profile image storage
- Real-time feedback with toast notifications and validation

---

## 🚀 How to Use the System

### 1. Access the Homepage

Visit the root URL (e.g., `http://127.0.0.1:5000/`) to access the homepage. From here, you can:

- View products
- Register or log in
- Navigate to staff or admin dashboards

---

## 👤 Customer Workflow

### Register

- Click **Register**
- Fill in:
  - Email
  - Username
  - Phone number
  - Password
- Submit the form

### Login

- Click **Login**
- Enter your registered **email** and **password**
- After login, you can:
  - Browse products
  - View your account settings
  - Reset your password
  - View login activity

---

## 🧑‍💼 Staff Workflow

### Login

- Click **Staff Login**
- Use credentials provided by the admin (e.g., `salesman1@gmail.com`)
- After login, you can:
  - View products
  - Start selling
  - View sales summary
  - Set sales date
  - Track total sales

---

## 🛠️ Admin Workflow

### Login

- Click **Admin Login**
- Use admin credentials (e.g., `admin@gmail.com`)
- After login, you can:
  - Manage customers
  - Add/view products
  - Edit your profile
  - Manage customer orders
  - Create/manage staff roles
  - View account balance breakdowns

---

## 🔐 Credentials Format

| Role     | Example Email           | Password         |
|----------|-------------------------|------------------|
| Customer | `customer1@gmail.com`   | `yourpassword`   |
| Staff    | `salesman1@gmail.com`   | `yourpassword`   |
| Admin    | `admin@gmail.com`       | `yourpassword`   |

> Admins must create staff accounts and assign roles before staff can log in.

---

## 🧾 Features

- ✅ Responsive UI with Bootstrap
- ✅ Background images for visual clarity
- ✅ Secure password hashing with bcrypt
- ✅ Role-based access control
- ✅ Real-time sales tracking
- ✅ Supabase image uploads
- ✅ Toast feedback and form validation

---

## 🛠️ Tech Stack

- **Backend**: Flask, SQLAlchemy, PostgreSQL
- **Frontend**: HTML, CSS, Bootstrap, JavaScript
- **Storage**: Supabase (for profile images)
- **Deployment**: Render / GitHub Actions

---

## ⚙️ Setup Instructions

### Step 1: Clone the repository

```bash
git clone https://github.com/your-username/supermarket-system.git
cd supermarket-system

 #step 2 activate a virtual enevironment
 python -m venv venv

  # On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate

# step 3 install dependencies
pip install -r requirements.txt

#step 4 Configure environment variables
DATABASE_URL=postgresql://username:password@localhost:5432/your_database
SUPABASE_URL=https://your-supabase-url.supabase.co
SUPABASE_KEY=your-supabase-api-key

#step 6 run the system in the terminal
python app.py