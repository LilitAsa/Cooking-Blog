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
  
