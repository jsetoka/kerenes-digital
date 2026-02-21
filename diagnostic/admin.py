from django.contrib import admin
from .models import DiagnosticLead, PlanActionRequest


@admin.register(DiagnosticLead)
class DiagnosticLeadAdmin(admin.ModelAdmin):
    list_display = ("created_at", "nom", "email",
                    "telephone", "niveau", "score_total")
    list_filter = ("niveau", "created_at")
    search_fields = ("nom", "email", "telephone")


@admin.register(PlanActionRequest)
class PlanActionRequestAdmin(admin.ModelAdmin):
    list_display = ("created_at", "lead", "objectif", "probleme_principal",
                    "outils_actuels", "statut")
    list_filter = ("statut", "created_at")
    search_fields = ("objectif", "probleme_principal")
