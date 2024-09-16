from django.urls import path
from . import views

# URL paths for news views
urlpatterns = [
    path('fetch-news/', views.fetch_and_store_articles),
    path('fetch-articles/', views.populate_article_content),
    path('test/', views.test_endpoint),
    path('articles/', views.get_articles),
    path('articles-random/', views.get_random_articles),
]