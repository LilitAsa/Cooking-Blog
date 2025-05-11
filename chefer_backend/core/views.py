from django.shortcuts import render
from django.core.paginator import Paginator
from django.core.cache import cache
from .models import *
  

def index(request):
    features = Feature.objects.all()
    testimonials = Testimonial.objects.all()
    team_members = TeamMember.objects.all()
    menus = Menu.objects.prefetch_related('dishes').all()
    blog_posts = BlogPost.objects.all()[:3]  
    

    context = {
        'features': features,
        'testimonials': testimonials,
        'team_members': team_members,
        'menus': menus,
        'blog_posts': blog_posts,
        'page_title': 'Home',
        'page_subtitle': 'Welcome to Chefer',
    }
    return render(request, 'index.html', context)


def menu(request):
    categories = cache.get('categories')
    if not categories:
        categories = Category.objects.prefetch_related('menu_items').all()
        cache.set('categories', categories, 60 * 15)  # Кэш на 15 минут
    features = Feature.objects.all()  
    paginator = Paginator(categories, 5) 
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    
    context = {
        'title': 'Menu',  
        'page_title': 'Menu',
        'name': 'Our Menu',
        'description' : "Explore our delicious menu",
        'categories': page_obj,
        'features': features,
        
    }
    return render(request, 'menu.html', context)


def blog(request):
    blog_posts = BlogPost.objects.all()

    context = {
        'blog_posts': blog_posts,
    }
    return render(request, 'blog.html', context)


def team(request):
    team_members = TeamMember.objects.all()

    context = {
        'team_members': team_members,
    }
    return render(request, 'team.html', context)


def testimonials(request):
    testimonials = Testimonial.objects.all()

    context = {
        'testimonials': testimonials,
    }
    return render(request, 'testimonials.html', context)

def about(request):
    chefs = Chef.objects.all()

    context = {
        'page_title': 'About',
        'chefs': chefs,
    }
    return render(request, 'about.html', context)

def contact(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')
        
    context = {
        'page_title': 'Contact Us',
        'page_subtitle': 'Get in touch with us',
    }
    if name and email and message:
        print(f"Name: {name}, Email: {email}, Message: {message}")
        context['success_message'] = 'Your message has been sent successfully!'
    else:
        context['error_message'] = 'Please fill in all fields.'
    return render(request, 'contact.html', context)

def feature_detail(request, pk):
    feature = Feature.objects.get(pk=pk)
    context = {
        'feature': feature,
    }
    return render(request, 'feature_detail.html', context)