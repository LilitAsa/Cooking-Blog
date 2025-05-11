from .models import InstagramImage

def instagram_context(request):
    instagram_images = InstagramImage.objects.all()[:8]
    instagram_link = "https://www.instagram.com/"
    return {
        'instagram_images': instagram_images,
        'instagram_link': instagram_link,
    }