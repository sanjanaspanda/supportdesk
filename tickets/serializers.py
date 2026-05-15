from rest_framework import serializers
from .models import Ticket, Comment, Agent


class AgentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Agent
        fields = ["id", "user", "department"]


class CommentSerializer(serializers.ModelSerializer):

    author = AgentSerializer(read_only=True)

    class Meta:
        model = Comment
        fields = [
            "id",
            "ticket",
            "author",
            "body",
            "created_at",
        ]


class TicketListSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ticket
        fields = [
            "id",
            "title",
            "status",
            "priority",
            "created_by",
            "created_at",
        ]


class TicketDetailSerializer(serializers.ModelSerializer):

    assigned_to = AgentSerializer(read_only=True)

    comments = CommentSerializer(many=True, read_only=True)

    class Meta:
        model = Ticket
        fields = [
            "id",
            "title",
            "description",
            "status",
            "priority",
            "created_by",
            "assigned_to",
            "created_at",
            "updated_at",
            "comments",
        ]