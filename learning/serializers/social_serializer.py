from rest_framework import serializers
from learning.models import SocialPost, SocialComment, SocialReaction


class SocialCommentSerializer(serializers.ModelSerializer):
    author_email    = serializers.EmailField(source='author.email', read_only=True)
    author_username = serializers.CharField(source='author.username', read_only=True)

    class Meta:
        model  = SocialComment
        fields = ['id', 'post', 'author', 'author_email', 'author_username', 'body', 'created_at']
        read_only_fields = ['author', 'created_at']

    def create(self, validated_data):
        validated_data['author'] = self.context['request'].user
        return super().create(validated_data)


class SocialReactionSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model  = SocialReaction
        fields = ['id', 'user', 'user_email', 'post', 'reaction', 'created_at']
        read_only_fields = ['user', 'created_at']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class SocialPostSerializer(serializers.ModelSerializer):
    author_email    = serializers.EmailField(source='author.email', read_only=True)
    author_username = serializers.CharField(source='author.username', read_only=True)
    post_type_display = serializers.CharField(source='get_post_type_display', read_only=True)
    comment_count   = serializers.SerializerMethodField()
    reaction_count  = serializers.SerializerMethodField()
    comments        = SocialCommentSerializer(many=True, read_only=True)

    class Meta:
        model  = SocialPost
        fields = ['id', 'author', 'author_email', 'author_username',
                  'post_type', 'post_type_display', 'content', 'image_url',
                  'is_public', 'comment_count', 'reaction_count',
                  'comments', 'created_at', 'updated_at']
        read_only_fields = ['author', 'created_at', 'updated_at']

    def get_comment_count(self, obj):
        return obj.comments.count()

    def get_reaction_count(self, obj):
        return obj.reactions.count()

    def create(self, validated_data):
        validated_data['author'] = self.context['request'].user
        return super().create(validated_data)
