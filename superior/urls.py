# superior/urls.py (or whatever your app name is)

from django.urls import path
from . import views

urlpatterns = [
    # Dashboard
    path('dashboard/metrics/', views.dashboard_metrics, name='dashboard-metrics'),

    # User Management
    path('users/', views.list_users, name='list-users'),
    path('users/<int:user_id>/', views.user_detail, name='user-detail'),
    path('users/<int:user_id>/ban/', views.ban_unban_user, name='ban-unban-user'),

    # Transaction Management
    path('transactions/', views.list_transactions, name='list-transactions'),
    path('transactions/<int:transaction_id>/', views.transaction_detail, name='transaction-detail'),
    path('transactions/<int:transaction_id>/approve/', views.approve_transaction, name='approve-transaction'),

    path('manage/codes/', views.manage_codes,name="mans"),
    path('manage/login-pin/', views.manage_login_pin,name="manss"),
]
