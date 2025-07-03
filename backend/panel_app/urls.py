from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token
from . import views # Import views module

app_name = 'panel_app'

urlpatterns = [
    # --- Authentication ---
    path('login/', obtain_auth_token, name='api_token_auth'),
    # path('logout/', views.LogoutView.as_view(), name='api_logout'),

    # --- Customer Profile & Data ---
    path('profile/', views.UserDetailView.as_view(), name='user_profile'),
    path('profile/configs/', views.UserConfigListView.as_view(), name='user_config_list'),
    path('tutorials/', views.TutorialListView.as_view(), name='tutorial_list'),
    path('announcements/public/', views.PublicAnnouncementListView.as_view(), name='public_announcement_list'),
    path('announcements/faq/', views.FAQAnnouncementListView.as_view(), name='faq_announcement_list'),

    # --- Admin Section ---
    # Admin: User Management
    path('admin/users/', views.AdminUserListView.as_view(), name='admin_user_list'),
    path('admin/users/create/', views.AdminUserCreateView.as_view(), name='admin_user_create'),
    path('admin/users/<int:pk>/', views.AdminUserDetailView.as_view(), name='admin_user_detail'),

    # Admin: Support Staff Management
    path('admin/support-users/create/', views.SupportUserCreateView.as_view(), name='support_user_create'),

    # Admin: Announcement Management
    path('admin/announcements/', views.AdminAnnouncementListCreateView.as_view(), name='admin_announcement_list_create'),
    path('admin/announcements/<int:pk>/', views.AdminAnnouncementDetailView.as_view(), name='admin_announcement_detail'),

    # Admin: Server Management
    path('admin/servers/', views.AdminServerListCreateView.as_view(), name='admin_server_list_create'),
    path('admin/servers/<int:pk>/', views.AdminServerDetailView.as_view(), name='admin_server_detail'),
    path('admin/servers/<int:pk>/test_connection/', views.AdminServerTestConnectionView.as_view(), name='admin_server_test_connection'),

    # Admin: Manual Config Add
    path('admin/configs/add_manual/', views.AdminConfigManualCreateView.as_view(), name='admin_config_manual_add'),

    # Admin: Fuzzy search for XUI clients
    path('admin/xui-clients/search/', views.AdminXUIClientsSearchView.as_view(), name='admin_xui_clients_search'),
]
