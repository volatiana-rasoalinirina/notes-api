from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated

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

    def perform_create(self, serializer):
        serializer.save(creator=self.request.user)
