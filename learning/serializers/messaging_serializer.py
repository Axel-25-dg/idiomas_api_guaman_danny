from rest_framework import serializers
from learning.models import MessageThread, Message, MessageAttachment


class MessageAttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model  = MessageAttachment
        fields = ['id', 'file_url', 'attachment_type', 'filename', 'created_at']
        read_only_fields = ['created_at']


class MessageSerializer(serializers.ModelSerializer):
    sender_email = serializers.EmailField(source='sender.email', read_only=True)
    attachments  = MessageAttachmentSerializer(many=True, read_only=True)

    class Meta:
        model  = Message
        fields = ['id', 'thread', 'sender', 'sender_email', 'body',
                  'is_read', 'read_at', 'attachments', 'created_at']
        read_only_fields = ['sender', 'is_read', 'read_at', 'created_at']

    def create(self, validated_data):
        validated_data['sender'] = self.context['request'].user
        return super().create(validated_data)


class MessageThreadSerializer(serializers.ModelSerializer):
    last_message    = serializers.SerializerMethodField()
    unread_count    = serializers.SerializerMethodField()
    participants_info = serializers.SerializerMethodField()

    class Meta:
        model  = MessageThread
        fields = ['id', 'subject', 'participants', 'participants_info',
                  'last_message', 'unread_count', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']

    def get_last_message(self, obj):
        msg = obj.messages.order_by('-created_at').first()
        if msg:
            return {'body': msg.body[:100], 'sender': msg.sender.email, 'created_at': msg.created_at}
        return None

    def get_unread_count(self, obj):
        user = self.context['request'].user
        return obj.messages.filter(is_read=False).exclude(sender=user).count()

    def get_participants_info(self, obj):
        return [{'id': p.id, 'email': p.email, 'username': p.username}
                for p in obj.participants.all()]
