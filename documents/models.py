from django.db import models
from wagtail.documents.models import AbstractDocument
from django.contrib.auth.models import Group


class CustomDocument(AbstractDocument):
    doc_type = models.CharField(
        max_length=50,
        choices=[
            ("procedure", "Procédure"),
            ("rapport", "Rapport"),
            ("support", "Support de cours"),
            ("marketing", "Marketing"),
        ],
        default="support",
    )
    reference = models.CharField(max_length=50, blank=True)
    confidential = models.BooleanField(default=False)
    allowed_groups = models.ManyToManyField(
        Group,
        blank=True,
        help_text="Groupes autorisés à télécharger (vide = accessible à tout utilisateur connecté).",
        related_name="allowed_documents",
    )

    # ✅ Déclare explicitement les champs affichés dans l’admin Wagtail
    # (puisque AbstractDocument.admin_form_fields n’existe pas dans ta version)
    admin_form_fields = (
        "title",
        "file",
        "collection",
        "tags",
        "doc_type",
        "reference",
        "confidential",
        "allowed_groups",
    )
