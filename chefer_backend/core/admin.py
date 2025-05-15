from django.contrib import admin
from .models import *


admin.site.register(Chef)
admin.site.register(Menu)
admin.site.register(Dish)
admin.site.register(BlogPost)
admin.site.register(Category)
admin.site.register(MenuItem)
admin.site.register(Testimonial)

@admin.register(Feature)
class FeatureAdmin(admin.ModelAdmin):
    list_display = ('title', 'discount_title', 'discount')
    list_filter = ('discount_title',)
    search_fields = ('title', 'description')
    

@admin.register(InstagramImage)
class InstagramImageAdmin(admin.ModelAdmin):
    list_display = ('id', 'image', 'link', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('id',)
    ordering = ('-created_at',)
  

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'subject', 'created_at', 'is_read')
    list_filter = ('is_read', 'created_at')
    search_fields = ('name', 'email', 'subject', 'message')
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)
  
  
@admin.register(NewsletterSubscriber)
class NewsletterSubscriberAdmin(admin.ModelAdmin):
    list_display = ('email', 'subscribed_at')
    list_filter = ('subscribed_at',)
    search_fields = ('email',)
    ordering = ('-subscribed_at',)
    readonly_fields = ('subscribed_at',)
    list_per_page = 10
    list_max_show_all = 100


