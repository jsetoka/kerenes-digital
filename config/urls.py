from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

from django.contrib.auth import views as auth_views
from wagtail.admin import urls as wagtailadmin_urls
from wagtail.documents import urls as wagtaildocs_urls
from wagtail import urls as wagtail_urls


urlpatterns = [
    path("django-admin/", admin.site.urls),
    path("admin/", include(wagtailadmin_urls)),
    path("documents/", include(wagtaildocs_urls)),

    # ✅ logout forcé -> redirection
    path("accounts/logout/",
         auth_views.LogoutView.as_view(next_page="/"), name="logout"),
    path("accounts/", include("django.contrib.auth.urls")),
    path("library/", include("library.urls")),


    path("", include(wagtail_urls)),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
