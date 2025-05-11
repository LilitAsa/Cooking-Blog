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
  
