from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from .models import Blog

class BlogSitemap(Sitemap):
    changefreq = "weekly"  # How often the page is updated
    priority = 0.8  # Higher value means more important (0.0 to 1.0)

    def items(self):
        return Blog.objects.filter(is_public=True)  # Only show public blogs

    def lastmod(self, obj):
        return obj.updated_at  # Use the last updated date of the blog

    def location(self, obj):
        return reverse('blog_detail', args=[obj.slug])  # Using slug for SEO-friendly URLs

