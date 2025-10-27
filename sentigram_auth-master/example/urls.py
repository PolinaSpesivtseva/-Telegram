from django.contrib import admin
from django.urls import include, path, re_path
from django.views.generic.base import TemplateView
from allauth.account.views import confirm_email
from django.conf.urls.static import static
from .views import CheckAuthView
from django.conf import settings
admin.autodiscover()
from django.urls import path, include
from example.demo.views import AlwaysRootLoginView

urlpatterns = [
    # ваш кастомный логин
    path(
        'accounts/login/',
        AlwaysRootLoginView.as_view(),
        name='account_login'
    ),
    path('accounts/check-auth/', CheckAuthView.as_view(), name='check-auth'),
    
    path('accounts/verify-email/<str:key>',
        confirm_email, name="account_confirm_email"),
    path("", TemplateView.as_view(template_name="index.html")),
    path("accounts/", include("allauth.urls")),
    path("accounts/profile/", TemplateView.as_view(template_name="profile.html")),
    path("admin/", admin.site.urls),
    path("i18n/", include("django.conf.urls.i18n")),
]
