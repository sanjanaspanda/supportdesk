from django.core.management.base import BaseCommand
from tenants.models import Client, Domain


class Command(BaseCommand):
    help = "Create a new tenant"

    def add_arguments(self, parser):
        parser.add_argument("--name", required=True)
        parser.add_argument("--schema", required=True)
        parser.add_argument("--domain", required=True)

    def handle(self, *args, **options):

        tenant = Client.objects.create(
            name=options["name"],
            schema_name=options["schema"],
        )

        Domain.objects.create(
            domain=options["domain"],
            tenant=tenant,
            is_primary=True,
        )

        self.stdout.write(
            self.style.SUCCESS(
                f"Tenant {tenant.name} created successfully"
            )
        )