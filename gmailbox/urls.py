# gmailbox/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('google/login', views.google_login, name='google_login'),
    path('google/callback', views.google_callback, name='google_callback'),
    path('inbox/', views.inbox, name='inbox'),
    path('message/<str:msg_id>/', views.message_detail, name='message_detail'),
    # exportación CSV
    path('logout/', views.logout_view, name='logout'),
    path('inbox/export.csv', views.export_csv, name='export_csv'),
]

