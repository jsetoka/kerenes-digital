# library/models.py
from django.db.models import Q
from wagtail.documents import get_document_model
from wagtail.models import Page
from django.db import models
from wagtail.admin.panels import FieldPanel


class DocumentLibraryPage(Page):
    intro = models.TextField(blank=True)

    content_panels = Page.content_panels + [
        FieldPanel("intro"),
    ]

    template = "library/document_library_page.html"

    def get_documents_queryset(self, request):
        Doc = get_document_model()
        qs = Doc.objects.all().order_by("-created_at")

        # Appliquer permissions
        user = request.user
        if not user.is_authenticated:
            return qs.none()

        # confidentiel => staff seulement
        if not user.is_staff:
            qs = qs.filter(Q(confidential=False) |
                           Q(confidential__isnull=True))

        # allowed_groups vide => accessible à tous users connectés
        # allowed_groups non vide => user doit être dans un groupe autorisé
        user_group_ids = user.groups.values_list("id", flat=True)
        qs = qs.filter(
            Q(allowed_groups__isnull=True) | Q(
                allowed_groups__in=user_group_ids)
        ).distinct()

        # Recherche
        q = request.GET.get("q", "").strip()
        if q:
            qs = qs.filter(
                Q(title__icontains=q) |
                Q(reference__icontains=q)
            )

        # Filtre type (si tu veux)
        doc_type = request.GET.get("type", "").strip()
        if doc_type:
            qs = qs.filter(doc_type=doc_type)

        return qs

    def serve(self, request, *args, **kwargs):
        # Option: obliger login pour voir la bibliothèque
        if not request.user.is_authenticated:
            from django.contrib.auth.views import redirect_to_login
            return redirect_to_login(request.get_full_path())
        return super().serve(request, *args, **kwargs)

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request)
        context["documents"] = self.get_documents_queryset(request)
        context["q"] = request.GET.get("q", "").strip()
        context["doc_type"] = request.GET.get("type", "").strip()
        return context
