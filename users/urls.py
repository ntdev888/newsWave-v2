from django.urls import path
from .views import RegisterView, get_user_id, LoginView, LogoutView, UpdateSettingsView, UpdateTopicsView, UserDetailView
from rest_framework.authtoken.views import obtain_auth_token

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('api-token-auth/', obtain_auth_token, name='api_token_auth'),
    # path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('settings/', UpdateSettingsView.as_view(), name='update_settings'),
    path('topics/', UpdateTopicsView.as_view(), name='update_topics'),
    path('me/', UserDetailView.as_view(), name='user_detail'),
    path('get-user-id/', get_user_id, name='get-user-id'),
]
