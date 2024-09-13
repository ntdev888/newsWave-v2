from rest_framework import serializers
from .models import Article

class ArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        # Ensure 'id' is included in the fields list
        fields = ['id', 'title', 'description', 'url', 'published_at', 'source_name', 'pictureUrl', 'topic']
