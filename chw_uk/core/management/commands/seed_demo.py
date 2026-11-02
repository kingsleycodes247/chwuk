from django.core.management.base import BaseCommand

from core.models import Announcement, Event, WorshipProgram, add_standard_order, next_saturday


class Command(BaseCommand):
    help = "Create a sample programme, announcement and event for local testing (placeholder data)."

    def handle(self, *args, **options):
        prog, created = WorshipProgram.objects.get_or_create(
            service_date=next_saturday(),
            defaults={"moderators": "Moderator names here", "meal_sponsor": "Sponsor name here", "is_published": True},
        )
        if created:
            add_standard_order(prog)
        Announcement.objects.get_or_create(
            title="Welcome", defaults={"body": "Sample announcement. Replace or delete this in the admin panel."}
        )
        self.stdout.write(self.style.SUCCESS(f"Sample data ready for {prog.service_date:%A %d %B %Y}."))
