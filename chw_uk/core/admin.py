from datetime import timedelta

from django import forms
from django.contrib import admin, messages
from django.utils.html import format_html

from .models import (
    Announcement, ContactMessage, Event, GalleryImage, ProgramItem, SiteSetting,
    WorshipProgram, add_standard_order,
)


def thumb(f, height=56):
    if not f:
        return "—"
    return format_html(
        '<img src="{}" alt="" style="height:{}px;width:auto;border-radius:8px;border:1px solid #d9dfeb">', f.url, height
    )


class ProgramItemInline(admin.TabularInline):
    model = ProgramItem
    extra = 0
    fields = ("order", "name", "ministers", "duration")
    ordering = ("order", "id")


class WorshipProgramForm(forms.ModelForm):
    add_standard_order = forms.BooleanField(
        required=False,
        label="Fill in the standard order of service",
        help_text="Tick to pre-fill the usual items (Adoration, Choir, Sermon, Havdalah…). "
                  "Only applies if no items have been entered yet; edit names and durations afterwards.",
    )

    class Meta:
        model = WorshipProgram
        fields = "__all__"


@admin.register(WorshipProgram)
class WorshipProgramAdmin(admin.ModelAdmin):
    form = WorshipProgramForm
    inlines = [ProgramItemInline]
    list_display = ("service_date", "title", "is_published", "item_count", "has_file", "updated_at")
    list_filter = ("is_published",)
    date_hierarchy = "service_date"
    actions = ["publish", "unpublish", "duplicate_next_week"]
    fieldsets = (
        ("Service", {"fields": ("service_date", "title", "moderators", "meal_sponsor", "is_published")}),
        ("Programme", {"fields": ("add_standard_order", "program_file", "notes")}),
    )

    @admin.display(description="Items")
    def item_count(self, obj):
        return obj.items.count()

    @admin.display(boolean=True, description="File")
    def has_file(self, obj):
        return bool(obj.program_file)

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        program = form.instance
        if form.cleaned_data.get("add_standard_order") and not program.items.exists():
            add_standard_order(program)

    @admin.action(description="Publish selected programmes")
    def publish(self, request, queryset):
        self.message_user(request, f"{queryset.update(is_published=True)} published.")

    @admin.action(description="Unpublish (make draft)")
    def unpublish(self, request, queryset):
        self.message_user(request, f"{queryset.update(is_published=False)} set to draft.")

    @admin.action(description="Copy to the following Saturday (as a draft)")
    def duplicate_next_week(self, request, queryset):
        made = 0
        for prog in queryset:
            target = prog.service_date + timedelta(days=7)
            while WorshipProgram.objects.filter(service_date=target).exists():
                target += timedelta(days=7)
            new = WorshipProgram.objects.create(
                service_date=target, title=prog.title, moderators=prog.moderators,
                meal_sponsor="", notes="", is_published=False,
            )
            ProgramItem.objects.bulk_create(
                [ProgramItem(program=new, order=i.order, name=i.name, ministers=i.ministers, duration=i.duration)
                 for i in prog.items.all()]
            )
            made += 1
        self.message_user(
            request,
            f"{made} draft(s) created. Open each one, update the ministers/sponsor, then tick Published.",
            messages.SUCCESS,
        )


@admin.register(SiteSetting)
class SiteSettingAdmin(admin.ModelAdmin):
    fieldsets = (
        ("Images (design these in Canva)", {"fields": ("hero_image", "about_image")}),
        ("Service details", {"fields": ("service_time", "welcome_message")}),
        ("Contact & social", {"fields": ("contact_email", "contact_phone", "whatsapp_link", "facebook_url", "youtube_url")}),
    )

    def has_add_permission(self, request):
        return not SiteSetting.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False

    def changelist_view(self, request, extra_context=None):
        SiteSetting.load()
        return super().changelist_view(request, extra_context)


@admin.register(GalleryImage)
class GalleryImageAdmin(admin.ModelAdmin):
    list_display = ("preview", "caption", "order", "is_published")
    list_display_links = ("preview", "caption")
    list_editable = ("order", "is_published")
    list_filter = ("is_published",)

    @admin.display(description="Preview")
    def preview(self, obj):
        return thumb(obj.image)


@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ("title", "is_active", "created_at")
    list_filter = ("is_active",)


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ("title", "date", "time_text", "is_published")
    list_filter = ("is_published",)


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "phone", "created_at", "is_read")
    list_filter = ("is_read",)
    search_fields = ("name", "email", "message")
    readonly_fields = ("name", "email", "phone", "message", "created_at")
    actions = ["mark_read"]

    def has_add_permission(self, request):
        return False

    @admin.action(description="Mark as read")
    def mark_read(self, request, queryset):
        queryset.update(is_read=True)
