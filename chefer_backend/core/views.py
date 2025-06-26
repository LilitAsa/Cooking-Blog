from django.shortcuts import get_object_or_404, redirect, render
from django import forms
from django.core.paginator import Paginator
from django.core.cache import cache
from django.core.mail import send_mail
from django.conf import settings
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from typing import Dict, List, Optional, Any
from .models import *
import logging
from django.http import HttpResponse
from django.views.decorators.http import require_http_methods
from django.utils.translation import gettext_lazy as _
from captcha.fields import CaptchaField
from .forms import *
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.db.models import Prefetch, Q

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
  
def get_menu_context(request):
    menus = Menu.objects.all()
    selected_menu_id = request.GET.get('menu')
    selected_menu = get_object_or_404(Menu, id=selected_menu_id) if selected_menu_id else menus.first()

    filtered_menu_items = Prefetch(
        'menu_items',
        queryset=MenuItem.objects.filter(dish__menu=selected_menu),
        to_attr='filtered_items'
    )
    features = get_cached_data(Feature, 'features')

    categories = Category.objects.filter(
        menu_items__dish__menu=selected_menu
    ).distinct().prefetch_related(
        filtered_menu_items,
        'menu_items__dish',
        'menu_items__dish__tags'
    ).order_by('name')

    paginator = Paginator(categories, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return {
        'categories': page_obj,
        'features': features,
        'menus': menus,
        'selected_menu': selected_menu,
    }

def index(request):
    features = get_cached_data(Feature, 'features')
    testimonials = get_cached_data(Testimonial, 'testimonials')
    team_members = get_cached_data(TeamMember, 'team_members')
    blog_posts = get_cached_data(BlogPost, 'blog_posts', limit=3)
    chefs = get_cached_data(Chef, 'chefs')
    categories = get_cached_data(Category, 'categories')
    
    menus = Menu.objects.all()
    selected_menu = menus.first()
    
    categories_for_index_menu = Category.objects.filter(
        menu_items__dish__menu=selected_menu
    ).distinct().prefetch_related(
        Prefetch('menu_items',
                 queryset=MenuItem.objects.filter(dish__menu=selected_menu),
                 to_attr='filtered_items'),
        'menu_items__dish',
        'menu_items__dish__tags'
    ).order_by('name')

    for category in categories_for_index_menu:
        if not hasattr(category, 'filtered_items') or not category.filtered_items:
            category.filtered_items = category.menu_items.all()

    context = {
        'features': features,
        'testimonials': testimonials,
        'team_members': team_members,
        'blog_posts': blog_posts,
        'chefs': chefs,
        'categories': categories_for_index_menu,
        'page_title': 'Home',
        'page_subtitle': 'Welcome to Chefer',
        'show_search': False,
        'menus': menus,
        'selected_menu': selected_menu,
        'name': 'Our Menu',
        'description': "Explore our delicious menu",
    }
    return render(request, 'index.html', context)


def menu(request):
    # Получаем список всех меню
    menus = Menu.objects.all()
    active_category_id = None 
    
    # Получаем ID активной категории из GET-параметра
    active_category_id = request.GET.get('category')
    if active_category_id:
        try:
            active_category = Category.objects.get(id=active_category_id)
        except Category.DoesNotExist:
            active_category = None
            

    # Определяем выбранное меню
    selected_menu_id = request.GET.get('menu')
    if selected_menu_id:
        selected_menu = get_object_or_404(Menu, id=selected_menu_id)
    else:
        selected_menu = menus.first()

    # Получаем поисковый запрос
    search_query = request.GET.get('search', '').strip()
    

    # Получаем категории, у которых есть блюда из выбранного меню
    categories = Category.objects.filter(
        menu_items__dish__menu=selected_menu
    ).distinct().prefetch_related(
        'menu_items__dish',
        'menu_items__dish__tags'
    ).order_by('name')

    # Пагинация
    paginator = Paginator(categories, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Для каждой категории фильтруем menu_items
    filtered_categories = []
    for category in page_obj:
        items = category.menu_items.filter(dish__menu=selected_menu)
        if search_query:
            items = items.filter(
                Q(dish__name__icontains=search_query) |
                Q(title__icontains=search_query) |
                Q(dish__description__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(category__name__icontains=search_query)
            )
        category.filtered_items = items
        if items.exists():
            filtered_categories.append(category)
        # Найдена первая категория с результатами — запомним её
        if active_category_id is None and items.exists():
            active_category_id = category.id

    context = {
        'title': 'Menu',
        'page_title': 'Menu',
        'name': 'Our Menu',
        'description': "Explore our delicious menu",
        'categories': filtered_categories,
        'features': get_cached_data(Feature, 'features'),
        'menus': menus,
        'selected_menu': selected_menu,
        'search_query': search_query,
        'show_search': True,
        'active_category_id': active_category_id or (filtered_categories[0].id if filtered_categories else None),
    }

    return render(request, 'menu.html', context)

def blog(request):
    blog_posts = get_cached_data(BlogPost, 'blog_posts')
    context = {
        'blog_posts': blog_posts,
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
        'form': ContactForm(),  # Добавляем форму в контекст
    }
    
    if request.method == 'POST':
        logger.info("Received POST request to contact form")
        form = ContactForm(request.POST)
        
        try:
            if not form.is_valid():
                logger.warning(f"Form validation errors: {form.errors}")
                context['error_message'] = 'Please correct the following errors:'
                context['form_errors'] = form.errors
                context['form'] = form
                return render(request, 'contact.html', context)
            
            # Получение и очистка данных формы
            form_data = {
                'name': form.cleaned_data['name'].strip(),
                'email': form.cleaned_data['email'].strip(),
                'subject': form.cleaned_data['subject'].strip(),
                'message': form.cleaned_data['message'].strip(),
            }
            logger.info(f"Form data received: {form_data}")
            
            # Сохранение сообщения в базу данных
            try:
                contact_message = ContactMessage.objects.create(**form_data)
                logger.info(f"Message saved to database with ID: {contact_message.id}")
            except Exception as e:
                logger.error(f"Database error: {str(e)}", exc_info=True)
                context['error_message'] = ERROR_MESSAGES['save_error']
                context['form'] = form
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
            context['form'] = form
            return render(request, 'contact.html', context)
            
    return render(request, 'contact.html', context)


def feature(request):
    features = get_cached_data(Feature, 'features')
    context = {
        'features': features,
        'page_title': 'Features',
    }
    return render(request, 'feature.html', context)


def feature_detail(request, pk):
    feature = get_object_or_404(Feature, pk=pk)
    
    context = {
        'feature': feature,
    }
    return render(request, 'feature_detail.html', context)


def error_404(request):
    context = {
        'page_title': '404',
        'page_subtitle': 'Page not found',
        'error_message': 'The page you are looking for does not exist.',
    }   
    
    return render(request, '404.html', context)


def blog_detail(request, pk):
    post = get_object_or_404(BlogPost, pk=pk)
    blog_posts = get_cached_data(BlogPost, 'blog_posts')
    comments = post.comments.filter(is_approved=True)
    
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.save()
            messages.success(request, 'Your comment has been submitted and is awaiting approval.')
            return redirect('blog_detail', pk=post.pk)
    else:
        form = CommentForm()
    
    context = {
        'post': post,
        'blog_posts': blog_posts,
        'comments': comments,
        'form': form,
        'page_title': post.title,
    }
    return render(request, 'blog_detail.html', context)


def newsletter_subscribe(request):
    if request.method == 'POST':
        form = NewsletterForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            NewsletterSubscriber.objects.get_or_create(email=email)
            return render(request, 'newsletter_success.html', {'email': email})
    else:
        form = NewsletterForm()
    return render(request, 'newsletter_form.html', {'form': form})

class NewsletterSendForm(forms.Form):
    subject = forms.CharField(max_length=200, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Subject'}))
    message = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Message', 'rows': 6}))

@staff_member_required
def send_newsletter(request):
    if request.method == 'POST':
        form = NewsletterSendForm(request.POST)
        if form.is_valid():
            subject = form.cleaned_data['subject']
            message = form.cleaned_data['message']
            from_email = settings.DEFAULT_FROM_EMAIL
            subscribers = NewsletterSubscriber.objects.values_list('email', flat=True)
            sent_count = 0
            for email in subscribers:
                send_mail(subject, message, from_email, [email], fail_silently=False)
                sent_count += 1
            messages.success(request, f'Newsletter sent to {sent_count} subscribers!')
            return redirect('send_newsletter')
    else:
        form = NewsletterSendForm()
    return render(request, 'send_newsletter.html', {'form': form})


def testimonials(request):
    testimonials = get_cached_data(Testimonial, 'testimonials')
    context = {
        'testimonials': testimonials,
        'page_title': 'Testimonials',
    }
    return render(request, 'testimonials.html', context)


def dishes_by_tag(request, tag_slug):
    tag = get_object_or_404(Tag, name=tag_slug)
    dishes = Dish.objects.filter(tags=tag).select_related('menu').prefetch_related('tags')
    features = get_cached_data(Feature, 'features')
    
    context = {
        'tag': tag,
        'dishes': dishes,
        'features': features,
        'page_title': f'Dishes - {tag.name}',
        'name': f'Dishes with tag "{tag.name}"',
        'description': 'Explore our delicious dishes',
    }
    return render(request, 'dishes_by_tag.html', context)


def dish_detail(request, pk):
    dish = get_object_or_404(Dish.objects.select_related('menu').prefetch_related('tags'), pk=pk)
    features = get_cached_data(Feature, 'features')
    
    context = {
        'dish': dish,
        'features': features,
        'page_title': dish.name,
        'name': dish.name,
        'description': dish.description,
    }
    return render(request, 'dish_detail.html', context)