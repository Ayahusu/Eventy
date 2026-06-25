from rest_framework import serializers
from ..models import Event, EventComment

class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = '__all__'
        read_only_fields = ['id', 'organizer', 'created_at', 'updated_at']

    def validate(self, data):
        if data.get("entry_fee", 0) < 0:
            raise serializers.ValidationError("Entry fee cannot be negative")
        return data

class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventComment
        fields = '__all__'
        read_only_fields = ['id', 'organizer', 'created_at', 'updated_at']
