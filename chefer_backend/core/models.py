from django.db import models

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

    def __str__(self):
        return self.title


class Menu(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Dish(models.Model):
    menu = models.ForeignKey(Menu, related_name='dishes', on_delete=models.CASCADE)
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

    def __str__(self):
        return self.title


class Category(models.Model):
    name = models.CharField(max_length=50)

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name


class MenuItem(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='menu_items')
    title = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=6, decimal_places=2)
    image = models.ImageField(upload_to='menu_images/')
    available = models.BooleanField(default=True)

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