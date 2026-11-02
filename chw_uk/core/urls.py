from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("programmes/", views.program_archive, name="archive"),
    path("programmes/<int:pk>/", views.program_detail, name="program_detail"),
    path("contact/", views.contact, name="contact"),
]
