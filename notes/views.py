from django.core.cache import cache
from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Note
from .permissions import IsOwnerOrReadOnly
from .serializers import NoteSerializer, NoteSerializerV2


class NoteViewSet(viewsets.ModelViewSet):
    queryset = Note.objects.all().order_by("-created_at")
    serializer_class = NoteSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["title", "content"]
    ordering_fields = ["created_at",]
    http_method_names = ["get", "post", "patch", "delete", "head", "options"]

    def get_serializer_class(self):
        if self.request.version == "v2":
            return NoteSerializerV2
        return NoteSerializer

    def list(self, request, *args, **kwargs):
        cached = cache.get(f"notes_list_{request.user.id}")
        if cached:
            return Response(cached)

        response = super().list(request, *args, **kwargs)
        cache.set(f"notes_list_{request.user.id}", response.data, timeout=300)
        return response

    def perform_create(self, serializer):
        serializer.save(creator=self.request.user)
        cache.delete(f"notes_list_{self.request.user.id}")

    def perform_update(self, serializer):
        serializer.save()
        cache.delete(f"notes_list_{self.request.user.id}")

    def perform_destroy(self, instance):
        instance.delete()
        cache.delete(f"notes_list_{self.request.user.id}")