"""
URL configuration for backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path , include
from django.http import HttpResponse
from chatbot import views

def homepage(request):
    return HttpResponse("Bienvenue sur l'API Django 🎉")

urlpatterns = [
     path('', homepage),
    path('admin/', admin.site.urls),
    path('api/', include('chatbot.api_urls')),
     path('create-ticket/', views.create_ticket, name='create_ticket'),
     path('test-pdf/', views.test_pdf_reading, name='test_pdf'), 
    
    
]
