from django.shortcuts import render
from django.core.paginator import Paginator
from django.core.cache import cache
from django.core.mail import send_mail
from django.conf import settings
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
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
    chefs = get_cached_data(Chef, 'chefs')
    
    context = {
        'team_members': team_members,
        'chefs': chefs,
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
    context = {
        'page_title': 'Contact Us',
        'page_subtitle': 'Get in touch with us',
    }
    
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        subject = request.POST.get('subject', '').strip()
        message = request.POST.get('message', '').strip()
        
        # Validation
        errors = []
        
        if not name:
            errors.append('Name is required')
        elif len(name) < 2:
            errors.append('Name must be at least 2 characters long')
            
        if not email:
            errors.append('Email is required')
        else:
            try:
                validate_email(email)
            except ValidationError:
                errors.append('Please enter a valid email address')
                
        if not subject:
            errors.append('Subject is required')
        elif len(subject) < 5:
            errors.append('Subject must be at least 5 characters long')
            
        if not message:
            errors.append('Message is required')
        elif len(message) < 10:
            errors.append('Message must be at least 10 characters long')
        
        if not errors:
            try:
                # Save to database
                contact_message = ContactMessage.objects.create(
                    name=name,
                    email=email,
                    subject=subject,
                    message=message
                )
                
                # Send email notification
                email_subject = f'New Contact Message: {subject}'
                email_message = f'''
                New message from website contact form:
                
                Name: {name}
                Email: {email}
                Subject: {subject}
                
                Message:
                {message}
                '''
                
                # Send email to admin
                send_mail(
                    email_subject,
                    email_message,
                    settings.DEFAULT_FROM_EMAIL,
                    [settings.ADMIN_EMAIL],
                    fail_silently=False,
                )
                
                # Send confirmation email to user
                user_email_subject = 'Thank you for contacting us'
                user_email_message = f'''
                Dear {name},
                
                Thank you for contacting us. We have received your message and will get back to you soon.
                
                Your message:
                {message}
                
                Best regards,
                Chefer Team
                '''
                
                send_mail(
                    user_email_subject,
                    user_email_message,
                    settings.DEFAULT_FROM_EMAIL,
                    [email],
                    fail_silently=False,
                )
                
                context['success_message'] = 'Your message has been sent successfully!'
            except Exception as e:
                context['error_message'] = 'Sorry, there was an error sending your message. Please try again later.'
                print(f"Error processing message: {e}")
        else:
            context['error_message'] = 'Please correct the following errors:'
            context['form_errors'] = errors
            # Preserve form data
            context['form_data'] = {
                'name': name,
                'email': email,
                'subject': subject,
                'message': message
            }
            
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
