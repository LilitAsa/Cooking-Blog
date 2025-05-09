from django.shortcuts import render
from .models import Chef, Feature, Menu, Dish, BlogPost, Category, MenuItem, Testimonial, TeamMember

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
    }
    return render(request, 'index.html', context)


def menu(request):
    categories = Category.objects.prefetch_related('menu_items').all()

    context = {
        'categories': categories,
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
        'chefs': chefs,
    }
    return render(request, 'about.html', context)

def contact(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')
    return render(request, 'contact.html')