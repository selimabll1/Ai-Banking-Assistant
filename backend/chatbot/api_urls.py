from django.urls import path
from . import views
from .views_form import form_start , form_peek , form_answer , form_pdf


urlpatterns = [
    path('register/', views.register_user),
    path('login/', views.login_user),
    path('messages/', views.message_list_create),
    path('form/start/', form_start, name='form_start'),
    path('form/peek/', form_peek),
    path('form/answer/', form_answer, name='form_answer'),
     path('form/pdf/<str:session_id>/', form_pdf),

  
]
