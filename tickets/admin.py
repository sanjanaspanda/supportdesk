from django.contrib import admin
from .models import Ticket, Agent, Comment


@admin.register(Agent)
class AgentAdmin(admin.ModelAdmin):
    list_display = ("user", "department")
    search_fields = ("user__username", "department")


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "status",
        "priority",
        "created_by",
        "assigned_to",
        "created_at",
    )

    list_filter = (
        "status",
        "priority",
        "created_at",
    )

    search_fields = (
        "title",
        "created_by",
    )


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = (
        "ticket",
        "author",
        "created_at",
    )

    search_fields = (
        "ticket__title",
        "author__user__username",
    )

    list_filter = (
        "created_at",
    )