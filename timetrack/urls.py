# urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('save_time_logs/', views.insert_time_data, name='save_time_logs'),
    path('track_hours/', views.track_hours, name='track_hours'),
    path('get-customer-names/', views.get_customer_names, name='get_customer_names'),
    path('get-projects-by-company/', views.get_projects_by_company, name='get_projects_by_company'),
]
