from datetime import timedelta
from pathlib import Path

from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django.db import models
from django.utils import timezone


def next_saturday(today=None):
    """Today if it is Saturday, otherwise the coming Saturday."""
    today = today or timezone.localdate()
    return today + timedelta(days=(5 - today.weekday()) % 7)


def validate_saturday(value):
    if value.weekday() != 5:
        raise ValidationError("Shabbat worship is held on Saturdays. Please pick a Saturday.")


def validate_file_size(f):
    if f.size > 8 * 1024 * 1024:
        raise ValidationError("File is too large (maximum 8 MB).")


IMAGE_EXTS = ["jpg", "jpeg", "png", "webp"]
image_validators = [FileExtensionValidator(IMAGE_EXTS), validate_file_size]


class SiteSetting(models.Model):
    """One editable row: details that change without a code deploy."""

    hero_image = models.FileField(
        upload_to="site/", blank=True, validators=image_validators,
        help_text="Large landscape image behind the top of the home page (Canva: 2400 × 1200 px, JPG/PNG/WEBP, "
                  "under 8 MB). It is shown softened so the text stays readable.",
    )
    about_image = models.FileField(
        upload_to="site/", blank=True, validators=image_validators,
        help_text="Image beside the 'About us' text (Canva: 1200 × 1400 px portrait works best).",
    )

    service_time = models.CharField(
        max_length=80, blank=True,
        help_text="Shown on the site, e.g. '10:00 AM'. Leave blank to show only 'Every Saturday'.",
    )
    welcome_message = models.TextField(
        blank=True, help_text="Optional short welcome line shown under the main heading."
    )
    contact_email = models.EmailField(blank=True)
    contact_phone = models.CharField(max_length=40, blank=True)
    whatsapp_link = models.URLField(blank=True, help_text="Optional WhatsApp group / chat link.")
    facebook_url = models.URLField(blank=True)
    youtube_url = models.URLField(blank=True)

    class Meta:
        verbose_name = "Site settings"
        verbose_name_plural = "Site settings"

    def __str__(self):
        return "Site settings"

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class WorshipProgram(models.Model):
    service_date = models.DateField(
        unique=True, validators=[validate_saturday], default=next_saturday,
        help_text="The Saturday this programme is for.",
    )
    title = models.CharField(max_length=160, default="Shabbat Worship Programme")
    moderators = models.CharField(max_length=200, blank=True, help_text="e.g. Bro. A / Bro. B")
    meal_sponsor = models.CharField(max_length=200, blank=True, help_text="Shabbat meal sponsor, if any.")
    notes = models.TextField(blank=True, help_text="Optional note shown under the programme.")
    program_file = models.FileField(
        "Programme image or PDF", upload_to="programs/%Y/", blank=True,
        validators=[FileExtensionValidator(["jpg", "jpeg", "png", "webp", "pdf"]), validate_file_size],
        help_text="Optional: upload the finished programme (JPG, PNG, WEBP or PDF). "
                  "It is shown on the landing page in addition to any rows entered below.",
    )
    is_published = models.BooleanField(
        "Published", default=True, help_text="Untick to keep this as a draft hidden from visitors."
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-service_date"]
        verbose_name = "Weekly programme"
        verbose_name_plural = "Weekly programmes"

    def __str__(self):
        return f"{self.title} – {self.service_date:%d %b %Y}"

    @property
    def file_ext(self):
        return Path(self.program_file.name).suffix.lower() if self.program_file else ""

    @property
    def is_pdf(self):
        return self.file_ext == ".pdf"

    @property
    def is_image(self):
        return self.file_ext in {".jpg", ".jpeg", ".png", ".webp"}


class ProgramItem(models.Model):
    program = models.ForeignKey(WorshipProgram, on_delete=models.CASCADE, related_name="items")
    order = models.PositiveSmallIntegerField(default=0, help_text="Lower numbers appear first.")
    name = models.CharField("Programme item", max_length=160)
    ministers = models.CharField(max_length=200, blank=True)
    duration = models.CharField(max_length=40, blank=True, help_text="e.g. 20 mins (leave blank for ***)")

    class Meta:
        ordering = ["order", "id"]
        verbose_name = "Programme item"
        verbose_name_plural = "Programme items"

    def __str__(self):
        return self.name


STANDARD_ORDER = [
    ("Sabbath School Moderator", "", ""),
    ("Siddur Interpretation", "", ""),
    ("Adoration", "", "20 mins"),
    ("Blessing of the Shabbat meal", "Elders", "5 mins"),
    ("Choir rendition", "Choristers", "15 mins"),
    ("Prayer after the Shabbat meal", "Elders", "5 mins"),
    ("Blessing of the Shabbat meal sponsor", "Resident Minister / Appointee", "5 mins"),
    ("Our Creed", "", ""),
    ("D.O.O.F.", "", "30 mins"),
    ("Sermon", "Resident Minister / Appointee", "45 mins"),
    ("Offerings", "", "40 mins"),
    ("Announcements", "Secretary department", "10 mins"),
    ("Havdalah", "", "25 mins"),
]


def add_standard_order(program):
    ProgramItem.objects.bulk_create(
        [
            ProgramItem(program=program, order=i * 10, name=n, ministers=m, duration=d)
            for i, (n, m, d) in enumerate(STANDARD_ORDER, start=1)
        ]
    )


class Announcement(models.Model):
    title = models.CharField(max_length=160)
    body = models.TextField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title


class Event(models.Model):
    title = models.CharField(max_length=160)
    date = models.DateField()
    time_text = models.CharField("Time", max_length=60, blank=True)
    location = models.CharField(max_length=200, blank=True, help_text="Leave blank for the Selby Centre.")
    description = models.TextField(blank=True)
    is_published = models.BooleanField(default=True)

    class Meta:
        ordering = ["date"]

    def __str__(self):
        return f"{self.title} ({self.date:%d %b %Y})"


class GalleryImage(models.Model):
    image = models.FileField(
        upload_to="gallery/", validators=image_validators,
        help_text="Canva: 1200 × 800 px landscape, JPG/PNG/WEBP, under 8 MB.",
    )
    caption = models.CharField(max_length=160, blank=True)
    order = models.PositiveSmallIntegerField(default=0, help_text="Lower numbers appear first.")
    is_published = models.BooleanField(default=True)

    class Meta:
        ordering = ["order", "-id"]
        verbose_name = "Gallery image"
        verbose_name_plural = "Gallery images"

    def __str__(self):
        return self.caption or f"Image {self.pk}"


class ContactMessage(models.Model):
    name = models.CharField(max_length=120)
    email = models.EmailField()
    phone = models.CharField(max_length=40, blank=True)
    message = models.TextField(max_length=3000)
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} – {self.created_at:%d %b %Y}"
