from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django.db.models import Count
from .models import Ticket, Comment, Agent
from django.core.cache import cache
from django_tenants.utils import connection
from rest_framework.response import Response
from .serializers import (
    TicketListSerializer,
    TicketDetailSerializer,
    CommentSerializer,
    AgentSerializer,
)

class TicketViewSet(viewsets.ModelViewSet):

    queryset = Ticket.objects.all().order_by("-created_at")

    permission_classes = [AllowAny]

    filterset_fields = ["status", "priority", "assigned_to"]

    search_fields = ["title", "created_by"]

    ordering_fields = ["created_at", "priority"]

    def get_serializer_class(self):

        if self.action == "list":
            return TicketListSerializer

        return TicketDetailSerializer

    def perform_create(self, serializer):
        serializer.save()

    @action(detail=True, methods=["post"])
    def assign(self, request, pk=None):

        ticket = self.get_object()

        agent_id = request.data.get("agent_id")

        if not agent_id:
            return Response(
                {"error": "agent_id is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            agent = Agent.objects.get(id=agent_id)

        except Agent.DoesNotExist:
            return Response(
                {"error": "Agent not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        ticket.assigned_to = agent
        ticket.save()
        
        # Celery trigger
        return Response(
            {"message": "Ticket assigned successfully"}
        )

    @action(detail=False, methods=["get"])
    def stats(self, request):
        # Redis implementation for cahing
        cache_key= "ticket_stats"
        
        cached_data = cache.get(cache_key)
        
        if cached_data:
            return Response({
                "source": "redis-cache",
                "data": cached_data
            })
            
        
        open_count = Ticket.objects.filter(status="open").count()
        resolved_count = Ticket.objects.filter(status="resolved").count()
        data={
            "open" : open_count,
            "resolved": resolved_count
        }

        cache.set(cache_key, data, timeout=300)

        return Response({
            "source": "db",
            "data": data
        })
        
        
class CommentViewSet(viewsets.ModelViewSet):

    serializer_class = CommentSerializer

    permission_classes = [AllowAny]

    queryset = Comment.objects.all().order_by("-created_at")

    def get_queryset(self):

        queryset = super().get_queryset()

        ticket_id = self.request.query_params.get("ticket")

        if ticket_id:
            queryset = queryset.filter(ticket_id=ticket_id)

        return queryset


class AgentViewSet(viewsets.ReadOnlyModelViewSet):

    queryset = Agent.objects.select_related("user").all()
    serializer_class = AgentSerializer
    permission_classes = [IsAuthenticated]

    def list(self, request, *args, **kwargs):

        schema_name = connection.schema_name
        cache_key = f"agents:{schema_name}"

        cached_data = cache.get(cache_key)

        if cached_data:
            return Response({
                "source": "redis-cache",
                "data": cached_data
            })

        serializer = self.get_serializer(self.get_queryset(), many=True)

        cache.set(cache_key, serializer.data, timeout=300)

        return Response({
            "source": "database",
            "data": serializer.data
        })
