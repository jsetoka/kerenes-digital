# library/models.py
from collections import defaultdict
from django.db.models import Q
from wagtail.models import Page
from wagtail.admin.panels import FieldPanel
from wagtail.documents import get_document_model
from wagtail.models import Collection
from django.db import models


class DocumentLibraryPage(Page):
    intro = models.TextField(blank=True)

    content_panels = Page.content_panels + [FieldPanel("intro")]
    template = "library/document_library_page.html"

    def _filtered_docs(self, request):
        Doc = get_document_model()
        qs = Doc.objects.select_related("collection").all().order_by("title")

        user = request.user
        if not user.is_authenticated:
            return qs.none()

        # confidential => staff only
        if not user.is_staff:
            qs = qs.filter(Q(confidential=False) |
                           Q(confidential__isnull=True))

        # groups
        user_group_ids = user.groups.values_list("id", flat=True)
        qs = qs.filter(
            Q(allowed_groups__isnull=True) | Q(
                allowed_groups__in=user_group_ids)
        ).distinct()

        # search
        q = request.GET.get("q", "").strip()
        if q:
            qs = qs.filter(Q(title__icontains=q) | Q(reference__icontains=q))

        return qs

    def _build_collection_tree(self, docs_qs):
        """
        Structure:
        roots = [ {collection, children:[...], documents:[...]} ... ]
        Basé sur treebeard (Collection est un MP_Node).
        """

        # docs par collection
        docs_by_collection = defaultdict(list)
        for d in docs_qs:
            docs_by_collection[d.collection_id].append(d)

        def build_node(collection: Collection):
            children_nodes = []
            for child in collection.get_children():
                node = build_node(child)
                if node:
                    children_nodes.append(node)

            node_docs = docs_by_collection.get(collection.id, [])

            # ignorer les noeuds vides
            if not node_docs and not children_nodes:
                return None

            return {
                "collection": collection,
                "documents": node_docs,
                "children": children_nodes,
            }

        roots = []
        for root in Collection.get_root_nodes():
            node = build_node(root)
            if node:
                roots.append(node)

        return roots

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request)
        docs = self._filtered_docs(request)
        context["q"] = request.GET.get("q", "").strip()
        context["collection_tree"] = self._build_collection_tree(docs)
        context["documents_count"] = docs.count()
        return context
