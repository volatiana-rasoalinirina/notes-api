from rest_framework import serializers
from .models import Note


class NoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Note
        fields = ["id", "title", "content", "created_at", "updated_at", "creator"]
        read_only_fields = ["id", "created_at", "updated_at"]

class NoteSerializerV2(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source="creator.id")
    class Meta:
        model = Note
        fields = ["id", "title", "content", "created_at", "updated_at", "owner"]
        read_only_fields = ["id", "created_at", "updated_at"]