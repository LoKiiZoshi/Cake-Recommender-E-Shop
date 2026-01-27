🎂 Smart Cake Shop – Django E-Commerce Project

A Django-based eCommerce web application for an online cake shop.
This project includes product management, shopping cart, recommendations, authentication, and admin dashboard, built with clean backend logic and modular app structure.

Designed for:

Python / Django Backend Developer Portfolio

Technical Interviews

Real-world Django practice

🚀 Features

User Authentication (Login / Register)

Product Listing & Details

Shopping Cart (Session-based)

Add / Remove / Update Cart Items

Cake Recommendation System

Admin Dashboard

Django Forms & Context Processors

Secure Django ORM usage

Modular App Architecture

🧱 Tech Stack

Backend: Python, Django

Frontend: HTML, CSS, Django Templates

Database: SQLite (default)

Auth: Django Authentication System

Version Control: Git, GitHub

📂 Project Structure
CakeShop/

├── accounts/              # User authentication
├── admin_dashboard/       # Admin-related features
├── chatbot/               # Chatbot logic (if enabled)
├── shop/                  # Core shop logic
│   ├── cart.py            # Cart functionality
│   ├── context_processors.py
│   ├── forms.py
│   ├── models.py
│   ├── recommendation.py # Product recommendations
│   ├── views.py
│   ├── urls.py

├── smart_cake_shop/       # Project settings
│
├── db.sqlite3
├── manage.py
├── requirements.txt
└── README.md

⚙️ Installation & Setup Guide

Follow these steps to run the project locally.

1️⃣ Clone the Repository
git clone
cd CakeShop

2️⃣ Create Virtual Environment
python -m venv venv


Activate it:

Windows

venv\Scripts\activate


Linux / macOS

source venv/bin/activate

3️⃣ Install Dependencies
pip install -r requirements.txt

4️⃣ Apply Migrations
python manage.py makemigrations
python manage.py migrate

5️⃣ Create Superuser
python manage.py createsuperuser

6️⃣ Run Development Server
python manage.py runserver


Open in browser:

http://127.0.0.1:8000/


Admin panel:

http://127.0.0.1:8000/admin/

🛒 Cart System (Important Feature)

Session-based cart

Add products with quantity

Update or remove items

Price handled using Decimal

Cart data stored securely in Django session

🎯 Recommendation System

Suggests related cakes/products

Improves user shopping experience

Demonstrates backend logic & data handling

🔐 Security

Django ORM prevents SQL Injection

CSRF protection enabled

Passwords stored as hashed values

Session-based cart handling

🧠 Developer Notes (Interview Ready)

This project demonstrates Django fundamentals such as session handling, cart logic, modular apps, ORM usage, context processors, and recommendation logic.

📈 Future Improvements

REST API using Django REST Framework

JWT Authentication

Payment Gateway Integration

Pagination & Filtering

Deployment (AWS / DigitalOcean)

PostgreSQL Database

⭐ Why This Project Matters

Real-world eCommerce logic

Clean backend architecture

Easy to explain in interviews

Strong portfolio project for Django backend roles

📄 License

This project is for educational and portfolio purposes.
