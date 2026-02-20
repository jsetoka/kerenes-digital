from django.contrib import admin
from .models import DiagnosticLead


@admin.register(DiagnosticLead)
class DiagnosticLeadAdmin(admin.ModelAdmin):
    list_display = ("created_at", "nom", "email",
                    "telephone", "niveau", "score_total")
    list_filter = ("niveau", "created_at")
    search_fields = ("nom", "email", "telephone")
