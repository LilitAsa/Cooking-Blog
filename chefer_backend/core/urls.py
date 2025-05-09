from django.urls import path
from . import views
from .views import *

urlpatterns = [
    path('', index, name='index'),
    path('about/', about, name='about'),
    path('blog/', blog, name='blog'),
    path('contact/', contact, name='contact'),
    path('menu/', menu, name='menu'),
    path('team/', team, name='team'),
    path('testimonials/', testimonials, name='testimonials'),
    path('feature/<int:pk>/', feature_detail, name='feature_detail'),
]