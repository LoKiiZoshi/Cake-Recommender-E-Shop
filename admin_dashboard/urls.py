from django.urls import path
from . import views 
from django.conf.urls.static import static
from django.conf import settings

app_name = 'admin_dashboard'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    
    # Products
    path('products/', views.product_list, name='products'),
    path('products/create/', views.product_create, name='product_create'),
    path('products/<int:pk>/edit/', views.product_edit, name='product_edit'),
    path('products/<int:pk>/del2ete/', views.product_delete, name='product_delete'),
    
    # Categories
    path('categories/', views.category_list, name='categories'),
    path('categories/create/', views.category_create, name='category_create'),
    path('categories/<int:pk>/edit/', views.category_edit, name='category_edit'),
    path('categories/<int:pk>/delete/', views.category_delete, name='category_delete'),
    
    # Orders
    path('orders/', views.order_list, name='orders'),
    path('orders/<int:pk>/', views.order_detail, name='order_detail'),
    path('orders/<int:pk>/update-status/', views.order_status_update, name='order_status_update'),
    
    # Customers
    path('customers/', views.customer_list, name='customers'),
    path('customers/<int:pk>/', views.customer_detail, name='customer_detail'),
    
    
    
    # eSewa Payments
    path('payments/esewa/', views.esewa_payments, name='esewa_payments'),
    path('payments/esewa/<int:pk>/process/', views.process_esewa_payment, name='process_esewa_payment'),
    
    
]  + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
