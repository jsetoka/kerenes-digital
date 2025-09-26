from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("django-admin/", admin.site.urls),
    path("admin/", include("wagtail.admin.urls")),
    path("documents/", include("wagtail.documents.urls")),
    path("", include("wagtail.urls")),  # Wagtail page routing
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)