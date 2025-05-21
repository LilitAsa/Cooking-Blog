from django.urls import path
from . import views
from .views import *
from django.conf.urls import include

urlpatterns = [
    path('', index, name='index'),
    path('about/', about, name='about'),
    path('blog/', blog, name='blog'),
    path('blog/<int:pk>/', blog_detail, name='blog_detail'),
    path('contact/', contact, name='contact'),
    path('menu/', menu, name='menu'),
    path('team/', team, name='team'),
    path('testimonials/', testimonials, name='testimonials'),
    path('feature/', feature, name='feature'),
    path('feature/<int:pk>/', feature_detail, name='feature_detail'),
    path('404/', error_404, name='error_404'),
    path('captcha/', include('captcha.urls')),
    path('newsletter/subscribe/', newsletter_subscribe, name='newsletter_subscribe'),
    path('send-newsletter/', send_newsletter, name='send_newsletter'),
    path('dishes/tag/<str:tag_slug>/', dishes_by_tag, name='dishes_by_tag'),
    path('dish/<int:pk>/', dish_detail, name='dish_detail'),
]

handler404 = error_404

