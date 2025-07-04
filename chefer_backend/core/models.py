import hashlib
from django.db import models
from django.contrib.auth.models import User

class Chef(models.Model):
    name = models.CharField(max_length=100)
    bio = models.TextField()
    profile_image = models.ImageField(upload_to='chefs/')
    social_twitter = models.URLField(blank=True, null=True)
    social_facebook = models.URLField(blank=True, null=True)
    social_linkedin = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.name


class Feature(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    image = models.ImageField(upload_to='features/')
    link = models.URLField(blank=True, null=True)  
    discount_title = models.CharField(max_length=200, blank=True, null=True)  
    discount = models.IntegerField(blank=True, null=True) 


    def __str__(self):
        return self.title


class Menu(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name

class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name
class Dish(models.Model):
    menu = models.ForeignKey(Menu, related_name='dishes', on_delete=models.CASCADE)
    tags = models.ManyToManyField(Tag, related_name='dishes')
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=6, decimal_places=2)
    image = models.ImageField(upload_to='dishes/')

    def __str__(self):
        return self.name


class BlogPost(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    image = models.ImageField(upload_to='blog/')
    created_at = models.DateTimeField(auto_now_add=True)
    author = models.CharField(max_length=100, default='Admin')

    def __str__(self):
        return self.title


class Category(models.Model):
    name = models.CharField(max_length=50)

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['name']

    def __str__(self):
        return self.name


class MenuItem(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='menu_items')
    dish = models.ForeignKey(Dish, on_delete=models.CASCADE, related_name='menu_items', null=True, blank=True)
    title = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=6, decimal_places=2)
    image = models.ImageField(upload_to='menu_images/')
    available = models.BooleanField(default=True)
    menu = models.ForeignKey(Menu, on_delete=models.CASCADE, related_name='menu_items', null=True, blank=True)

    def __str__(self):
        return f"{self.title} ({self.category.name})"


class Testimonial(models.Model):
    client_name = models.CharField(max_length=100)
    profession = models.CharField(max_length=100, blank=True, null=True)
    content = models.TextField()
    image = models.ImageField(upload_to='testimonials/')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.client_name


class TeamMember(models.Model):
    name = models.CharField(max_length=100)
    role = models.CharField(max_length=100)
    profile_image = models.ImageField(upload_to='team/')
    social_twitter = models.URLField(blank=True, null=True)
    social_facebook = models.URLField(blank=True, null=True)
    social_linkedin = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.name
    

class InstagramImage(models.Model):
    image = models.ImageField(upload_to='instagram/') 
    created_at = models.DateTimeField(auto_now_add=True) 
    link = models.URLField(blank=True, null=True)
    
    def __str__(self):
        return f"Instagram Image {self.id}"


class ContactMessage(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"Message from {self.name} - {self.subject}"

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Contact Message'
        verbose_name_plural = 'Contact Messages'
        

class NewsletterSubscriber(models.Model):
    email = models.EmailField(unique=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email
    

class Comment(models.Model):
    post = models.ForeignKey(BlogPost, on_delete=models.CASCADE, related_name='comments')
    name = models.CharField(max_length=100)
    email = models.EmailField()
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_approved = models.BooleanField(default=False)
    
    def get_gravatar_url(self, size=50):
        email = self.email.strip().lower().encode('utf-8')
        hash = hashlib.md5(email).hexdigest()
        return f"https://www.gravatar.com/avatar/{hash}?s={size}&d=identicon"

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'Comment by {self.name} on {self.post.title}'
    