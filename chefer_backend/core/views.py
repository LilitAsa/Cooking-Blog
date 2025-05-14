from django.shortcuts import render
from django.core.paginator import Paginator
from django.core.cache import cache
from django.core.mail import send_mail
from django.conf import settings
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from typing import Dict, List, Optional, Any
from .models import *
import logging

# Настройка логгера
logger = logging.getLogger(__name__)

# Константы для валидации
MIN_NAME_LENGTH = 2
MIN_SUBJECT_LENGTH = 5
MIN_MESSAGE_LENGTH = 10

# Константы для сообщений
ERROR_MESSAGES = {
    'name_required': 'Name is required',
    'name_too_short': f'Name must be at least {MIN_NAME_LENGTH} characters long',
    'email_required': 'Email is required',
    'email_invalid': 'Please enter a valid email address',
    'subject_required': 'Subject is required',
    'subject_too_short': f'Subject must be at least {MIN_SUBJECT_LENGTH} characters long',
    'message_required': 'Message is required',
    'message_too_short': f'Message must be at least {MIN_MESSAGE_LENGTH} characters long',
    'save_error': 'Sorry, there was an error processing your message. Please try again later.',
    'email_error': 'Message saved but there was an error sending emails.',
    'success': 'Your message has been sent successfully!',
}

# Константы для email
EMAIL_TEMPLATES = {
    'admin_subject': 'New Contact Message: {subject}',
    'admin_message': '''
    New message from website contact form:
    
    Name: {name}
    Email: {email}
    Subject: {subject}
    
    Message:
    {message}
    ''',
    'user_subject': 'Thank you for contacting us',
    'user_message': '''
    Dear {name},
    
    Thank you for contacting us. We have received your message and will get back to you soon.
    
    Your message:
    {message}
    
    Best regards,
    Chefer Team
    ''',
}

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


def validate_contact_form_data(name: str, email: str, subject: str, message: str) -> List[str]:
    """
    Валидация данных формы контактов
    
    Args:
        name: Имя отправителя
        email: Email отправителя
        subject: Тема сообщения
        message: Текст сообщения
        
    Returns:
        List[str]: Список ошибок валидации
    """
    errors = []
    
    if not name:
        errors.append(ERROR_MESSAGES['name_required'])
    elif len(name) < MIN_NAME_LENGTH:
        errors.append(ERROR_MESSAGES['name_too_short'])
        
    if not email:
        errors.append(ERROR_MESSAGES['email_required'])
    else:
        try:
            validate_email(email)
        except ValidationError:
            errors.append(ERROR_MESSAGES['email_invalid'])
            
    if not subject:
        errors.append(ERROR_MESSAGES['subject_required'])
    elif len(subject) < MIN_SUBJECT_LENGTH:
        errors.append(ERROR_MESSAGES['subject_too_short'])
        
    if not message:
        errors.append(ERROR_MESSAGES['message_required'])
    elif len(message) < MIN_MESSAGE_LENGTH:
        errors.append(ERROR_MESSAGES['message_too_short'])
        
    return errors


def send_contact_emails(name: str, email: str, subject: str, message: str) -> bool:
    """
    Отправка email-уведомлений
    
    Args:
        name: Имя отправителя
        email: Email отправителя
        subject: Тема сообщения
        message: Текст сообщения
        
    Returns:
        bool: True если письма отправлены успешно, False в случае ошибки
    """
    from_email = settings.DEFAULT_FROM_EMAIL or 'noreply@example.com'
    admin_email = settings.ADMIN_EMAIL or 'admin@example.com'
    
    try:
        # Подготовка данных для писем
        admin_subject = EMAIL_TEMPLATES['admin_subject'].format(subject=subject)
        admin_message = EMAIL_TEMPLATES['admin_message'].format(
            name=name,
            email=email,
            subject=subject,
            message=message
        )
        
        user_subject = EMAIL_TEMPLATES['user_subject']
        user_message = EMAIL_TEMPLATES['user_message'].format(
            name=name,
            message=message
        )
        
        # Отправка письма администратору
        try:
            logger.info(f"Attempting to send admin notification to {admin_email}")
            send_mail(
                admin_subject,
                admin_message,
                from_email,
                [admin_email],
                fail_silently=False,  # Изменено на False для получения ошибок
            )
            logger.info(f"Admin notification sent successfully to {admin_email}")
        except Exception as e:
            logger.error(f"Failed to send admin notification: {str(e)}", exc_info=True)
            logger.error(f"Email settings: host={settings.EMAIL_HOST}, port={settings.EMAIL_PORT}, "
                        f"use_tls={settings.EMAIL_USE_TLS}, from_email={from_email}")
            return False
        
        # Отправка подтверждения пользователю
        try:
            logger.info(f"Attempting to send user confirmation to {email}")
            send_mail(
                user_subject,
                user_message,
                from_email,
                [email],
                fail_silently=False,  # Изменено на False для получения ошибок
            )
            logger.info(f"User confirmation sent successfully to {email}")
        except Exception as e:
            logger.error(f"Failed to send user confirmation: {str(e)}", exc_info=True)
            logger.error(f"Email settings: host={settings.EMAIL_HOST}, port={settings.EMAIL_PORT}, "
                        f"use_tls={settings.EMAIL_USE_TLS}, from_email={from_email}")
            return False
        
        return True
    except Exception as e:
        logger.error(f"Unexpected error in send_contact_emails: {str(e)}", exc_info=True)
        logger.error(f"Email settings: host={settings.EMAIL_HOST}, port={settings.EMAIL_PORT}, "
                    f"use_tls={settings.EMAIL_USE_TLS}, from_email={from_email}")
        return False


