from django.conf import settings
from django.contrib import admin
from django.urls import include, path, re_path
from django.views.static import serve

admin.site.site_header = "CHW UK · Admin"
admin.site.site_title = "CHW UK Admin"
admin.site.index_title = "Manage the website"

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("core.urls")),
]

# Uploaded programme files (images / PDFs). For heavy traffic, serve /media/ from nginx or object storage.
urlpatterns += [
    re_path(r"^media/(?P<path>.*)$", serve, {"document_root": settings.MEDIA_ROOT}),
]
