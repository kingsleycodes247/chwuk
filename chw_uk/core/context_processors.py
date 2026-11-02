from urllib.parse import quote_plus

from django.conf import settings
from django.utils import timezone

from .models import ContactMessage, SiteSetting, WorshipProgram, next_saturday


def site(request):
    s = settings.SYNAGOGUE
    q = quote_plus(s["map_query"])
    return {
        "syn": s,
        "site_settings": SiteSetting.load(),
        "full_address": ", ".join([s["venue"], *s["address_lines"]]),
        "map_embed_url": f"https://www.google.com/maps?q={q}&output=embed",
        "directions_url": f"https://www.google.com/maps/dir/?api=1&destination={q}",
    }


def admin_dashboard(request):
    """Status cards for the admin home page only (avoids extra queries on public pages)."""
    if request.path.rstrip("/") != "/admin":
        return {}
    upcoming = next_saturday(timezone.localdate())
    return {
        "dash_next_saturday": upcoming,
        "dash_next_program": WorshipProgram.objects.filter(service_date=upcoming).first(),
        "dash_unread_messages": ContactMessage.objects.filter(is_read=False).count(),
    }
