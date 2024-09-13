from django.shortcuts import render
from django.db import IntegrityError, transaction
from django.http import JsonResponse
from newsapi import NewsApiClient
from .models import Article
from rest_framework.response import Response
from django.utils.dateparse import parse_datetime
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from .serializers import ArticleSerializer
import random

news_topics = [
    "Politics",
    "Technology",
    "Business",
    "Health",
    "Entertainment",
    "Sports",
    "Science",
    "Environment",
    "Education",
    "Economy",
    "World News",
    "Travel",
    "Culture",
    "Fashion",
    "Lifestyle",
    "Food & Cooking",
    "Real Estate",
    "Automotive",
    "Crime",
    "Weather",
    "History",
    "Religion",
    "Celebrity",
    "Human Interest"
]

# Initialize the News API client
newsapi = NewsApiClient(api_key='cad07dc33d534c508a93ae9128e9d716')

# Helper function to get sources and domains
def get_sources_and_domains():
    all_sources = newsapi.get_sources()['sources']
    sources = []
    domains = []
    for e in all_sources:
        id = e['id']
        domain = e['url'].replace("http://", "").replace("https://", "").replace("www.", "")
        slash = domain.find('/')
        if slash != -1:
            domain = domain[:slash]
        sources.append(id)
        domains.append(domain)
    return sources, domains

# Django view for fetching and storing news articles
@csrf_exempt
def fetch_and_store_articles(request):
    if request.method == "POST":
        stored_articles = []

        for keyword in news_topics:
            sources, domains = get_sources_and_domains()

            # Fetch related news articles
            if len(sources) > 20 or len(domains) > 20:
                related_news = newsapi.get_everything(q=keyword, language='en', sort_by='relevancy')
            else:
                sources_str = ", ".join(sources)
                domains_str = ", ".join(domains)
                related_news = newsapi.get_everything(q=keyword, sources=sources_str, domains=domains_str, language='en', sort_by='relevancy')

            no_of_articles = min(related_news['totalResults'], 100)
            articles = related_news['articles'][:no_of_articles]

            # Process each article
            for article in articles:
                picture_url = article.get('urlToImage', '')

                # Skip the article if pictureUrl is None or empty
                if not picture_url:
                    print(f"Skipping article '{article['title']}' due to missing pictureUrl.")
                    continue

                try:
                    with transaction.atomic():  # Use atomic transaction to prevent database lock
                        article_obj, created = Article.objects.get_or_create(
                            title=article['title'],
                            url=article['url'],
                            defaults={
                                'description': article.get('description', ''),
                                'published_at': parse_datetime(article['publishedAt']),
                                'source_name': article['source']['name'],
                                'pictureUrl': picture_url,
                                'topic': keyword,
                            }
                        )

                        if created:
                            stored_articles.append(article_obj)

                except IntegrityError as e:
                    print(f"IntegrityError: Could not create article with title '{article['title']}' due to unique constraint: {e}")
                    # Optional: handle the specific case here, e.g., skip, update, or notify

        # Return the stored articles as JSON
        return JsonResponse({
            "message": f"{len(stored_articles)} articles fetched and stored successfully.",
            "articles": list(Article.objects.values())
        }, safe=False)

    else:
        return JsonResponse({"error": "POST request required."}, status=400)

# def get_articles(request):
#     print("Success")
#     if request.method == "GET":
#         # Get the topic from the request parameters
#         topic = request.GET.get("topic", "")
#         print(f"Topic:{topic}")

#         # Retrieve all articles of the given topic from the database
#         articles = Article.objects.filter(topic=topic)

#         # If there are fewer than 8 articles, return all of them
#         if len(articles) <= 8:
#             random_articles = list(articles)
#         else:
#             # Randomly select 8 articles
#             random_articles = random.sample(list(articles), 8)
#             print(random_articles[1])

#         # Convert the articles to a list of dictionaries to make them JSON serializable
#         articles_data = [
#             {   "id": article.id,
#                 "title": article.title,
#                 "url": article.url,
#                 "description": article.description,
#                 "published_at": article.published_at,
#                 "source_name": article.source_name,
#                 "pictureUrl": article.pictureUrl,
#                 "topic": article.topic
#             }
#             for article in random_articles
#         ]

#         # Return the selected articles as JSON
#         return JsonResponse(articles_data, safe=False)

#     else:
#         return JsonResponse({"error": "GET request required."}, status=400)
    
# def get_random_articles(request):
#     if request.method == "GET":
#         # Retrieve all articles from the database
#         articles = Article.objects.all()

#         # If there are fewer than 8 articles, return all of them
#         if len(articles) <= 8:
#             random_articles = list(articles)
#         else:
#             # Randomly select 8 articles
#             random_articles = random.sample(list(articles), 8)

#         # Convert the articles to a list of dictionaries to make them JSON serializable
#         articles_data = [
#             {
#                 "title": article.title,
#                 "url": article.url,
#                 "description": article.description,
#                 "published_at": article.published_at,
#                 "source_name": article.source_name,
#                 "pictureUrl": article.pictureUrl,
#                 "topic": article.topic
#             }
#             for article in random_articles
#         ]

#         # Return the selected articles as JSON
#         return JsonResponse(articles_data, safe=False)

#     else:
#         return JsonResponse({"error": "GET request required."}, status=400)


@api_view(['GET'])
def get_articles(request):
    print("Success")
    if request.method == "GET":
        # Get the topic from the request parameters
        topic = request.GET.get("topic", "")
        print(f"Topic: {topic}")

        # Retrieve all articles of the given topic from the database
        articles = Article.objects.filter(topic=topic)
        if len(articles) == 0:
            articles = Article.objects.all()

        # If there are fewer than 8 articles, return all of them
        if len(articles) <= 8:
            random_articles = list(articles)
        else:
            # Randomly select 8 articles
            random_articles = random.sample(list(articles), 8)
            print(random_articles[1])

        # Use the serializer to convert the articles to JSON serializable data
        serializer = ArticleSerializer(random_articles, many=True)

        # Return the serialized articles as JSON
        return Response(serializer.data)

    else:
        return JsonResponse({"error": "GET request required."}, status=400)


@api_view(['GET'])
def get_random_articles(request):
    if request.method == "GET":
        # Retrieve all articles from the database
        articles = Article.objects.all()

        # If there are fewer than 8 articles, return all of them
        if len(articles) <= 8:
            random_articles = list(articles)
        else:
            # Randomly select 8 articles
            random_articles = random.sample(list(articles), 8)

        # Use the serializer to convert the articles to JSON serializable data
        serializer = ArticleSerializer(random_articles, many=True)

        # Return the serialized articles as JSON
        return Response(serializer.data)

    else:
        return JsonResponse({"error": "GET request required."}, status=400)




# Endpoint testing
def test_endpoint(request):
    return JsonResponse({"message": "Endpoint Reached."}, status=200)

