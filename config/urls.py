from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

from django.contrib.auth import views as auth_views
from wagtail.admin import urls as wagtailadmin_urls
from wagtail.documents import urls as wagtaildocs_urls
from wagtail import urls as wagtail_urls
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect


class FrontLoginView(LoginView):
    def get_success_url(self):
        user = self.request.user
        if user.is_staff:
            return "/admin/"
        return "/"


urlpatterns = [
    path("django-admin/", admin.site.urls),
    path("admin/", include(wagtailadmin_urls)),
    path("documents/", include(wagtaildocs_urls)),

    # ✅ logout forcé -> redirection
    path("accounts/logout/",
         auth_views.LogoutView.as_view(next_page="/"), name="logout"),


    path("accounts/login/", FrontLoginView.as_view(
        template_name="registration/login.html"
    ), name="login"),

    path("accounts/logout/", auth_views.LogoutView.as_view(
        next_page="/"
    ), name="logout"),

    path("accounts/password_change/", auth_views.PasswordChangeView.as_view(
        template_name="registration/password_change_form.html",
        success_url="/"
    ), name="password_change"),

    path("accounts/password_change/done/", auth_views.PasswordChangeDoneView.as_view(
        template_name="registration/password_change_done.html",
    ), name="password_change_done"),


    path("accounts/", include("django.contrib.auth.urls")),
    path("library/", include("library.urls")),


    path("", include(wagtail_urls)),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
