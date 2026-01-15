from django.urls import path
from . import views
from django.conf.urls.static import static
from django.conf import settings


app_name = 'shop'

urlpatterns = [ 
               
               
    path('', views.home, name='home'),  
    
    
    
    
    # New pages
    path('categories/', views.categories_view, name='categories'),
    path('about/', views.about_view, name='about'),
    path('contact/', views.contact_view, name='contact'),
    
    
    
    path('shop/', views.shop_list, name='shop_list'),
    path('products/', views.product_list, name='product_list'),
    path('products/<int:id>/<slug:slug>/', views.product_detail, name='product_detail'),
    path('category/<slug:category_slug>/', views.product_list, name='product_list_by_category'),
    
    
    
    # Cart URLs
    path('cart/', views.cart_detail, name='cart_detail'),
    path('cart/add/<int:product_id>/', views.cart_add, name='cart_add'),
    path('cart/remove/<int:product_id>/', views.cart_remove, name='cart_remove'),
    
    
     
    # Checkout and Order URLs
    path('checkout/', views.order_create, name='checkout'),
    path('orders/', views.order_history, name='order_history'),
    path('orders/<int:order_id>/', views.order_detail, name='order_detail'),
    
    
    
    # eSewa Payment URLs
    path('payment/esewa/<int:order_id>/', views.esewa_payment, name='esewa_payment'),
    path('payment/esewa/success/', views.esewa_success, name='esewa_success'),
    path('payment/esewa/failure/', views.esewa_failure, name='esewa_failure'), 
    
    
    
    
    
    
   path('quick-view/<int:product_id>/', views.quick_view, name='quick_view'),
   
   
   
   
    path('contact/', views.contact_view, name='contact'),
    path('contact/ajax/', views.contact_ajax_view, name='contact_ajax'),
    
   
    
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
