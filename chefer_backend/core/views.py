from django.shortcuts import render
from django.core.paginator import Paginator
from django.core.cache import cache
from .models import *
  

def get_cached_data(model_class, cache_key, limit=None, **kwargs):
    """
    Универсальная функция для получения кэшированных данных
    
    Args:
        model_class: Класс модели Django
        cache_key: Ключ для кэша
        limit: Ограничение количества записей (опционально)
        **kwargs: Дополнительные параметры для фильтрации
    """
    full_cache_key = f"{cache_key}_{limit}" if limit else cache_key
    data = cache.get(full_cache_key)
    
    if not data:
        data = model_class.objects.filter(**kwargs)
        if limit:
            data = data[:limit]
        cache.set(full_cache_key, data, 60 * 15)  # Кэш на 15 минут
    
    return data


def index(request):
    features = get_cached_data(Feature, 'features')
    testimonials = get_cached_data(Testimonial, 'testimonials')
    team_members = get_cached_data(TeamMember, 'team_members')
    menus = Menu.objects.prefetch_related('dishes').all()
    blog_posts = get_cached_data(BlogPost, 'blog_posts', limit=3)
    chefs = get_cached_data(Chef, 'chefs')
    categories = get_cached_data(Category, 'categories')
    
    context = {
        'features': features,
        'testimonials': testimonials,
        'team_members': team_members,
        'menus': menus,
        'blog_posts': blog_posts,
        'chefs': chefs,
        'categories': categories,
        'page_title': 'Home',
        'page_subtitle': 'Welcome to Chefer',
    }
    return render(request, 'index.html', context)


def menu(request):
    categories = get_cached_data(Category, 'categories')
    features = get_cached_data(Feature, 'features')
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
    context = {
        'blog_posts': get_cached_data(BlogPost, 'blog_posts', limit=3),
        'page_title': 'Blog',
    }
    return render(request, 'blog.html', context)


def team(request):
    team_members = get_cached_data(TeamMember, 'team_members')

    context = {
        'team_members': team_members,
        'page_title': 'Team',
    }
    return render(request, 'team.html', context)


def testimonials(request):
    testimonials = get_cached_data(Testimonial, 'testimonials')

    context = {
        'testimonials': testimonials,
        'page_title': 'Testimonials',
    }
    return render(request, 'testimonials.html', context)


def about(request):
    chefs = get_cached_data(Chef, 'chefs')
    features = get_cached_data(Feature, 'features')

    context = {
        'page_title': 'About',
        'chefs': chefs,
        'features': features,
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


def feature(request):
    features = get_cached_data(Feature, 'features')
    context = {
        'features': features,
        'page_title': 'Features',
    }
    return render(request, 'feature.html', context)


def feature_detail(request, pk):
    feature = Feature.objects.get(pk=pk)
    context = {
        'feature': feature,
    }
    return render(request, 'feature_detail.html', context)


def error_404(request, exception):
    return render(request, '404.html', {})


def blog_detail(request, pk):
    post = BlogPost.objects.get(pk=pk)
    blog_posts = get_cached_data(BlogPost, 'blog_posts')
    context = {
        'post': post,
        'blog_posts': blog_posts,
        'page_title': post.title,
    }
    return render(request, 'blog_detail.html', context)