def contact(request) -> Any:
    """
    Представление для страницы контактов
    
    Args:
        request: HTTP запрос
        
    Returns:
        HttpResponse: Ответ с отрендеренным шаблоном
    """
    context: Dict[str, Any] = {
        'page_title': 'Contact Us',
        'page_subtitle': 'Get in touch with us',
    }
    
    if request.method == 'POST':
        logger.info("Received POST request to contact form")
        
        try:
            # Получение и очистка данных формы
            form_data = {
                'name': request.POST.get('name', '').strip(),
                'email': request.POST.get('email', '').strip(),
                'subject': request.POST.get('subject', '').strip(),
                'message': request.POST.get('message', '').strip(),
            }
            logger.info(f"Form data received: {form_data}")
            
            # Валидация данных
            errors = validate_contact_form_data(**form_data)
            
            if errors:
                logger.warning(f"Validation errors: {errors}")
                context['error_message'] = 'Please correct the following errors:'
                context['form_errors'] = errors
                context['form_data'] = form_data
                return render(request, 'contact.html', context)
            
            # Сохранение сообщения в базу данных
            try:
                contact_message = ContactMessage.objects.create(**form_data)
                logger.info(f"Message saved to database with ID: {contact_message.id}")
            except Exception as e:
                logger.error(f"Database error: {str(e)}", exc_info=True)
                context['error_message'] = ERROR_MESSAGES['save_error']
                context['form_data'] = form_data
                return render(request, 'contact.html', context)
            
            # Отправка email-уведомлений
            try:
                if send_contact_emails(**form_data):
                    logger.info(f"Emails sent successfully for message ID: {contact_message.id}")
                    context['success_message'] = ERROR_MESSAGES['success']
                else:
                    logger.warning(f"Email sending failed for message ID: {contact_message.id}")
                    context['error_message'] = ERROR_MESSAGES['email_error']
                    # Сохраняем информацию об ошибке в базе данных
                    contact_message.is_read = False
                    contact_message.save()
            except Exception as e:
                logger.error(f"Email sending error: {str(e)}", exc_info=True)
                context['error_message'] = ERROR_MESSAGES['email_error']
                # Сохраняем информацию об ошибке в базе данных
                contact_message.is_read = False
                contact_message.save()
                
        except Exception as e:
            logger.error(f"Unexpected error in contact view: {str(e)}", exc_info=True)
            context['error_message'] = ERROR_MESSAGES['save_error']
            # Сохраняем данные формы для повторной отправки
            if 'form_data' in locals():
                context['form_data'] = form_data
            
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
    context = {
        'page_title': '404',
        'page_subtitle': 'Page not found',
        'error_message': 'The page you are looking for does not exist.',
    }   
    
    return render(request, '404.html', context)


def blog_detail(request, pk):
    post = BlogPost.objects.get(pk=pk)
    blog_posts = get_cached_data(BlogPost, 'blog_posts')
    context = {
        'post': post,
        'blog_posts': blog_posts,
        'page_title': post.title,
    }
    return render(request, 'blog_detail.html', context)

