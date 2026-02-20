from django.contrib import admin
from .models import RdvRequest, DiagnosticSubmission


@admin.register(RdvRequest)
class RdvRequestAdmin(admin.ModelAdmin):
    list_display = ("created_at", "creneau", "canal",
                    "telephone", "email", "nom")
    list_filter = ("canal", "creneau", "created_at")
    search_fields = ("nom", "email", "telephone", "besoin")


@admin.register(DiagnosticSubmission)
class DiagnosticSubmissionAdmin(admin.ModelAdmin):
    list_display = ("created_at", "nom", "email",
                    "telephone", "niveau", "score")
    list_filter = ("niveau", "created_at")
    search_fields = ("nom", "email", "telephone", "entreprise")
