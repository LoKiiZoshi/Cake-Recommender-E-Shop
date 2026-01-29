from django.conf import settings 
from django.urls import path,include
from .views import chatbot_view

urlpatterns = [
     path('chatbot',chatbot_view,name ='chatbot'),
]
