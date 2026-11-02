from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from .forms import ContactForm
from .models import Announcement, Event, GalleryImage, WorshipProgram, next_saturday


def home(request):
    today = timezone.localdate()
    published = WorshipProgram.objects.filter(is_published=True).prefetch_related("items")
    program = published.filter(service_date__gte=today).order_by("service_date").first()
    program_is_upcoming = program is not None
    if program is None:
        program = published.order_by("-service_date").first()

    ctx = {
        "next_shabbat": next_saturday(today),
        "program": program,
        "program_is_upcoming": program_is_upcoming,
        "announcements": Announcement.objects.filter(is_active=True)[:4],
        "events": Event.objects.filter(is_published=True, date__gte=today)[:6],
        "gallery": GalleryImage.objects.filter(is_published=True)[:9],
        "form": ContactForm(),
    }
    return render(request, "core/home.html", ctx)


def program_archive(request):
    programs = WorshipProgram.objects.filter(is_published=True)
    return render(request, "core/archive.html", {"programs": programs})


def program_detail(request, pk):
    program = get_object_or_404(WorshipProgram.objects.prefetch_related("items"), pk=pk, is_published=True)
    return render(request, "core/program_detail.html", {"program": program})


@require_POST
def contact(request):
    form = ContactForm(request.POST)
    if form.is_valid():
        form.save()
        messages.success(request, "Thank you — your message has been received. We will be in touch.")
    else:
        messages.error(request, "Sorry, we couldn't send your message. Please check the form and try again.")
    return redirect("/#contact")
