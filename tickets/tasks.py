import logging
from datetime import timedelta

from celery import shared_task
from django.utils import timezone
from django_tenants.utils import schema_context

from .models import Agent, Ticket

logger = logging.getLogger(__name__)


@shared_task
def notify_ticket_created(ticket_id, tenant_schema):
    with schema_context(tenant_schema):
        ticket = Ticket.objects.get(id=ticket_id)
        logger.info(
            "Ticket created notification sent for ticket_id=%s tenant_schema=%s title=%s created_by=%s",
            ticket.id,
            tenant_schema,
            ticket.title,
            ticket.created_by,
        )


@shared_task
def notify_ticket_assigned(ticket_id, agent_id, tenant_schema):
    with schema_context(tenant_schema):
        ticket = Ticket.objects.select_related("assigned_to__user").get(id=ticket_id)
        agent = Agent.objects.select_related("user").get(id=agent_id)
        logger.info(
            "Ticket assignment notification sent for ticket_id=%s agent_id=%s tenant_schema=%s agent=%s",
            ticket.id,
            agent.id,
            tenant_schema,
            agent.user.username,
        )


@shared_task
def auto_close_stale_tickets(tenant_schema):
    with schema_context(tenant_schema):
        stale_before = timezone.now() - timedelta(days=7)
        closed_count = Ticket.objects.filter(
            status="open",
            created_at__lt=stale_before,
        ).update(status="closed", updated_at=timezone.now())

        logger.info(
            "Auto-closed %s stale tickets for tenant_schema=%s",
            closed_count,
            tenant_schema,
        )
        return closed_count
