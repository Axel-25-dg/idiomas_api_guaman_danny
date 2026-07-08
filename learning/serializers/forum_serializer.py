from rest_framework import serializers
from learning.models import ForumCategory, ForumThread, ForumPost, ForumReaction, ForumReport


class ForumCategorySerializer(serializers.ModelSerializer):
    thread_count = serializers.SerializerMethodField()

    class Meta:
        model  = ForumCategory
        fields = ['id', 'name', 'description', 'icon', 'order', 'is_active', 'thread_count', 'created_at']

    def get_thread_count(self, obj):
        return obj.threads.count()


class ForumPostSerializer(serializers.ModelSerializer):
    author_email    = serializers.EmailField(source='author.email', read_only=True)
    author_username = serializers.CharField(source='author.username', read_only=True)
    reaction_count  = serializers.SerializerMethodField()

    class Meta:
        model  = ForumPost
        fields = ['id', 'thread', 'author', 'author_email', 'author_username',
                  'parent', 'body', 'is_deleted', 'reaction_count', 'created_at', 'updated_at']
        read_only_fields = ['author', 'is_deleted', 'created_at', 'updated_at']

    def get_reaction_count(self, obj):
        return obj.reactions.count()

    def create(self, validated_data):
        validated_data['author'] = self.context['request'].user
        return super().create(validated_data)


class ForumThreadSerializer(serializers.ModelSerializer):
    author_email    = serializers.EmailField(source='author.email', read_only=True)
    author_username = serializers.CharField(source='author.username', read_only=True)
    category_name   = serializers.CharField(source='category.name', read_only=True)
    post_count      = serializers.SerializerMethodField()

    class Meta:
        model  = ForumThread
        fields = ['id', 'category', 'category_name', 'author', 'author_email', 'author_username',
                  'title', 'body', 'is_pinned', 'is_closed', 'views',
                  'post_count', 'created_at', 'updated_at']
        read_only_fields = ['author', 'views', 'created_at', 'updated_at']

    def get_post_count(self, obj):
        return obj.posts.filter(is_deleted=False).count()

    def create(self, validated_data):
        validated_data['author'] = self.context['request'].user
        return super().create(validated_data)


class ForumReactionSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model  = ForumReaction
        fields = ['id', 'user', 'user_email', 'post', 'reaction', 'created_at']
        read_only_fields = ['user', 'created_at']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class ForumReportSerializer(serializers.ModelSerializer):
    reporter_email = serializers.EmailField(source='reporter.email', read_only=True)

    class Meta:
        model  = ForumReport
        fields = ['id', 'reporter', 'reporter_email', 'post', 'reason', 'status', 'created_at']
        read_only_fields = ['reporter', 'status', 'created_at']

    def create(self, validated_data):
        validated_data['reporter'] = self.context['request'].user
        return super().create(validated_data)
