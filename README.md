Project Overview🔆

The Cake Recommender System is a modern, intelligent platform designed for cake shops to provide customers with personalized recommendations, an interactive chatbot experience, and seamless online ordering with integrated payment options. This system leverages multiple recommendation algorithms to deliver tailored suggestions and enhance customer engagement.

It is designed to mimic a modern e-commerce cake shop where users can explore cakes, interact with an AI assistant, and complete purchases effortlessly via integrated payment gateways such as eSewa.
Key Features
User Features

Browse cakes with rich images and descriptions

Personalized cake recommendations based on 5 advanced algorithms

Interactive chatbot to assist in cake selection and queries

Add cakes to cart, checkout, and process payments securely

View order history and track deliveries

Option to redeem offers, coupons, or reward points

Admin Features

Manage cakes, categories, and inventory

Track user activity and order history

Monitor sales, ratings, and customer feedback

Configure discount campaigns, reward systems, and promotions

Recommendation Algorithms

The platform supports five types of recommendation strategies to enhance user experience:

Collaborative Filtering – Suggests cakes based on similar user behavior and interactions

Content-Based Filtering – Recommends cakes similar in features to ones the user liked

Hybrid Recommendation – Combines collaborative and content-based approaches for better accuracy

KMeans Clustering – Groups users or cakes into clusters for targeted suggestions

Popularity-Based – Highlights trending or highly-rated cakes

Technology Stack

Backend: Python, Django

Frontend: Django Templates, HTML5, CSS3, Bootstrap 5, JavaScript

Database: PostgreSQL / SQLite

APIs: Django REST Framework (optional for future expansion)

Payment Integration: eSewa, with secure transaction handling

AI/ML: Scikit-learn, Pandas, NumPy (for recommendation engine)


System Architecture
[ User Interface ] 
      │
      ▼
[ Django Templates & Chatbot Frontend ]
      │
      ▼
[ Django Backend ]
      │
      ├─ Recommender Engine (5 Algorithms)
      ├─ Order Management System
      ├─ Payment Gateway Integration (eSewa)
      └─ Admin Dashboard
      │
      ▼
[ Database (PostgreSQL / SQLite) ]



The system separates user-facing features from admin controls for clean scalability

Recommender engine is modular for easy addition of new algorithms

Payment and order systems are fully integrated for a seamless checkout experience


Payment Gateway Integration

Supports eSewa, Nepal’s most popular digital wallet

Secure transactions with automatic order status updates

Easy integration with front-end cart and checkout system



Future Enhancements

Add multi-language support for international customers

Integrate real-time chatbot with NLP for dynamic responses

Implement advanced analytics and dashboard for sales predictions

Expand to multi-store management for large cake shop chains

Introduce AI-based cake design suggestions based on user preferences



Folder Structure
CakeRecommender/
│
├── cake_shop/           # Main Django app
│   ├── templates/       # HTML templates for frontend
│   ├── static/          # CSS, JS, images
│   ├── models.py        # Database models
│   ├── views.py         # Views & API endpoints
│   ├── recommender.py   # Recommendation algorithms
│   └── urls.py          # App routing
│
├── CakeRecommender/
│   ├── settings.py      # Django project settings
│   ├── urls.py          # Project-level routes
│   └── wsgi.py          # WSGI entry point
│
├── requirements.txt     # Python dependencies
├── manage.py            # Django management utility
└── README.md            # Project documentation


Installation & Setup

Clone the repository:

git clone https://github.com/yourusername/CakeRecommender.git

Create a virtual environment:

python -m venv env
source env/bin/activate  # Linux/Mac
env\Scripts\activate     # Windows

Install dependencies:

pip install -r requirements.txt

Apply migrations:

python manage.py migrate

Run the development server:

python manage.py runserver

Access the platform at: http://127.0.0.1:8000/

Contributing

Fork the repository

Create a feature branch (git checkout -b feature/your-feature)

Commit your changes (git commit -m 'Add feature')

Push to the branch (git push origin feature/your-feature)

Create a Pull Request
Contact

Developer: Lokendra Joshi

GitHub: github.com/lokendrajoshi

LinkedIn: linkedin.com/in/lokendrajoshi
