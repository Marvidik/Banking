"""
URL configuration for Banking project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path
from authentication import views 
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns


urlpatterns = [
    path("admin/", admin.site.urls),
    path("login/",views.login,name="login"),
    path("register/",views.register,name="register"),
    path("transactions/<id>/",views.get_transactions, name="transaction"),
    path("make-transactions/<id>",views.make_transaction, name="maketransaction"),
    path("confirm-pin/",views.confirm_pin,name="Confirm-Pin"),
    path("profile/<id>",views.get_profile,name="getprofile"),
    path("create-profile/",views.create_profile,name="create-profile"),
    path('security-answers/', views.create_security_answers, name='create_security_answers'),
    path('check-security-answer/<id>', views.check_security_answer, name='check_security_answer'),
    path("create-pin/",views.create_transaction_pin,name="trans-pin"),
    path("check-pin/<id>",views.check_transaction_pin,name="check"),
    path('check-imf-code/', views.check_imf_code, name='check_imf_code'),
    path('check-ipn-code/', views.check_ipn_code, name='check_ipn_code'),
    path('check-bank-transfer-code/', views.check_bank_transfer_code, name='check_bank_transfer_code'),

    path('password/reset/', views.password_reset, name='password_reset'),
    path('password/reset/confirm', views.password_reset_confirm, name='password_reset_confirm'),
    path("otp/",views.confirm_otp,name="confirm_otp"),
    
]


# Serve static files during development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)


urlpatterns+= staticfiles_urlpatterns()