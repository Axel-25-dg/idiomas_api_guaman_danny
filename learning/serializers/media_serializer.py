"""
Serializers para MediaFile y MediaProgress
"""
from rest_framework import serializers
from learning.models import MediaFile, MediaProgress


class MediaFileSerializer(serializers.ModelSerializer):
    uploaded_by_email = serializers.EmailField(source='uploaded_by.email', read_only=True)
    file_url          = serializers.SerializerMethodField()
    thumbnail_url     = serializers.SerializerMethodField()
    percentage        = serializers.FloatField(read_only=True, default=0)

    class Meta:
        model  = MediaFile
        fields = [
            'id', 'uuid', 'original_name', 'file', 'mime_type', 'extension',
            'size', 'width', 'height', 'file_url', 'thumbnail_url',
            'storage_provider', 'status', 'uploaded_by', 'uploaded_by_email',
            'created_at', 'percentage', # <--- ¡Añadido aquí!
        ]
        read_only_fields = [
            'uuid', 'mime_type', 'extension', 'size', 'width', 'height',
            'checksum', 'status', 'uploaded_by', 'created_at',
        ]
    def get_file_url(self, obj):
        return obj.file_url

    def get_thumbnail_url(self, obj):
        return obj.thumbnail_url


class MediaProgressSerializer(serializers.ModelSerializer):
    lesson_title = serializers.CharField(source='lesson.title', read_only=True)
    percentage   = serializers.FloatField(read_only=True)

    class Meta:
        model  = MediaProgress
        fields = [
            'id', 'lesson', 'lesson_title',
            'position_sec', 'duration_sec', 'completed',
            'percentage', 'last_watched',
        ]
        read_only_fields = ['last_watched', 'percentage']
